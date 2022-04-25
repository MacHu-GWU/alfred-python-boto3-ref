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
dir_here = Path.cwd().absolute()
dir_home = Path.home()
dir_alfred_fts = Path(dir_home, ".alfred-fts")
dir_alfred_fts.mkdir(parents=True, exist_ok=True)

path_data_zip = Path(dir_here, "python-boto3-data.zip")
path_alfred_fts_data = Path(dir_alfred_fts, "boto3.json")
path_alfred_fts_settings = Path(dir_alfred_fts, "boto3-setting.json")
path_alfred_fts_index = Path(dir_alfred_fts, "boto3-whoosh_index")

# Find latest release asset
res = urlopen("https://api.github.com/repos/MacHu-GWU/alfred-python-boto3-ref/releases?per_page=1")
response_data = json.loads(res.read().decode("utf-8"))
browser_download_url = response_data[0]["assets"][0]["browser_download_url"]

# Download latest release asset
with Path(dir_here, "python-boto3-data.zip").open("wb") as f:
    res = urlopen(browser_download_url)
    f.write(res.read())

# Unzip asset
with ZipFile(str(path_data_zip), "r") as z:
    z.extractall(str(dir_here))

# Copy data files to the correct location
path_alfred_fts_data.write_text(Path(dir_here, "boto3.json").read_text())
path_alfred_fts_settings.write_text(Path(dir_here, "boto3-setting.json").read_text())
shutil.rmtree(str(path_alfred_fts_index), ignore_errors=True)
