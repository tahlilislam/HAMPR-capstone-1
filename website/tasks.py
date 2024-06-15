from celery import shared_task
from flask_login import login_required, current_user
from website.models import User, Email, Goal, GoalProgress
from datetime import datetime, time, timedelta
# from flask_mailman import Mail, EmailMessage
from flask_mail import Message, Mail
from website import create_app
from flask import session
from zoneinfo import ZoneInfo


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


@shared_task(bind=True, ignore_result=False)
def send_mail(self):

    with app.app_context():

        from website.models import User, Email

        # user = User.query.get(user_id)

        users = User.query.all()
        user_timezone = session.get('timezone')

        # for user in users:
        # if user:
        # Check if it's time to send a reminder based on the user's frequency
        # if user.reminder_frequency.should_send_reminder():
        # Retrieve the user's email address
        # email = "dummieuserexperience@gmail.com"
        # email = user.email
        # msg = EmailMessage()

        for user in users:
            if user is current_user:
                for goal in user.goals:
                    if goal.should_send_reminder(user_timezone):

                        mail = Mail(app)
                        msg = Message()
                        msg = Message(subject='Hello from the other side!',
                                      sender='noreply@mailtrap.io', recipients=['dummieuserexperience@gmail.com'])
                        msg.body = "Hey Paul, sending you this email from my Flask app, lmk if it works"
                        mail.send(msg)

        return "Message sent!"

        # # When creating an Email object
        # user_timezone = 'America/New_York'  # Example timezone
        # email = Email(
        #     recipient='example@example.com',
        #     subject='Test Email',
        #     email_body='This is a test email.',
        #     sent_at= datetime.utcnow(),  # Store timestamps in UTC
        #     user_id=user.id,  # Example user ID
        #     user_timezone=user_timezone
        # )

        #  id = db.Column(db.Integer, primary_key=True)
        #     recipient = db.Column(db.String(100), nullable=False)
        #     subject = db.Column(db.String(255), nullable=False)
        #     email_body = db.Column(db.Text, nullable=False)
        #     sent_at = db.Column(db.DateTime(timezone=True), nullable=False)
        #     status = db.Column(db.String(20), default='pending')

        #     user_id = db.Column(db.Integer, db.ForeignKey(
        #         'users.id', ondelete='cascade'))
        #     user = db.relationship("User", backref="emails")
        #     # Store user's timezone info
        #     user_timezone = db.Column(db.String(50), nullable=False)

        # Convert and display timestamp in the user's timezone
        # local_sent_at = Email.localize_timestamp(
        #     email.sent_at, email.user_timezone)
        # print(f"Sent at (User's Local Time): {local_sent_at}")

        # # Send the email
        # with current_app.app_context():
        #     mail = current_app.extensions['mail']
        #     mail.send(message)

        # return "USER not found"
