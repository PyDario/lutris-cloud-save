#!/bin/bash

#Debug variables (Usually set by lutris upon game launch)
# export WINEPREFIX=
# export game_name=

# Resolve Placeholders
export LOCALAPPDATA=$WINEPREFIX/drive_c/users/$USER/AppData/Local

POSITIONAL_ARGS=()
set -a
while [[ $# -gt 0 ]]; do
    case $1 in
        -l|--load)
            IS_LOAD_MODE=TRUE
            shift
            ;;
        --config)
            . $2 # Parse the configs. Can still be overridden with arguments
            shift
            shift
            ;;
        -h|--hostname)
            FTP_HOSTNAME="$2"
            shift
            shift
            ;;
        -u|--user)
            FTP_USER="$2"
            shift
            shift
            ;;
        -p|--password)
            FTP_PASSWORD="$2"
            shift
            shift
            ;;
        -dir|--savefolder)
            FTP_SAVE_FOLDER="$2"
            shift
            shift
            ;;
        -*|--*)
            echo "Unknown option $1"
            exit 1
            ;;
        *)
            POSITIONAL_ARGS+=("$1")
            shift
            ;;
    esac
done
set +a

set -- "${POSITIONAL_ARGS[@]}"
if [[ -n $1 ]]; then
    echo "Last line of file specified as non-opt/last argument:"
    tail -1 "$1"
fi

# Install dependencies and start programm
pip install pyyaml
pip install pysftp
python ./main.py