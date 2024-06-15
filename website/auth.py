from flask import Blueprint, render_template, redirect, flash, url_for
from .forms import UserAddForm, LoginForm
from .models import User
from flask_login import login_user, login_required, logout_user, current_user
from sqlalchemy.exc import IntegrityError
from flask import request, session
from . import db

auth = Blueprint('auth', __name__)


@auth.route('/get-timezone', methods=['POST'])
def get_timezone():
        timezone = request.json.get('timezone')
        if timezone:
            session['timezone'] = timezone
            return 'Timezone updated successfully', 200
        else:
            return 'Timezone not provided', 400



@auth.route('/sign-up', methods=["GET", "POST"])
def signup():
    """Handle user signup.

    Create new user and add to DB. Redirect to home page.

    If form not valid, present form.

    If the there already is a user with that username: flash message
    and re-present form.
    """

    form = UserAddForm()

    if form.validate_on_submit():
        try:
            user = User.signup(
                username=form.username.data,
                password=form.password.data,
                email=form.email.data,
                first_name=form.first_name.data,
                last_name=form.last_name.data,
                age=form.age.data,
                ethnicity=form.ethnicity.data,
                profession=form.profession.data,
                financial_status_range=form.financial_status_range.data,
                education_level=form.education_level.data,
                location_general=form.location_general.data
                # image_url=form.image_url.data or User.image_url.default.arg,
            )
            db.session.commit()

        except IntegrityError:
            flash("Username already taken", 'danger')
            return render_template('sign_up.html', form=form)

        login_user(user, remember=True)

        return redirect(url_for('views.home'))

    else:
        return render_template('sign_up.html', form=form, user=current_user)


@auth.route('/login', methods=["GET", "POST"])
def login():
    """Handle user login."""

    form = LoginForm()

    if form.validate_on_submit():
        user = User.authenticate(form.username.data,
                                 form.password.data)

        if user:
            login_user(user, remember=True)
            flash(f"Hello, {user.username}!", "success")
            return redirect(url_for('views.home'))

        flash("Invalid credentials.", 'danger')

    return render_template('login.html', form=form, user=current_user)


@auth.route('/logout')
@login_required
def logout():
    """Handle logout of user."""
    logout_user()
    return redirect(url_for('auth.login'))
