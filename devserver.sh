#!/bin/sh
source .venv/bin/activate
python -m flask --app run run -p $PORT --debug