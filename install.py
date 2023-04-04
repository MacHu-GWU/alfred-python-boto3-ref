#!/bin/bash

"""
Warning! This installation script is like how those popular opensource project
automate the installation:

- `Oh-my-zsh <https://github.com/ohmyzsh/ohmyzsh/blob/master/oh-my-zsh.sh>`_
- `HomeBrew <https://github.com/Homebrew/install/blob/master/install.sh>`_
- `pyenv installer <https://github.com/pyenv/pyenv-installer/raw/master/bin/pyenv-installer>`_

If this installation script is hacked, it may harm your laptop.

Usage:

.. code-block:: bash

    python3 -c "$(curl -fsSL https://raw.githubusercontent.com/MacHu-GWU/alfred-python-boto3-ref/main/install.py)"
"""

import json
import shutil
from pathlib import Path
from urllib.request import urlopen
from zipfile import ZipFile

# Define variables
# don't use Path(__file__).absolute().parent, this script is executed by `python3 -c (curl ...)`
dir_here = Path.cwd().absolute()
dir_home = Path.home()
dir_alfred_fts = Path(dir_home, ".alfred-afwf", "afwf_fts_anything")
dir_alfred_fts.mkdir(parents=True, exist_ok=True)

data_zip_file = "python-boto3-data.zip"
path_data_zip = Path(dir_here, data_zip_file)
path_alfred_fts_data = Path(dir_alfred_fts, "boto3-data.json")
path_alfred_fts_settings = Path(dir_alfred_fts, "boto3-setting.json")
path_alfred_fts_index = Path(dir_alfred_fts, "boto3-whoosh_index")

release_url = "https://api.github.com/repos/MacHu-GWU/alfred-python-boto3-ref/releases?per_page=1"
print("Find the latest release asset ...")
res = urlopen(release_url)
response_data = json.loads(res.read().decode("utf-8"))
browser_download_url = response_data[0]["assets"][0]["browser_download_url"]
file = "/".join(browser_download_url.split("/")[-2:])
print(f"Found {file!r}!")

print(f"download {browser_download_url} to {dir_here} ...")
with Path(dir_here, data_zip_file).open("wb") as f:
    res = urlopen(browser_download_url)
    f.write(res.read())

print(f"extract {data_zip_file} ...")
with ZipFile(str(path_data_zip), "r") as z:
    z.extractall(str(dir_here))

print(f"Copy setting and data file to {dir_alfred_fts} ...")
path_alfred_fts_data.write_text(Path(dir_here, "boto3-data.json").read_text())
path_alfred_fts_settings.write_text(Path(dir_here, "boto3-setting.json").read_text())
shutil.rmtree(str(path_alfred_fts_index), ignore_errors=True)
