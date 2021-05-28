#!/bin/sh

black backend
PYTHONPATH=backend pylint backend
flake8 backend
pydocstyle backend
