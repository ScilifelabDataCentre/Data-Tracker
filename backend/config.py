#!/usr/bin/env python3
"""
Settings manager for the data tracker.

Read settings from `./config.yaml`, `../config.yaml` or from the provided path.
"""

import logging
import os
import sys
import yaml


def read_config(path: str = ''):
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
            fpath = os.path.join(location, "config.yaml")
            if os.path.exists(fpath):
                path = fpath
                break

    with open(path, "r") as in_file:
        return yaml.load(in_file, Loader=yaml.FullLoader)


def init(app):
    """
    Read settings and add them to the app config.

    Args:
        app: the Flask app

    """
    config_file = ''
    arg = "--config_file"
    if arg in sys.argv:
        try:
            config_file = sys.argv[sys.argv.index(arg)+1]
        except IndexError:
            logging.error("No argument for --config_file")
            sys.exit(1)

    config = read_config(config_file)
    if config['dev_mode']['testing']:
        logging.getLogger().setLevel(logging.DEBUG)
        config['TESTING'] = True

    app.config.update(config)
    app.config['SECRET_KEY'] = config['flask']['secret']
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'