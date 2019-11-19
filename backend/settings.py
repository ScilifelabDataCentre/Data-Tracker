#!/usr/bin/env python3
"""
Settings manager for the data tracker.

Read settings from `./settings.yaml`, `../settings.yaml` or from the provided path.
"""

import sys
import os
import yaml


def read_settings(path:str =''):
    """
    Look for settings.yaml and parse the settings from there.

    The file is expected to be found in the current, parent or provided folder.

    Args:
        path (str): The yaml file to use

    Returns:
        dict: The loaded settings

    Raises:
        FileNotFoundError: No settings file found

    """

    file_locations = [os.getcwd(),
                      os.pardir]
    if not path:
        for location in file_locations:
            fpath = os.path.join(location, "settings.yaml")
            if os.path.exists(fpath):
                path = fpath
                break

    if path:
        with open(path, "r") as in_file:
            return yaml.load(in_file, Loader=yaml.FullLoader)


settings_file = ''
ARG = "--settings_file"
if ARG in sys.argv:
    try:
        settings_file = sys.argv[sys.argv.index(ARG)+1]
    except IndexError:
        logging.error("No argument for --settings_file")
        sys.exit(1)

SETTINGS = read_settings(settings_file)
