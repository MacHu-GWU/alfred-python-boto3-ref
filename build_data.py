# -*- coding: utf-8 -*-

import re
import json
import typing as T
import dataclasses

from diskcache import Cache
from pathlib_mate import Path

try:
    from functools import cached_property
except:
    from cached_property import cached_property

import afwf
import requests
from bs4 import BeautifulSoup

# ------------------------------------------------------------------------------
dataset_name = "boto3"

dir_here = Path.dir_here(__file__)
dir_cache = Path(dir_here, ".cache")
path_spec_file_json = Path(dir_here, "spec-file.json")

dir_home = Path.home()
p_alfred_data = Path(dir_here, f"{dataset_name}-data.json")
p_alfred_setting = Path(dir_here, f"{dataset_name}-setting.json")

cache = Cache(dir_cache.abspath)
cache_expire = 24 * 3600
# ------------------------------------------------------------------------------


def get_html_with_cache(url: str) -> str:
    """
    Crawl the URL HTML content, store it to the disk cache.
    :param url: webpage URL
    :return: HTML
    """
    if url in cache:
        return cache.get(url)
    else:
        html = requests.get(url).text
        cache.set(url, html, expire=cache_expire)
        return html


@dataclasses.dataclass
class AWSService:
    """
    ServiceHomepage Dataclass
    :param name: it is the clickable text in the boto3 document homepage sidebar.
        For example, for Elastic Block Storage service, the url is
        https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ebs.html,
        the clickable text in the sidebar is "EBS".
    :param href_name: the last part of the document url.
        For example, for Elastic Block Storage service, the url is
        https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ebs.html,
        the last part is "ebs".
    :param doc_url: the boto3 document url
    :param service_id: the service id that can be used in boto3.client("${service_id}")
    """

    name: str = dataclasses.field()
    href_name: str = dataclasses.field()
    doc_url: str = dataclasses.field()
    service_id: str = dataclasses.field()

    @property
    def name_snake_case(self) -> str:
        return self.name.lower().replace("-", "_")

    @property
    def service_id_snake_case(self) -> str:
        return self.service_id.lower().replace("-", "_")

    @property
    def service_id_camel_case(self) -> str:
        return "".join(
            [word[0].upper() + word[1:] for word in self.name.lower().split("-")]
        )


def crawl_service_page(html: str) -> str:
    """
    Given an AWS Service boto3 API documentation webpage HTML,
    extract the string token that used to create boto3 client.
    For example, given EBS boto3 API doc at https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ebs.html
    it returns "ebs", so we can use boto3.client("ebs") to create ebs client.
    :param html:
    :return: service id
    """
    pattern = re.compile("client = boto3.client\('[\d\D]*'\)")
    soup = BeautifulSoup(html, "html.parser")
    div_client = soup.find("div", class_="highlight-default notranslate")
    service_id = None
    for line in div_client.text.split("\n"):
        res = re.findall(pattern, line)
        if len(res):
            service_id = res[0].split("'")[1]
    return service_id


def crawl_home_page(html: str):
    """
    get all AWS Service boto3 api homepage from the boto3 doc homepage,
    from its sidebar.
    """
    aws_service_list = list()
    soup = BeautifulSoup(html, "html.parser")
    ul = soup.find("ul", class_="current")
    for a in ul.find_all("a", class_="reference internal"):
        # make sure the link is an aws service link
        if "#" not in a.attrs["href"]:
            href_name = a.attrs["href"]
            name = a.text
            doc_url = f"https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/{href_name}"
            aws_service = AWSService(
                name=name,
                href_name=href_name,
                doc_url=doc_url,
                service_id="",
            )
            # print(aws_service)
            aws_service_list.append(aws_service)
    return aws_service_list


def get_all_aws_service() -> T.List[AWSService]:
    """
    get all AWS Service boto3 api homepage from the boto3 doc homepage,
    from its sidebar.
    """
    url_available_services = "https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/index.html"
    html = get_html_with_cache(url_available_services)
    aws_service_list = crawl_home_page(html)
    return aws_service_list


