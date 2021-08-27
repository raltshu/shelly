from DataView.flaskApp.handlers.table_view import TableView
from flask import Flask

app = Flask(__name__)

TableView.register(app, route_base='/api/app')


if __name__ == "__main__":
    app.run()