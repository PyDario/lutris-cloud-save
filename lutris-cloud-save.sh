#!/bin/bash

# Shared folder for your cloud saves
# export CLOUDSAVE_FOLDER=
# Enter the Password to your Shared Nextcloud folder here
# export CLOUDSEND_PASSWORD=

#Debug variables (Usually set by lutris upon game launch)
# export WINEPREFIX=
# export game_name=

# Resolve Placeholders
export LOCALAPPDATA=$WINEPREFIX/drive_c/users/$USER/AppData/Local

pip install pyyaml
python ./main.py