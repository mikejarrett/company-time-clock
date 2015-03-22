# -*- coding: utf-8 -*-

from flask import render_template, redirect, request, url_for, abort, jsonify
from flask.ext.login import (
    current_user, login_required, login_user, logout_user
)

from webapp import app
from webapp import forms

from logic import controller as logic
from logic.utils import time_difference_in_hours

USER_CONTROLLER = logic.UserController()
PUNCH_CONTROLLER = logic.PunchController(
    USER_CONTROLLER.session, USER_CONTROLLER
)


@app.route('/', methods=['GET', 'POST'])
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = forms.LoginForm()
    if form.validate_on_submit():
        user, validated = USER_CONTROLLER.validate_username_and_password(
            form.username.data, form.password.data)

        if validated:
            login_user(user, remember=True)
            return redirect(request.args.get("next") or url_for("punches"))
        else:
            return redirect('/index')

    context = {
        'title': 'Sign In',
        'form': form,
    }
    return render_template('login.html', **context)


@app.route("/logout")
def logout():
    logout_user()
    return redirect('/')


@app.route('/punches')
@login_required
def punches():
    user = request.args.get('user')
    if user:
        user = USER_CONTROLLER.get_user_by_id(user)
    else:
        user = current_user
    punches = PUNCH_CONTROLLER.get_user_punches_by_range(user)

    context = {
        'title':  '{} Punches'.format(user.fullname),
        'punches': punches,
        'current_punch': PUNCH_CONTROLLER.get_current_punch(current_user.id)
    }
    return render_template('punches.html', **context)


@app.route('/users')
@login_required
def users():
    users = USER_CONTROLLER.get_users()

    context = {
        'title': 'Users',
        'users': users,
        'current_punch': PUNCH_CONTROLLER.get_current_punch(current_user.id)
    }
    return render_template('users.html', **context)


@app.route('/user/<username>')
@login_required
def user_profile(username):
    user = USER_CONTROLLER.get_user_by_username(username)
    if not user:
        abort(404)

    context = {
        'title': user.fullname,
        'user': user,
        'current_punch': PUNCH_CONTROLLER.get_current_punch(current_user.id)
    }
    return render_template('user.html', **context)


@app.route('/punch-in', methods=['GET', 'POST'])
@app.route('/user/<username>/edit')
@login_required
def user_edit(username):
    # TODO
    user = USER_CONTROLLER.get_user_by_username(username)
    form = forms.UserEditForm(username=user.username, fullname=user.fullname)

    if form.validate_on_submit():
        pass

    context = {
        'title': 'Edit {}'.format(user.username),
        'user': current_user,
        'current_punch': PUNCH_CONTROLLER.get_current_punch(current_user.id),
        'form': form,
    }
    return render_template('user-edit.html', **context)


@app.route('/punch-in', methods=['GET', 'POST'])
@login_required
def punchin():
    form = forms.PunchInForm()

    if form.validate_on_submit():
        punch = PUNCH_CONTROLLER.punch_in(
            current_user.id, description=form.description.data,
            tags=form.tags.data.split(','), user=current_user
        )
        return redirect(url_for("punches"))

    context = {
        'title': 'Sign In',
        'form': form,
        'current_punch': PUNCH_CONTROLLER.get_current_punch(current_user.id)
    }
    return render_template('punchin.html', **context)


@app.route('/punch-out')
@login_required
def punch_out():
    punch = PUNCH_CONTROLLER.punch_out(current_user.id, current_user)
    return redirect('/punches')


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404
