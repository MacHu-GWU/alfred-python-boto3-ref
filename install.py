#!/bin/bash

from pathlib import Path

Path(Path.home(), "Documents", "data.json").unlink()
# print("hello world!")
# dir_here="${HOME}/.alfred-fts"
#
# echo "download copy search index data for alfred-python-boto3-ref ..."
# if ! [ -e "${dir_here}" ]; then
#     mkdir -p "${dir_here}"
# fi
#
# curl "https://api.github.com/repos/MacHu-GWU/alfred-python-boto3-ref/releases?per_page=1" | jq |

# python -c "$(curl -fsSL https://raw.githubusercontent.com/MacHu-GWU/alfred-python-boto3-ref/main/install.py)"