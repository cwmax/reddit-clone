from flask import flash

from app.models import Users
from app.auth.forms import LoginForm


def validate_passwords_match(password_1: str, password_2: str) -> bool:
    if password_1 != password_2:
        flash("Passwords don't match")
        return False
    return True


def validate_new_username_and_email_unique(user_name: str, email: str) -> bool:
    if Users.query.filter_by(user_name=user_name).first() is not None:
        flash('Please use a different username')
        return False
    if Users.query.filter_by(email=email).first() is not None:
        flash('Please use a different email')
        return False
    return True


def validate_user_input_correct(form: LoginForm) -> bool:
    user = Users.query.filter_by(user_name=form.username.data).first()
    if user is None or not user.check_password(form.password.data):
        flash('Invalid username or password')
        return False
    return True
