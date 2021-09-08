import datetime

from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, login_user, logout_user
from werkzeug.urls import url_parse

from app.auth.forms import LoginForm, RegisterForm
from . import bp
from app.models import Users
from app.main.submit_helpers import add_to_session_and_submit
from app.auth.validators.validate_users import (validate_new_username_and_email_unique,
                                                validate_passwords_match,
                                                validate_user_input_correct)


def create_and_submit_user(user_name: str, email: str, password_1: str) -> (Users, bool):
    user = Users(user_name=user_name,
                 email=email,
                 created_at=datetime.datetime.utcnow())
    user.hash_password(password_1)
    if add_to_session_and_submit(user, 'submit_user'):
        return user, True
    return user, False


def validate_new_user_data(user_name: str, email: str, password_1: str, password_2: str) -> bool:
    if not validate_passwords_match(password_1, password_2):
        return False
    if not validate_new_username_and_email_unique(user_name, email):
        return False
    return True


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(user_name=form.username.data).first()
        if not validate_user_input_correct(form):
            return redirect(url_for('auth.login'))
        login_user(user, remember=form.remember_me.data)

        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('main.home')
        return redirect(next_page)

    return render_template('auth/login.html', title='Sign In', form=form)


@bp.route('/register', methods=['GET', "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = RegisterForm()
    if form.validate_on_submit():
        password_1 = form.password.data
        password_2 = form.password_repeat.data
        user_name = form.username.data
        email = form.email.data
        if not validate_new_user_data(user_name, email, password_1, password_2):
            return redirect(url_for('auth.register'))
        user, ok = create_and_submit_user(user_name, email, password_1)
        if ok:
            login_user(user)
            return redirect(url_for('main.home'))

    return render_template('auth/register.html', form=form)


@bp.get('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.home'))
