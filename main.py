import os
import sys
import yaml
import logging
import pysftp

is_load_mode = True
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

ftp_save_folder = os.environ.get("FTP_SAVE_FOLDER")
if ftp_save_folder == None or ftp_save_folder == "":
    ftp_save_folder = "./"

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

with pysftp.Connection(ftp_hostname, username=ftp_user, password=ftp_password) as sftp:
    if not is_load_mode:
        sftp.put_r(save_file_location, ftp_save_folder+"/"+game_name, preserve_mtime=True)
    else:
        print (ftp_save_folder+"/"+game_name)
        sftp.get_d(ftp_save_folder+"/"+game_name, save_file_location, preserve_mtime=True)
