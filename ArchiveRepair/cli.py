import os
import re
import logging
from datetime import datetime

from palworld_save_tools.palsav import compress_gvas_to_sav, decompress_sav_to_gvas
from palworld_save_tools.gvas import GvasFile
from palworld_save_tools.paltypes import PALWORLD_CUSTOM_PROPERTIES, PALWORLD_TYPE_HINTS

from pathlib import Path

MAGIC_BYTES = b"PlZ"

VERSION = os.environ.get("VERSION_NAME", "UNKNOWN")
COMMIT_DATE = os.environ.get("GIT_COMMIT_DATE", "UNKNOWN")
COMMIT_HASH = os.environ.get("GIT_SHA", "UNKNOWN")
EXPECTED_SAVE_GAME_TYPE = "/Script/Pal.PalWorldPlayerSaveGame"
CORRUPTED_SAVE_GAME_TYPE = "None.PalWorldPlayerSaveGame"


def main():
    logging.basicConfig(level=logging.DEBUG)
    current_time = datetime.now()
    formatted_time = current_time.strftime("%Y-%m-%d %H:%M:%S")
    logging.info("------------------------------")
    logging.info(f"Now time:{formatted_time}")
    logging.info(f"PalWorldSaveRepair v{VERSION} {COMMIT_DATE} {COMMIT_HASH}")
    logging.info("https://github.com/EngrZhou/PalworldArchiveRepair")
    logging.info("------------------------------")
    env_key = "PLAYERS_SAVE_PATH"
    path = os.environ.get(env_key)
    if path is None:
        logging.warning(f"{env_key} environment variable not found, Use default replace.")
        path = "/data/Players"
    else:
        logging.debug(f"Prepare list {path}")

    try:
        dir_entries = list(Path(path).glob("*.sav"))
    except Exception as e:
        logging.exception(f"Failed to read dir: {path}")
        exit(1)
    if not dir_entries:
        logging.warning(f"{path} folder is empty.")
        return
    for file_path in dir_entries:
        file_name = file_path.name
        # base_name = re.sub(r'\..*', '', file_name)
        logging.debug(f"Prepare check file: {file_name}")
        try:
            with open(file_path, "rb") as f:
                _data = f.read()
                raw_gvas, _ = decompress_sav_to_gvas(_data)
                logging.debug(f"Decompress sav to GVAS success.")
                custom_properties = {}
                custom_properties_keys = ["all"]
                if len(custom_properties_keys) > 0 and custom_properties_keys[0] == "all":
                    custom_properties = PALWORLD_CUSTOM_PROPERTIES
                else:
                    for prop in PALWORLD_CUSTOM_PROPERTIES:
                        if prop in custom_properties_keys:
                            custom_properties[prop] = PALWORLD_CUSTOM_PROPERTIES[prop]
                gvas_file = GvasFile.read(
                    raw_gvas, PALWORLD_TYPE_HINTS, custom_properties, allow_nan=True
                )
                if gvas_file.header.save_game_class_name == CORRUPTED_SAVE_GAME_TYPE:
                    gvas_file.header.save_game_class_name = EXPECTED_SAVE_GAME_TYPE
                    logging.info(f"Try fix {file_name} {CORRUPTED_SAVE_GAME_TYPE} to {EXPECTED_SAVE_GAME_TYPE}")
                else:
                    logging.info(f"Skipping {file_name} as it doesn't need fixing")
                    continue
                # Prepare write file
                if ("Pal.PalWorldSaveGame" in gvas_file.header.save_game_class_name
                        or "Pal.PalLocalWorldSaveGame" in gvas_file.header.save_game_class_name):
                    save_type = 0x32
                else:
                    save_type = 0x31
                sav_file = compress_gvas_to_sav(
                    gvas_file.write(PALWORLD_CUSTOM_PROPERTIES), save_type
                )
                with open(file_path, "wb") as wf:  # Open the file in write-binary mode
                    wf.write(sav_file)
                logging.info(f"Try fix {file_name} finished.")
        except Exception as e:
            logging.exception(f"Failed to read save file:{e}")
            continue
    logging.info("All save files have been repaired.")
