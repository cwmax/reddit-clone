import logging
import datetime

from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, login_user, logout_user
from werkzeug.urls import url_parse

from app.auth.forms import LoginForm, RegisterForm
from . import bp
from app.models import Users
from app import db


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = LoginForm()
    if form.validate_on_submit():
        flash(f'Login request for user {form.username.data}, '
              f'remember_me={form.remember_me.data}')
        user = Users.query.filter_by(user_name=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
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
        if password_1 != password_2:
            flash("Passwords don't match")
            return redirect(url_for('auth.register'))

        if Users.query.filter_by(user_name=user_name).first() is not None:
            flash('Please use a different username')
            return redirect(url_for('auth.register'))
        if Users.query.filter_by(email=email).first() is not None:
            flash('Please use a different email')
            return redirect(url_for('auth.register'))

        user = Users(user_name=user_name,
                     email=email,
                     created_at=datetime.datetime.utcnow())
        user.hash_password(password_1)
        db.session.add(user)
        try:
            db.session.commit()
            login_user(user, remember=True)
            return redirect(url_for('main.home'))
        except Exception as e:
            logging.error(f"Encountered exception {str(e)}")
            flash("Error encountered while creating the account")
            db.session.rollback()
    return render_template('auth/register.html', form=form)


@bp.get('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.home'))
