#!/bin/sh
#
# This script just tries to make sure that the tornado webserver starts and
# doesn't crash immediately.

FLASK_APP=app

! timeout 5 flask run
