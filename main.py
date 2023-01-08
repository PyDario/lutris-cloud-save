import os
import sys
import yaml
import logging

game_name = os.environ.get("game_name")
if game_name == None:
    logging.error("game_name is not set. Check if the file was started from a lutris runtime")
    sys.exit(1)

# Get FTP data
ftp_hostname = os.environ.get("FTP_HOSTNAME")
if ftp_hostname == None:
    logging.error("FTP_HOSTNAME has not been set. Aborting")
    sys.exit(1)

ftp_user = os.environ.get("FTP_USER")
if ftp_user == None:
    logging.error("FTP_USER has not been set. Aborting")
    sys.exit(1)

ftp_password = os.environ.get("FTP_PASSWORD")
if ftp_password == None:
    logging.error("FTP_PASSWORD has not been set. Aborting")
    sys.exit(1)

placeholders = {
    "%LOCALAPPDATA%": os.environ.get("LOCALAPPDATA")
}

# Get save file location
with open("./lutris-save-file-locations.yml/lutris-save-file-locations.yml", "r") as stream:
    save_file_location = ''
    try: 
        save_file_location = yaml.safe_load(stream)[game_name]
    except yaml.YAMLError as exc:
        print(exc)

# Resolve placeholders
for placeholder in placeholders:
    save_file_location = save_file_location.replace(placeholder, placeholders[placeholder])

