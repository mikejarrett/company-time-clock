# -*- coding: utf-8 -*-
from flask.ext.wtf import Form

from wtforms import StringField, BooleanField
from wtforms.validators import DataRequired
from wtforms import TextField, PasswordField, DateTimeField
from wtforms.validators import required


class LoginForm(Form):
    username = TextField('Username', validators=[required()])
    password = PasswordField('Password', validators=[required()])


class PunchInForm(Form):
    description = TextField('Description', validators=[required()])
    tags = TextField('Tags')


class UserEditForm(Form):
    username = TextField('Username', validators=[required()])
    fullname = TextField('Full Name', validators=[required()])
    password = PasswordField('Password')
    password2 = PasswordField('Validate Password')


class PunchForm(Form):
    description = TextField('description', validators=[required()])
    start_time = DateTimeField('Start Time', validators=[required()])
    end_time = DateTimeField('End Time')
