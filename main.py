import os
import sys
import yaml
import logging
import pysftp
import argparse

env_HOME = os.environ.get("HOME")
env_USER = os.environ.get("USER")
env_XDG_CONFIG_HOME = os.environ.get("XDG_CONFIG_HOME") or env_HOME+"/.config"
env_game_name = os.environ.get("game_name")
env_WINEPREFIX = os.environ.get("WINEPREFIX")

placeholders = {
    "%LOCALAPPDATA%": (env_WINEPREFIX or "") + "/drive_c/users/"+env_USER+"/AppData/Local",
}

if not env_HOME:
    logging.critical("$HOME is not set! Please ensure your environment is properly set up")
    sys.exit(1)
if not env_game_name:
    logging.error("game_name is not set. Check if the file was started from a lutris runtime")
    sys.exit(1)

# Pass and evaluate arguments
parser = argparse.ArgumentParser(description="Backs up and downloads your Lutris save files using SFTP")
parser.add_argument(
    "-l", "--load",
    action="store_true",
    help="If this option is set, the save file will be fetched from remote"
)
parser.add_argument(
    "--keep_os_seperate",
    action="store_true",
    help="Keep save files of different operation systems in their respective folder"
)
parser.add_argument(
    "--ftp-config",
    default=env_HOME+"/.config/lutris-cloud-savec",
    help="Alternatively to arguments, an ftp-config file can be provided. This file has a higher priority than the arguments"
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
    "-ftpdir", "--ftp-save-folder",
    help="Remote folder location for the save files"
)
parser.add_argument(
    "--dev",
    action="store_true",
    help="This program was started in a dev environment"
)
args = parser.parse_args()

is_load_mode = bool(os.environ.get("IS_LOAD_MODE"))
keep_os_seperate = bool(os.environ.get("KEEP_OS_SEPERATE"))

config_folder = ".config" if args.dev else env_XDG_CONFIG_HOME+"/lutris-cloud-save"

logging.info("Starting "+env_game_name+" with load_mode="+str(args.load))
print("Starting "+env_game_name+" with load_mode="+str(args.load))

# Get FTP data
if args.ftp_config and os.path.exists(args.ftp_config):
    with open(args.ftp_config, "r") as stream:
        try:
            loaded_yaml = yaml.safe_load(stream);
            args.hostname = loaded_yaml.ftp_hostname
            args.user = loaded_yaml.ftp_user
            args.password = loaded_yaml.ftp_password
            args.ftp_save_folder = loaded_yaml.ftp_save_folder
        except yaml.YAMLError as exc:
            print(exc)

if not args.ftp_hostname:
    logging.error("ftp-hostname has not been set. Aborting")
    sys.exit(1)

if not args.ftp_user:
    logging.error("ftp-user has not been set. Aborting")
    sys.exit(1)

if not args.ftp_password:
    logging.error("ftp-password has not been set. Aborting")
    sys.exit(1)

if not bool(args.ftp_save_folder):
    args.ftp_save_folder = "./"

starter = "win" if env_WINEPREFIX else "linux"

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
        if args.load:
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