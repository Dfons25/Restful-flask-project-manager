from flask import Flask
from flask_restplus import Resource, fields, Namespace
from flask_login import login_user, login_required, logout_user, current_user
import routes.database.queries as bd

"""
Module responsible for handling the app
Will only recieve and send static files 
"""

app = Flask(__name__, static_folder='../static')
endpoint = Namespace('app', description='site related endpoints')


@endpoint.route('/')
class LandingPage(Resource):

    @staticmethod
    def get():
        return app.send_static_file('landing.html')


@endpoint.route('/board')
class IndexPage(Resource):

    @login_required
    def get(self):
        headers = {'Content-Type': 'text/html'}
        return app.send_static_file('board.html')


@endpoint.route('/user/logout/')
class LogoutUser(Resource):

    def get(self):
        return app.send_static_file('landing.html')


@endpoint.route('/user')
class UserUpdate(Resource):

    @login_required
    def get(self):
        return app.send_static_file('update.html')

"""
Page redirect in the case the user is not properly logged in
"""

@bd.login_manager.unauthorized_handler
def unauthorized():
    return app.send_static_file('landing.html')