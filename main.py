import os
import sys
import yaml
import logging

game_name = os.environ.get("game_name")
if game_name == None:
    logging.error("game_name is not set. Check if the file was started from a lutris runtime")
    sys.exit(1)

cloudsave_folder = os.environ.get("CLOUDSAVE_FOLDER")
if cloudsave_folder == None:
    logging.error("CLOUDSAVE_FOLDER has not been set. Aborting")
    sys.exit(1)

placeholders = {
    "%LOCALAPPDATA%": os.environ.get("LOCALAPPDATA")
}

with open("./lutris-save-file-locations.yml/lutris-save-file-locations.yml", "r") as stream:
    save_file_location = ''
    try: 
        save_file_location = yaml.safe_load(stream)[game_name]
    except yaml.YAMLError as exc:
        print(exc)

# Resolve placeholders
for placeholder in placeholders:
    save_file_location = save_file_location.replace(placeholder, placeholders[placeholder])
