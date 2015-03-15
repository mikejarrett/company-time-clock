# -*- coding: utf-8 -*-

from flask import render_template, redirect
from flask.ext.login import current_user, login_required, login_user

from webapp import app
from webapp.forms import LoginForm

from logic import controller as logic


@app.route('/punches')
@login_required
def punches():
    punches = logic.PunchController().get_user_punches_by_range(
        current_user)
    return render_template('reports.html', title='Reports', punches=punches)


@app.route('/', methods=['GET', 'POST'])
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        controller = logic.UserController()
        user, validated = controller.validate_username_and_password(
            form.username.data, form.password.data)

        if validated:
            login_user(user, remember=True)
            return redirect('/punches')
        else:
            return redirect('/index')

    return render_template('login.html', title='Sign In', form=form)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect('/index')
