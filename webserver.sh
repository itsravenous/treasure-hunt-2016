#!/bin/sh
# or you can copy+paste this into a shell

export FLASK_APP=webserver.py
export FLASK_DEBUG=0  # setting to 1 would allow arbitrary code execution
flask run --host=0.0.0.0
