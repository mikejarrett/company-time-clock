# -*- coding: utf-8 -*-
from flask.ext.wtf import Form

from wtforms import StringField, BooleanField
from wtforms.validators import DataRequired
from wtforms import TextField, PasswordField
from wtforms.validators import required


class LoginForm(Form):
    username = TextField('Username', validators=[required()])
    password = PasswordField('Password', validators=[required()])


class PunchInForm(Form):
    description = TextField('Description', validators=[required()])
    tags = TextField('Tags')
