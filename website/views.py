from flask import Blueprint, render_template, url_for, redirect, flash, session, jsonify, request
from flask_login import login_required, current_user
from . import db
from .forms import JournalForm, GoalForm, GoalDaysForm
from .models import Journal, Goal, GoalProgress
from datetime import datetime, timedelta, time
from zoneinfo import ZoneInfo
from wtforms import BooleanField


views = Blueprint('views', __name__)


@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    # Get timezone from session, or fall back to the value stored in the database
    user_timezone = session.get('timezone', current_user.timezone)

    form = JournalForm()

    if form.validate_on_submit():
        title = form.title.data
        text_entry = form.text_entry.data
        user_id = current_user.id
        journal_entry = Journal(
            title=title, text_entry=text_entry, user_id=user_id)
        db.session.add(journal_entry)
        db.session.commit()
        flash('Journal entry created successfully', 'success')
        return redirect(url_for('views.home'))

    # Assume you store the user's timezone in session
    user_timezone = session.get('timezone', 'UTC')
    # print(f'TIMEZONE: {user_timezone}')
    # Retrieve journal entries for the user
    journals = Journal.query.filter_by(user_id=current_user.id).all()

    return render_template("home.html", user=current_user, form=form, journals=journals, user_timezone=user_timezone)


@views.route('/set-goal', methods=['GET', 'POST'])
@login_required
def set_goal():
    form = GoalForm()

    if form.validate_on_submit():

    # Check for an existing active goal
        print(f"Checking for active goals for user {current_user.id}")

        existing_goal = Goal.query.filter(
            Goal.user_id == current_user.id,
            Goal.completed == False,
            Goal.end_date > datetime.utcnow()
        ).first()

        if existing_goal:
            print("An active goal already exists")  # Debug: Check if this condition is hit
            flash('You already have an active goal.', 'error')
            return redirect(url_for('views.my_goals'))
        print(f"Existing Goal Found: {existing_goal}")

        if existing_goal is None:
            print("No existing active goal found.")
        else:
            print(f"Found an existing goal: {existing_goal.goal_text}")


    # Creating a new goal

        # Get timezone from session
        user_timezone = session.get('timezone')
        if not user_timezone:
            # Handle case where timezone is not available
            user_timezone = 'UTC'

        # using datetime.combine with minimal time component
        # Assuming form.start_date.data is a date object and form.reminder_time.data is a time object
        start_datetime_local = datetime.combine(
            form.start_date.data, form.reminder_time.data)
        reminder_datetime_local = datetime.combine(
            form.start_date.data, form.reminder_time.data)
        end_datetime_local = start_datetime_local + timedelta(days=14)

        # Convert the local datetime to a timezone-aware datetime in UTC
        start_datetime_utc = Goal.to_utc(start_datetime_local, user_timezone)
        reminder_datetime_utc = Goal.to_utc(
            reminder_datetime_local, user_timezone)
        end_datetime_utc = Goal.to_utc(end_datetime_local, user_timezone)

        # Converting the string number values to integers
        days_of_week_integers = [int(day) for day in form.days_of_week.data]

        # if field.data < datetime.date.today():
        #     raise ValidationError("The date cannot be in the past!")

        # Create a new Goal object
        new_goal = Goal(
            user_id=current_user.id,
            goal_text=form.goal_text.data,
            days_of_week=days_of_week_integers,
            reminder_time=reminder_datetime_utc,
            start_date=start_datetime_utc,
            end_date=end_datetime_utc
        )

        # Add the new goal to the database session and commit
        db.session.add(new_goal)
      
        db.session.commit()

        # Create GoalProgress entries
        new_goal.create_progress_entries()
        

        flash('Goal set successfully', 'success')
        return redirect(url_for('views.my_goals'))
    
    print("Form validation failed:", form.errors)

    return render_template("set_goals.html", user=current_user, form=form)


@views.route('/mygoals', methods=['GET', 'POST'])
@login_required
def my_goals():
    active_goal = Goal.query.filter(
        Goal.user_id == current_user.id,
        Goal.end_date >= datetime.utcnow(),
        Goal.completed == False
    ).first()

    # fetching existing goal progress entries from database
    goal_days = []
    progress_entries = {}  # Initializing to avoid unbound local error

    if active_goal:
        # list comprehension iterarting every day between start and end dates
        #  if the days is one of the user;s specified days to work on goal(using .weekday() method we we are creating an integer set for days of the week 0-6);
        # then that date is added to the goals_days list
        goal_days = [(active_goal.start_date + timedelta(days=x)) for x in range((active_goal.end_date - active_goal.start_date).days + 1)
                     if (active_goal.start_date + timedelta(days=x)).weekday() in active_goal.days_of_week]
        
        progress_entries_query = GoalProgress.query.filter_by(goal_id=active_goal.id).all()

        # Map each progress entry by its date into a progress object dictionary for easy access in the template
        progress_entries = {progress.date.strftime('%Y-%m-%d'): progress for progress in progress_entries_query}

    return render_template("my_goals.html", user=current_user, active_goal=active_goal, goal_days=goal_days, progress_entries=progress_entries)


@views.route('/update-goal-progress/<int:goal_id>/<string:date_str>', methods=['POST'])
@login_required
def update_goal_progress(goal_id, date_str):
    
    data = request.get_json()
    completed = data.get('completed', False)

    # Convert date_str to a datetime object and set min time to midnight to create a consistent datetime object with the database
    goal_date = datetime.combine(datetime.strptime(date_str, '%Y-%m-%d').date(), time.min)
    
    # check for user id with goal id first and can raise exception
    
    goal = Goal.query.filter_by(id=goal_id, user_id=current_user.id).first()

    if (Goal.query.filter(Goal.user_id==current_user.id).first()):
            
            goal_progress = GoalProgress.query.filter_by(goal_id=goal_id, date=goal_date).first()
            if not goal:
                return jsonify({'error': 'Goal not found or does not belong to the current user'}), 404

            # Query GoalProgress by goal_id and the datetime range for the whole day
            # using equality checkes to see if goal date is in range tille just before the next day
            goal_progress = GoalProgress.query.filter(
                GoalProgress.goal_id == goal_id,
                GoalProgress.date >= goal_date,
                GoalProgress.date < goal_date + timedelta(days=1)
            ).first()

            if goal_progress:
                goal_progress.completed = completed
                
                db.session.commit()
                return jsonify({'message': 'GoalProgress updated successfully'})
            else:
                return jsonify({'error': 'GoalProgress not found'}), 404



 