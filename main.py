import yaml
import os

game_name = os.environ.get("game_name")
cloudsave_folder = os.environ.get("CLOUDSAVE_FOLDER")

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

os.system("./cloudsend.sh/cloudsend.sh -e '" + save_file_location + "' '" + cloudsave_folder + "'")