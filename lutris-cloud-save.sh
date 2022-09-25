#!/bin/bash

# Shared folder for your cloud saves
# CLOUDSAVE_FOLDER=
# Enter the Password to your Shared Nextcloud folder here
# CLOUDSEND_PASSWORD= 

# Resolve Placeholders
export LOCALAPPDATA=$WINEPREFIX/drive_c/users/$USER/AppData/Local

pip install pyyaml
python ./main.py