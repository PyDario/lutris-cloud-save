import os
import sys
import yaml
import logging
import pysftp

is_load_mode = bool(os.environ.get("IS_LOAD_MODE"))
keep_os_seperate = bool(os.environ.get("KEEP_OS_SEPERATE"))

game_name = os.environ.get("game_name")
if game_name == None:
    logging.error("game_name is not set. Check if the file was started from a lutris runtime")
    sys.exit(1)

script_path = os.environ.get("SCRIPT_PATH")
if script_path == None:
    logging.error("script_path is not set. Check if the variable is correctly set")
    sys.exit(1)

print("Starting "+game_name+" with load_mode="+str(is_load_mode))
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
    "%LOCALAPPDATA%": os.environ.get("LOCALAPPDATA"),
    "$XDG_CONFIG_HOME": os.environ.get("XDG_CONFIG_HOME") or os.environ.get("HOME")+"/.config"
}

starter = "win" if os.environ.get("WINE") != None else "linux"

# Get save file location
with open(script_path+"/lutris-save-file-locations.yml/lutris-save-file-locations.yml", "r") as stream:
    save_file_location = ''
    try:
        loaded_yaml = yaml.safe_load(stream);
        save_file_location = loaded_yaml[game_name].setdefault(starter, "") if loaded_yaml.get(game_name) != None else ""
        if save_file_location == "":
            logging.error("No save file location found for this game. " + \
                        "Please contact the maintainer to add your game to the list")
            sys.exit(1)
        logging.info("save file location: " + save_file_location)
    except yaml.YAMLError as exc:
        logging.critical("lutris-save-file-locations.yml could not be opened")
        logging.critical("Stacktrace: "+exc)
        sys.exit(1)

# Resolve placeholders
for placeholder in placeholders:
    if placeholders[placeholder] == None:
        logging.error("Path:" + placeholder + " was not correctly set. Save folder could not be determined")
        sys.exit(1)
    save_file_location = save_file_location.replace(placeholder, placeholders[placeholder])

try:
    with pysftp.Connection(ftp_hostname, username=ftp_user, password=ftp_password) as sftp:
        if not sftp.exists(ftp_save_folder):
            logging.error("Remote save folder is invalid. Please check if it points to the right location")
            sys.exit(1)

        ftp_save_folder += "/" + (starter+"/" if keep_os_seperate else "") + game_name
        if is_load_mode:
            if sftp.exists(ftp_save_folder):
                sftp.get_d(ftp_save_folder, save_file_location, preserve_mtime=True)
            else:
                logging.info("No cloud save available")
        else:
            if not sftp.exists(ftp_save_folder):
                logging.info("No existing save file. Create new")
                sftp.mkdir(ftp_save_folder)

            sftp.put_r(save_file_location, ftp_save_folder, preserve_mtime=True)
except:
    logging.error("SFTP Connection could not be established. \
                Please check if you have a running internet connection and the FTP connection data is valid")
    sys.exit(1)