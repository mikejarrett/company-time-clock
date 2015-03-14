# -*- coding: utf-8 -*-
from flask import Flask
from flask.ext.login import LoginManager

from logic.controller import UserController

app = Flask(__name__)
app.config.from_object('webapp.config')

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view =  "signin"


@login_manager.user_loader
def load_user(userid):
    return UserController().get_user_by_id(userid)


from webapp import views
