from celery import shared_task, Task
from flask_login import login_required, current_user
from website.models import User, Email, Goal, GoalProgress
from datetime import datetime, time, timedelta
from flask_mail import Message, Mail
from website import create_app
from flask import session
from zoneinfo import ZoneInfo
# from website.auth import cache
# from website.timezone_store import user_timezones

import os
import requests


app = create_app()


@shared_task(ignore_result=False)
def add_together(a: int, b: int) -> int:
    return a + b


@shared_task(ignore_result=False)
def what():
    return 'awesome! it works :)'


@shared_task(bind=True, ignore_result=False)
def mark_missed_goals(self):
    with app.app_context():
        print("RUNNING MARKED MISSED GOALS")

        # to prevent circular import erros we are importing it locally
        from website.models import db
        import pdb

        today = datetime.combine(datetime.utcnow(), time.min)
        # fetch the single active goal
        active_goal = Goal.query.filter(
            Goal.end_date >= today, Goal.completed == False).first()

        if active_goal:
            missed_days = GoalProgress.query.filter(
                GoalProgress.goal_id == active_goal.id,
                GoalProgress.date < today,
                GoalProgress.completed == False
            ).all()
            # pdb.set_trace()
            print(
                f"Processing {len(missed_days)} missed day entries for goal {active_goal.id}")
            for day in missed_days:
                print(f"Marking day {day.date} as missed")
                day.missed = True

            db.session.commit()

# @celery.task(base=RequestContextTask)
@shared_task(bind=True, ignore_result=False)
def send_mail(self):
    with app.app_context():

        # with app.test_request_context():

        from website.models import User, Email

        users = User.query.all()

        print(f"ARRAY LENGTH: {len(users)}")

        for user in users:
          

            ######## Using SAMPLE TIMEZONE to prevent ERRORS #################
            user_timezone = "America/Los_Angeles"
            ##################################

            print(f"User: {user.username}, Timezone: {user_timezone}")

            for goal in user.goals:
                if goal.should_send_reminder(user_timezone):
                    print(goal)
                    mail = Mail(app)
                    msg = Message()
                    msg = Message(subject=f'Reminder to complete your goal: {goal.goal_text}',
                                  sender='noreply@mailtrap.io', recipients=['dummieuserexperience@gmail.com'])
                    msg.body = f"Hey {user.first_name}, \n\nThis is a reminder to complete your goal: {goal.goal_text}.\n\nBest regards,\nYour App Team"
                    mail.send(msg)
                    print("RAN SENT MAIL")


        return "Message sent or waiting for reminder window!"
