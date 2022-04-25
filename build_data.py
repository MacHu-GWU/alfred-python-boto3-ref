# -*- coding: utf-8 -*-

import json
from typing import List

from diskcache import Cache
from pathlib_mate import Path

import requests
from bs4 import BeautifulSoup

# ------------------------------------------------------------------------------
dataset_name = "boto3"

dir_here = Path.dir_here(__file__)
dir_cache = Path(dir_here, ".cache")

dir_home = Path.home()
p_alfred_data = Path(dir_home, ".alfred-fts", f"{dataset_name}.json")
p_alfred_setting_data = Path(dir_home, ".alfred-fts", f"{dataset_name}-setting.json")

cache = Cache(dir_cache.abspath)
cache_expire = 24 * 3600


# ------------------------------------------------------------------------------


def get_html_with_cache(url: str) -> str:
    if url in cache:
        return cache.get(url)
    else:
        html = requests.get(url).text
        cache.set(url, html, expire=cache_expire)
        return html


alfred_data = list()


# for each AWS Service page, locate the client section
class ServiceHomepage:
    def __init__(self, name, url):
        self.name = name
        self.url = url


def get_all_service_homepage() -> List[ServiceHomepage]:
    """
    get all AWS Service boto3 api homepage
    """
    service_homepage_list = list()

    url_available_services = "https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/index.html"
    html = get_html_with_cache(url_available_services)
    soup = BeautifulSoup(html, "html.parser")
    div = soup.find("div", id="available-services")
    for a in div.find_all("a", class_="reference internal"):
        # make sure the link is a aws service link
        if "#" not in a.attrs["href"]:
            href_service_name = a.attrs["href"]
            name = a.text
            url = f"https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/{href_service_name}"
            service_homepage = ServiceHomepage(name=name, url=url)
            service_homepage_list.append(service_homepage)

    return service_homepage_list


service_homepage_list = get_all_service_homepage()
for service_homepage in service_homepage_list:
    # service_homepage = ServiceHomepage( # for debug only
    #     name="EC2",
    #     url="https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ec2.html"
    # )
    print(f"working on {service_homepage.url} ...")
    html = get_html_with_cache(service_homepage.url)
    soup = BeautifulSoup(html, "html.parser")

    h1 = soup.find("h1")
    a = h1.find("a")

    div = soup.find("div", id="client")
    for ul in div.find_all("ul", class_="simple"):
        for a in ul.find_all("a"):
            try:
                href = a.attrs["href"]
                title = a.attrs["title"]
                if href.split(".")[-1] == title.split(".")[-1]:
                    method_name = href.split(".")[-1]
                    url_api = f"{service_homepage.url}{href}"
                    doc = dict(
                        title=f"{service_homepage.name}.{method_name}",
                        url=url_api,
                        ngram_field=f"{service_homepage.name.lower()} {' '.join(method_name.lower().split('_'))}",
                    )
                    alfred_data.append(doc)
            except:
                pass

alfred_settings_data = {
    "columns": [
        {
            "name": "title",
            "type_is_store": True
        },
        {
            "name": "url",
            "type_is_store": True
        },
        {
            "name": "ngram_field",
            "ngram_minsize": 2,
            "ngram_maxsize": 10,
            "type_is_nporngram": True
        }
    ],
    "title_field": "{title}",
    "subtitle_field": "open {url}",
    "arg_field": "{url}",
    "autocomplete_field": "{ngram_field}",
}

p_alfred_data.write_text(json.dumps(alfred_data, indent=4))
p_alfred_setting_data.write_text(json.dumps(alfred_settings_data, indent=4))
