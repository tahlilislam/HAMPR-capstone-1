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
# user_timezone = session.get('timezone', 'UTC')



# class RequestContextTask(Task):
#     """Base class for tasks that run inside a Flask request context."""
#     abstract = True

#     def __call__(self, *args, **kwargs):
#         with app.test_request_context():
#             return super(RequestContextTask, self).__call__(*args, **kwargs)


MICROSERVICE_URL = os.getenv('MICROSERVICE_URL', 'http://127.0.0.1:5000')


# @shared_task(ignore_result=False)
# def get_timezone():
#     with app.app_context():
#         user_timezone = session.get('timezone')
#         return user_timezone


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
        from website.timezone_store import user_timezones
        from website import redis_client  # Adjust this import based on your project structure


        # from website import cache

        users = User.query.all()

        print(f"ARRAY LENGTH: {len(users)}")

        for user in users:
            print(user)
            print(len(user.goals))
            # user_timezone = user_timezones.get(user.id, 'UTC')  # Get timezone for each user
            user_timezone = redis_client.get(f'timezone:{user.id}')
            if user_timezone:
                user_timezone = user_timezone.decode('utf-8')  # Decode bytes to string
            # else:
            #     user_timezone = 'UTC'  # Fallback to UTC if not set


            # # Call the API to get the timezone
            # # Replace with your actual API URL
            # response = requests.get('http://127.0.0.1:5000/get-timezone')
            # if response.status_code == 200:
            #     user_timezone = response.json().get('timezone', 'UTC')
            #     print(f'USER TIMEZONE:{user_timezone}')
            # # else:
            # #     user_timezone = 'UTC'  # Default if API call fails

            # # Get timezone from cache
            # # user_timezone = cache.get('timezone')

            # user_timezone = session.get('timezone', 'UTC')

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

        # for user in users:
        #     if user is current_user:
        #         for goal in user.goals:
        #             if goal.should_send_reminder(user_timezone):

        #                 mail = Mail(app)
        #                 msg = Message()
        #                 msg = Message(subject='Reminder to complete your goal:',
        #                               sender='noreply@mailtrap.io', recipients=['dummieuserexperience@gmail.com'])
        #                 msg.body = "Hey Paul, sending you this email from my Flask app, lmk if it works"
        #                 mail.send(msg)
        #                 print("RAN SENT MAIL")

        return "Message sent or waiting for reminder window!"
