from flask import Flask
from utils.db import DataBase

app = Flask(__name__)
data_base = DataBase()
if __name__ == '__main__':
    print(__name__)
    app.run(debug=True, host='0.0.0.0', port=80)

from app import views
