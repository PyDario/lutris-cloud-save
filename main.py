import os
import sys
import yaml
import logging
import pysftp
import argparse

if not (home_folder := os.environ.get("HOME")):
    logging.critical("$HOME is not set! Please ensure your environment is properly set up")
    sys.exit(1)

# Pass and evaluate arguments
parser = argparse.ArgumentParser(description="Backs up and downloads your Lutris save files using SFTP")
parser.add_argument(
    "-l", "--load",
    help="If this option is set, the save file will be fetched from remote"
)
parser.add_argument(
    "--keep_os_seperate",
    help="Keep save files of different operation systems in their respective folder"
)
parser.add_argument(
    "--config",
    default=home_folder+"/.config/lutris-cloud-savec",
    help="Alternative path for a config file. Default is $HOME/.config/lutris-cloud-savec"
)
parser.add_argument(
    "-ftph", "--hostname",
    help="FTP Hostname"
)
parser.add_argument(
    "-ftpu", "--user",
    help="FTP Username"
)
parser.add_argument(
    "-ftpp", "--password",
    help="FTP Password"
)
parser.add_argument(
    "-ftpdir", "--ftp-savefolder",
    help="Remote folder location for the save files"
)
args = parser.parse_args()

is_load_mode = bool(os.environ.get("IS_LOAD_MODE"))
keep_os_seperate = bool(os.environ.get("KEEP_OS_SEPERATE"))

if not (game_name := os.environ.get("game_name")):
    logging.error("game_name is not set. Check if the file was started from a lutris runtime")
    sys.exit(1)

if not (script_path := os.environ.get("SCRIPT_PATH")):
    logging.error("script_path is not set. Check if the variable is correctly set")
    sys.exit(1)

logging.info("Starting "+game_name+" with load_mode="+str(is_load_mode))
print("Starting "+game_name+" with load_mode="+str(is_load_mode))
# Get FTP data
if not (ftp_hostname := os.environ.get("FTP_HOSTNAME")):
    logging.error("FTP_HOSTNAME has not been set. Aborting")
    sys.exit(1)

if not (ftp_user := os.environ.get("FTP_USER")):
    logging.error("FTP_USER has not been set. Aborting")
    sys.exit(1)

if not (ftp_password := os.environ.get("FTP_PASSWORD")):
    logging.error("FTP_PASSWORD has not been set. Aborting")
    sys.exit(1)

ftp_save_folder = os.environ.get("FTP_SAVE_FOLDER")
if ftp_save_folder == None or ftp_save_folder == "":
    ftp_save_folder = "./"

placeholders = {
    "%LOCALAPPDATA%": os.environ.get("LOCALAPPDATA"),
    "$XDG_CONFIG_HOME": os.environ.get("XDG_CONFIG_HOME") or os.environ.get("HOME")+"/.config"
}

starter = "win" if bool(os.environ.get("WINEPREFIX")) else "linux"

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

if not os.path.exists(save_file_location):
    logging.warning("Save file location doesn't exist. This could be due to the fact, that no save file has been written yet")
    sys.exit(0)

# Up- or Download file
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
                sys.exit(0)
        else:
            if not sftp.exists(ftp_save_folder):
                logging.info("No existing save folder. Create new")
                sftp.mkdir(ftp_save_folder)

            sftp.put_r(save_file_location, ftp_save_folder, preserve_mtime=True)
except:
    logging.error("SFTP Connection could not be established. \
                Please check if you have a running internet connection and the FTP connection data is valid")
    sys.exit(1)