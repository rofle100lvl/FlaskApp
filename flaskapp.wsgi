#!/usr/bin/python
import sys
import logging
logging.basicConfig(stream=sys.stderr)
sys.path.insert(0,"/var/www/FlaskApp/FlaskApp")

# venv activating
activate_this = '/var/www/FlaskApp/FlaskApp/venv/bin/activate_this.py'

with open(activate_this) as file_:
    exec(file_.read(), dict(__file__=activate_this))

from app import app as application
application.secret_key = 'Add your secret key'
