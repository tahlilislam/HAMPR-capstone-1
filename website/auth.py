from flask import Blueprint, render_template, redirect, flash, url_for, jsonify
from .forms import UserAddForm, LoginForm
from .models import User
from flask_login import login_user, login_required, logout_user, current_user
from sqlalchemy.exc import IntegrityError
from flask import request, session
from . import db, cache
# from .tasks import send_mail
from website.timezone_store import user_timezones
from website import redis_client  # Adjust this import based on your project structure




auth = Blueprint('auth', __name__)


# @cache.cached(timeout=60, query_string=True)
@auth.route('/set-timezone', methods=['POST'])
def set_timezone():
        # from website.tasks import send_mail

        timezone = request.json.get('timezone')
        
        if timezone:
            session['timezone'] = timezone
            # cache.set("timezone", timezone)
            # print(cache.get('timezone'))  # Should print the timezone you just set

            #  # Call your Celery task and pass the timezone
            # send_mail.delay(timezone)

            # user_timezones[current_user.id] = timezone  # Update the in-memory dictionary

            # redis_client.set(f"user_timezone:{current_user.id}", timezone)  # Store in Redis
            # print(redis_client.get(f"user_timezone:{current_user.id}"))  # Debug: Verify stored value

            return 'Timezone updated successfully', 200
        else:
            session['timezone'] = 'UTC'
            return 'Timezone not provided', 400

@auth.route('/get-timezone', methods=['GET'])
def get_timezone():
    timezone = session.get('timezone', 'UTC')  
    # print(cache.get('timezone'))  # Should print the timezone you just set

    return jsonify({'timezone': timezone})


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
            db.session.rollback()  # Roll back the session to avoid InvalidRequestError during testing
            flash("Username already taken", 'danger')
            return render_template('sign_up.html', form=form)

        login_user(user, remember=True)

        return redirect(url_for('views.home'))
        # return f"{user.id}"

    else:
        # return "form not validated"
        return render_template('sign_up.html', form=form, user=current_user)


# @auth.route('/test', methods=["GET", "POST"])
# def test_route():
#     return "HELLO from test"



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
