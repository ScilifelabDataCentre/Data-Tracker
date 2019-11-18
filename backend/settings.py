#!/usr/bin/env python3
"""Read settings from settings.yaml"""

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
            fpath = os.path.join(yloc, "settings.yaml")
            if os.path.exists(fpath):
                path = fpath
                break

    with open(path, "r") as in_file:
        return yaml.load(in_file, Loader=yaml.FullLoader)
