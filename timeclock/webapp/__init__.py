# -*- coding: utf-8 -*-
from flask import Flask
from flask.ext.login import LoginManager
from flask_bootstrap import Bootstrap

from logic.controller import UserController

def create_app():
    app = Flask(__name__)
    app.config.from_object('webapp.config')
    Bootstrap(app)

    return app

app = create_app()
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view =  "login"


@login_manager.user_loader
def load_user(userid):
    return UserController().get_user_by_id(userid)


from webapp import views