def step1_crawl_spec_file_data():
    # --------------------------------------------------------------------------
    # get all AWS Service boto3 api homepage from the boto3 doc homepage,
    # from its sidebar.
    # --------------------------------------------------------------------------
    print("get all AWS service ...")
    url_available_services = "https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/index.html"
    html = get_html_with_cache(url_available_services)
    aws_service_list = crawl_home_page(html)
    print(f"found {len(aws_service_list)} AWS Services that has boto3 API")

    # --------------------------------------------------------------------------
    # iterate through all service page, and extract service_id
    # --------------------------------------------------------------------------
    print("extract service_id ...")
    for aws_service in aws_service_list:
        print(f"working on {aws_service.doc_url} ...")
        html = get_html_with_cache(aws_service.doc_url)
        service__id = crawl_service_page(html)
        aws_service.service_id = service__id

    # --------------------------------------------------------------------------
    # dump service data
    # --------------------------------------------------------------------------
    print("dump service data ...")
    spec_file_data: T.List[T.Dict[str, str]] = [
        dataclasses.asdict(aws_service) for aws_service in aws_service_list
    ]
    path_spec_file_json.write_text(json.dumps(spec_file_data, indent=4))


def get_documents(aws_service: AWSService) -> T.List[T.Dict[str, T.Any]]:
    html = get_html_with_cache(aws_service.doc_url)
    soup = BeautifulSoup(html, "html.parser")

    docs = list()

    section = soup.find("section", id="client")
    if section is not None:
        for a in section.find_all("a", class_="reference internal"):
            try:
                href = a.attrs["href"]
                method_name = a.text.strip()
                api_url = f"https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/{href}"
                doc = dict(
                    title=f"client | {aws_service.service_id}.{method_name}",
                    url=api_url,
                    ngram1="client",
                    ngram2=aws_service.name.lower(),
                    ngram3=aws_service.service_id.lower(),
                    ngram4=method_name,
                    order=1,
                )
                # print(doc)
                docs.append(doc)
            except:
                pass

    section = soup.find("section", id="paginators")
    if section is not None:
        for a in section.find_all("a", class_="reference internal"):
            try:
                href = a.attrs["href"]
                method_name = a.text.strip()
                api_url = f"https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/{href}"
                doc = dict(
                    title=f"paginator | {aws_service.service_id}.{method_name}",
                    url=api_url,
                    ngram1="pagi",
                    ngram2=aws_service.name.lower(),
                    ngram3=aws_service.service_id.lower(),
                    ngram4=method_name,
                    order=2,
                )
                # print(doc)
                docs.append(doc)
            except:
                pass

    return docs


def step2_create_fts_data():
    spec_file_data = json.loads(path_spec_file_json.read_text())
    aws_service_list = [AWSService(**data) for data in spec_file_data]
    docs = list()
    for aws_service in aws_service_list:
        print(f"working on {aws_service.doc_url} ...")
        docs.extend(get_documents(aws_service))
    p_alfred_data.write_text(json.dumps(docs, indent=4))


def step3_create_fts_setting():
    alfred_settings_data = {
        "fields": [
            {"name": "title", "type_is_store": True},
            {"name": "url", "type_is_store": True},
            {
                "name": "ngram1",
                "type_is_ngram": True,
                "ngram_minsize": 2,
                "ngram_maxsize": 6,
            },
            {
                "name": "ngram2",
                "type_is_ngram": True,
                "ngram_minsize": 2,
                "ngram_maxsize": 10,
                "weight": 2.0,
            },
            {
                "name": "ngram3",
                "type_is_store": True,
                "type_is_ngram": True,
                "ngram_minsize": 2,
                "ngram_maxsize": 10,
                "weight": 2.0,
            },
            {
                "name": "ngram4",
                "type_is_store": True,
                "type_is_ngram": True,
                "ngram_minsize": 2,
                "ngram_maxsize": 10,
                "weight": 1.0,
            },
            {
                "name": "order",
                "type_is_store": True,
                "type_is_numeric": True,
                "is_sortable": True,
                "is_sort_ascending": True,
            },
        ],
        "title_field": "{title}",
        "subtitle_field": "open {url}",
        "arg_field": "{url}",
        "autocomplete_field": "{ngram3}.{ngram4}",
    }
    p_alfred_setting.write_text(json.dumps(alfred_settings_data, indent=4))


# step1_crawl_spec_file_data()
# step2_create_fts_data()
# step3_create_fts_setting()
