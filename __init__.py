from flask import Flask
from routes import api
from routes.database.queries import db
from routes.database.queries import login_manager
import logging
import os

"""
Main module where all the apps are initiated and the project configs are set
"""

def create_app():
    app = Flask(__name__, static_url_path='/static')

    app.config['DEBUG'] = True
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'

    app.secret_key = 'thisissecrett'

    api.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)

    return app


def setup_database(app):
    with app.app_context():
        db.create_all()

"""
If there's no database found in the directory, a new one will be created using the structure info
Commented lines are for saving logs into an external file
"""

if __name__ == '__main__':
    app = create_app()
    # logging.basicConfig(filename='logs.log', level=logging.DEBUG)
    # logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)
    if not os.path.isfile('sqlite:///database.db'):

        setup_database(app)

    app.run()

