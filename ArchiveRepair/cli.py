import logging
import os
import pickle
from datetime import datetime
from pathlib import Path

from palworld_save_tools.gvas import GvasFile
from palworld_save_tools.palsav import compress_gvas_to_sav, decompress_sav_to_gvas
from palworld_save_tools.paltypes import PALWORLD_CUSTOM_PROPERTIES, PALWORLD_TYPE_HINTS

DOCKER_ENV = os.environ.get("PAL_IN_DOCKER", "FALSE")
VERSION = os.environ.get("VERSION_NAME", "UNKNOWN")
EXPECTED_SAVE_GAME_TYPE = "/Script/Pal.PalWorldPlayerSaveGame"
CORRUPTED_SAVE_GAME_TYPE = "None.PalWorldPlayerSaveGame"
ROOT_PATH = "/data/save_games"
BACKUP_PATH = "/data/backups"
MISSING_JSON_FIELD = "PalStorageContainerId"
SLOT_ID_FILE_NAME = "slot_id.bak"


def load_slot_backups():
    _file_path = f"{BACKUP_PATH}/{SLOT_ID_FILE_NAME}"
    if not os.path.exists(_file_path):
        logging.info(f"{_file_path} is not exists.")
        return

    with open(_file_path, "rb") as f:
        return pickle.load(f)


def save_slot_backups(slot_info):
    if not slot_info:
        logging.warning(f"Backup users_slot_info with empty data. Returning.")
        return
    _file_path = f"{BACKUP_PATH}/{SLOT_ID_FILE_NAME}"
    logging.debug(f"backup users_slot_info:{slot_info} to {_file_path}")
    os.makedirs(os.path.dirname(_file_path), exist_ok=True)
    with open(_file_path, 'wb') as file:
        pickle.dump(slot_info, file)
    logging.info(f"Backup saved to {_file_path}")


def main():
    logging.basicConfig(level=logging.INFO if DOCKER_ENV == "TRUE" else logging.DEBUG)
    current_time = datetime.now()
    formatted_time = current_time.strftime("%Y-%m-%d %H:%M:%S")
    logging.info("------------------------------")
    logging.info(f"Now time:{formatted_time}")
    logging.info(f"PalWorldSaveRepair v{VERSION}")
    logging.info("https://github.com/AzureChubby/PalworldArchiveRepair")
    logging.info("------------------------------")

    backups_slot_info = load_slot_backups()
    if backups_slot_info is None or not isinstance(backups_slot_info, dict):
        logging.debug(f"backups_size:0 {type(dict)}")
    else:
        logging.debug(f"backups_size:{len(backups_slot_info)}")

    players_path = f"{ROOT_PATH}/Players"
    try:
        dir_entries = list(Path(players_path).glob("*.sav"))
    except Exception as e:
        logging.exception(f"Failed to read dir: {players_path}")
        exit(1)
    if not dir_entries:
        logging.warning(f"{players_path} folder is empty.")
        return
    _users_slot_info = {}
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
                _file_content_changed = False
                if gvas_file.header.save_game_class_name == CORRUPTED_SAVE_GAME_TYPE:
                    gvas_file.header.save_game_class_name = EXPECTED_SAVE_GAME_TYPE
                    _file_content_changed = True
                    logging.info(f"Try fix {file_name} {CORRUPTED_SAVE_GAME_TYPE} to {EXPECTED_SAVE_GAME_TYPE}")
                else:
                    logging.info(f"Skipping {file_name} as it save_game_class_name doesn't need fixing")

                if "SaveData" in gvas_file.properties:
                    _save_data_dict = gvas_file.properties["SaveData"]
                    _value = _save_data_dict.get("value")
                    if _value:
                        _slot_info = _value.get("PalStorageContainerId")
                        if _slot_info:
                            logging.info(f"{file_name} needn't fix PalStorageContainerId")
                            if not backups_slot_info or file_name not in backups_slot_info:
                                _users_slot_info[file_name] = _slot_info
                                logging.info(f"{file_name} will backup PalStorageContainerId")
                        else:
                            _current_user_slot_info = None
                            if backups_slot_info:
                                _current_user_slot_info = backups_slot_info.get(file_name)
                            if _current_user_slot_info:
                                _value["PalStorageContainerId"] = _current_user_slot_info
                                logging.info(f"Try fix {file_name} PalStorageContainerId")
                                _file_content_changed = True
                            else:
                                logging.warning(f"{file_name} not contain PalStorageContainerId "
                                                f"and no backups for use!!!")
                else:
                    logging.debug(f"SaveData not in gvas_file.properties. {gvas_file.properties.keys()}")

                if not _file_content_changed:
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
    if _users_slot_info and _users_slot_info != backups_slot_info:
        if backups_slot_info:
            _users_slot_info.update(backups_slot_info)
        save_slot_backups(_users_slot_info)

    logging.info("All save files have been repaired.")
