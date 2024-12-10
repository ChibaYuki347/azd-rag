#!/bin/bash

# Get environment variables from azd
eval $(azd env get-values | sed 's/^/export /')

# echo 'Creating Python virtual environment'
python3 -m venv .venv

# Activate .venv/bin/activate
source .venv/bin/activate

# Installing dependencies from "requirements.txt" into virtual environment
.venv/bin/python -m pip --quiet --disable-pip-version-check install -r requirements.txt

# Run the Python script
python3 ./scripts/initial_setup_aisearch.py