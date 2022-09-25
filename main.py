import yaml
import os

game_name = os.environ.get("game_name")
with open("./lutris-save-file-locations.yml/lutris-save-file-locations.yml", "r") as stream:
    save_file_location = ''
    try: 
        save_file_location = yaml.safe_load(stream)["Downwell"]
    except yaml.YAMLError as exc:
        print(exc)

print(save_file_location)