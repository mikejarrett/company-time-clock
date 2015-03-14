# -*- coding: utf-8 -*-
from flask import render_template, redirect
from flask.ext.login import login_user

from webapp import app
from webapp.forms import LoginForm

from logic.controller import UserController


@app.route('/')
@app.route('/index')
def index():
    user = {'nickname': 'Miguel'}
    return render_template('index.html', title='Welcome', user=user)


@app.route('/hello')
def hello():
    return 'Hello monk butts!'


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        import ipdb; ipdb.set_trace()
        controller = UserController()
        user, validated = controller.validate_username_and_password(
            form.username.data, form.password.data)

        if validated:
            login_user(user)
            return redirect('/hello')
        else:
            return redirect('/index')

    return render_template('login.html', title='Sign In', form=form)
