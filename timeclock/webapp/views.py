# -*- coding: utf-8 -*-

from flask import render_template, redirect, request, url_for, abort
from flask.ext.login import (
    current_user, login_required, login_user, logout_user
)

from webapp import app
from webapp.forms import LoginForm

from logic import controller as logic
from logic.utils import time_difference_in_hours


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
            return redirect(request.args.get("next") or url_for("punches"))
        else:
            return redirect('/index')

    return render_template('login.html', title='Sign In', form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect('/')


@app.route('/punches')
@login_required
def punches():
    user = request.args.get('user')
    if user:
        user = logic.UserController().get_user_by_id(user)
    else:
        user = current_user
    punches = logic.PunchController().get_user_punches_by_range(user)

    title = '{} Punches'.format(user.fullname)
    return render_template('punches.html', title=title, punches=punches)


@app.route('/users')
@login_required
def users():
    users = logic.UserController().get_users()
    return render_template('users.html', title='Users', users=users)


@app.route('/user/<username>')
@login_required
def user_profile(username):
    user = logic.UserController().get_user_by_username(username)
    if not user:
        abort(404)

    return render_template('user.html', title=user.fullname, user=user)


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404
