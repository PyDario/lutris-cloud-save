#!/bin/bash

# FTP Data
export FTP_HOSTNAME=""
export FTP_USER=""
export FTP_PASSWORD=""
export FTP_SAVE_FOLDER=""

#Debug variables (Usually set by lutris upon game launch)
# export WINEPREFIX=
# export game_name=

# Resolve Placeholders
export LOCALAPPDATA=$WINEPREFIX/drive_c/users/$USER/AppData/Local

pip install pyyaml
python ./main.py