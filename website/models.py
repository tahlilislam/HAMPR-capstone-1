# from the current package import
# from . import db
import pdb
from website import db
from datetime import datetime as dt, timezone, timedelta
from timezonefinder import TimezoneFinder
from zoneinfo import ZoneInfo
import tzdata

from flask_login import UserMixin

from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()

## AN APP INSTANCE CREATED TO HELP CREATE MODEL INSTANCES ON PYTHON SHELL; UNCOMMENT WHEN NEEDED
## NEED TO PUSH and POP app CONTEXT WHILE WORKING IN TERMINAL by typing ctx.push() and ctx.pop() when done
# from website import create_app
# app = create_app()
# ctx = app.app_context()
########################

# to ensure "modified_at" field in Journal model gets the current time when a new "Journal" instance is created
# and not only when a class is first loaded.
def get_current_utc_time():
    return dt.now(ZoneInfo('UTC'))

class User(db.Model, UserMixin):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), nullable=False, unique=True,)
    username = db.Column(db.String(150), nullable=False, unique=True,)
    password = db.Column(db.String(150), nullable=False)
    first_name = db.Column(db.String(150), nullable=False)
    last_name = db.Column(db.String(150), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    ethnicity = db.Column(db.String(150))
    profession = db.Column(db.String(150))
    education_level = db.Column(db.String(50))
    financial_status_range = db.Column(db.String(150))
    location_general = db.Column(db.String(150))
    created_at = db.Column(db.DateTime(timezone=True),
                           default=dt.now(tz=ZoneInfo('UTC')))
    # Adding a new timezone column that saves session timezone data
    timezone = db.Column(db.String(50), default='UTC')


    my_journals = db.relationship('Journal', backref='author')

    def __repr__(self):
        return f"<User(user_id={self.id}, username={self.username}, first_name={self.first_name}, last_name={self.last_name}, created_at={self.created_at})>"

    @classmethod
    def signup(cls, username, email, password, first_name, last_name, age, ethnicity, profession, education_level, financial_status_range, location_general):
        """Sign up user.

        Hashes password and adds user to system.
        """

        hashed_pwd = bcrypt.generate_password_hash(password).decode('UTF-8')

        user = User(
            username=username,
            email=email,
            password=hashed_pwd,
            first_name=first_name,
            last_name=last_name,
            age=age,
            profession=profession,
            education_level=education_level,
            ethnicity=ethnicity,
            location_general=location_general,
            financial_status_range=financial_status_range,
            # timezone=timezone
        )

        db.session.add(user)
        return user

    @classmethod
    def authenticate(cls, username, password):
        """Find user with `username` and `password`.

        This is a class method (call it on the class, not an individual user.)
        It searches for a user whose password hash matches this password
        and, if it finds such a user, returns that user object.

        If can't find matching user (or if password is wrong), returns False.
        """

        user = cls.query.filter_by(username=username).first()

        if user:
            is_auth = bcrypt.check_password_hash(user.password, password)
            if is_auth:
                return user

        return False


class Journal(db.Model):
    __tablename__ = "journals"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50), nullable=False)
    text_entry = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey(
        'users.id', ondelete='cascade'))
    modified_at = db.Column(db.DateTime(timezone=True),
                            default=get_current_utc_time, nullable=False)
    # Store user's timezone info

    def local_modified_at(self, user_timezone):
        # cannot refer to self.modified_at since it is converted to a 'InstrumentedAttribute' object instead of datetime obj
         # Convert modified_at to datetime if needed
        if not isinstance(self.modified_at, dt):
            raise ValueError(
                "The 'modified_at' parameter must be a datetime object")

        # Convert modified_at which is stored in UTC to the specified user timezone object
        modified_at_local = self.modified_at.astimezone(
            ZoneInfo(user_timezone))

        # Get the current time in the user timezone
        current_time = dt.now(ZoneInfo(user_timezone))

        # a time delta object
        time_diff = current_time - modified_at_local

        # Calculate how long ago the modification occurred
        if time_diff.days == 0:
            # Less than a day ago
            if time_diff.seconds < 60:
                # Less than a minute
                display_time = "Just now"
            elif time_diff.seconds < 3600:
                # Less than an hour
                minutes = time_diff.seconds // 60
                display_time = f"{minutes} minute{'s' if minutes != 1 else ''} ago"
            else:
                # Less than a day
                hours = time_diff.seconds // 3600
                display_time = f"{hours} hour{'s' if hours != 1 else ''} ago"
        else:
            # More than a day ago
            days = time_diff.days
            display_time = f"{days} day{'s' if days != 1 else ''} ago"

        date_string = modified_at_local.strftime("%m-%d-%Y")

        # Return the local date and how long ago it was edited
        return f'Last Edited: {date_string}, {display_time}'


class Goal(db.Model):
    __tablename__ = "goals"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey(
        'users.id', ondelete='cascade'))
    goal_text = db.Column(db.String(150), nullable=False)
    # frequency = db.Column(db.Integer, nullable=False)
    # Array of integers representing days
    days_of_week = db.Column(db.ARRAY(db.Integer), nullable=False)
    # Time of day for reminders
    reminder_time = db.Column(db.DateTime(timezone=True), nullable=False)
    start_date = db.Column(db.DateTime(timezone=True), nullable=False)
    end_date = db.Column(db.DateTime(timezone=True), nullable=False)
    completed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime(timezone=True),
                           default=dt.now(tz=ZoneInfo('UTC')), nullable=False)

    # Store user's timezone info
    user = db.relationship("User", backref="goals")

    @classmethod
    def to_utc(self, local_datetime, user_timezone):
        local_time_zone = ZoneInfo(user_timezone)
        return local_datetime.astimezone(local_time_zone).astimezone(ZoneInfo('UTC'))

    def start_date_local(self, user_timezone):
        return self.start_date.astimezone(ZoneInfo(user_timezone))

    def end_date_local(self, user_timezone):
        return self.end_date.astimezone(ZoneInfo(user_timezone))

# #### add time as parameter and use default values
#### since _now will be changing when we are running tests
    def should_send_reminder(self, user_timezone, utc_now=None):
        # Get the current utc datetime as timezone aware
        if utc_now is None:
            utc_now = dt.utcnow().replace(tzinfo=ZoneInfo('UTC'))

        user_tzinfo = ZoneInfo(user_timezone)

        # Convert UTC now to the user's local time
        localized_now = utc_now.astimezone(user_tzinfo)

        # using python's datetime.datetime object methods
        current_day = localized_now.weekday()  # Monday is 0 and Sunday is 6
        current_time = localized_now.time().replace(microsecond=0)  # User's local time

        # Since reminder_time is already in UTC, we can compare it directly with utc_now
        # Or, convert reminder_time to the user's local timezone before comparison

        reminder_time_localized = self.reminder_time.astimezone(
            user_tzinfo)

        reminder_time_only = reminder_time_localized.time().replace(microsecond=0)

        # Calculate the end of the reminder window as a time object
        reminder_window_end = (dt.combine(
            dt.today(), reminder_time_only) + timedelta(minutes=5)).time()

        # Diagnostic prints
        print(
            f"Current Day: {current_day}, Reminder Day(s): {self.days_of_week}")
        print(
            f"Current Time: {current_time}, Reminder Time: {reminder_time_only}, Window End: {reminder_window_end}")
        print(
            f"Is current day in days_of_week? {'Yes' if current_day in self.days_of_week else 'No'}")
        print(
            f"Is current time within reminder window? {'Yes' if reminder_time_only <= current_time <= reminder_window_end else 'No'}")

        # Check if the current day is in the goal's days_of_week and if the current time is close to the reminder time
        # returns true or false
        return current_day in self.days_of_week and reminder_time_only <= current_time <= reminder_window_end

    def create_progress_entries(self):
            # Loop through each day between start_date and end_date
        # pdb.set_trace()
        for single_date in (self.start_date + timedelta(n) for n in range((self.end_date - self.start_date).days + 1)):
                # Check if the day's weekday is in days_of_week
            if single_date.weekday() in self.days_of_week:
                # Create a GoalProgress entry for this day
                # pdb.set_trace()
                # raise
                progress = GoalProgress(
                    goal_id=self.id, date=single_date, completed=False)
                db.session.add(progress)
        db.session.commit()


    def check_completion(self):
        goal_days = [(self.start_date + timedelta(days=x)) for x in range((self.end_date - self.start_date).days + 1)
                     if (self.start_date + timedelta(days=x)).weekday() in self.days_of_week]

        completed_days = GoalProgress.query.filter(
            GoalProgress.goal_id == self.id,
            GoalProgress.completed == True
        ).all()

        completed_dates = [progress.date for progress in completed_days]
        is_completed = all(day.date() in completed_dates for day in goal_days)

        if is_completed:
            self.completed = True
            db.session.commit()
    

class GoalProgress(db.Model):

    __tablename__ = 'goal_progresses'

    id = db.Column(db.Integer, primary_key=True)
    goal_id = db.Column(db.Integer, db.ForeignKey('goals.id'), nullable=False)
    date = db.Column(db.DateTime(timezone=True), nullable=False)
    completed = db.Column(db.Boolean, default=False, nullable=False)
    missed = db.Column(db.Boolean, default=False, nullable=False) 

    # relationships
    goal = db.relationship('Goal', backref=db.backref('progress', lazy=True))


class Email(db.Model):
    __tablename__ = 'emails'

    id = db.Column(db.Integer, primary_key=True)
    recipient = db.Column(db.String(100), nullable=False)
    subject = db.Column(db.String(255), nullable=False)
    email_body = db.Column(db.Text, nullable=False)
    sent_at = db.Column(db.DateTime(timezone=True), nullable=False)
    status = db.Column(db.String(20), default='pending')

    user_id = db.Column(db.Integer, db.ForeignKey(
        'users.id', ondelete='cascade'))
    user = db.relationship("User", backref="emails")
    # Store user's timezone info
    user_timezone = db.Column(db.String(50), nullable=False)

    @staticmethod
    def localize_timestamp(timestamp, user_timezone):
        """
        Convert a UTC timestamp to the user's timezone.
        """
        # Checking to see if there's a timezone info and if timestamp has a fixed offset from utc so we can use it for accurate datetime operations
        if timestamp.tzinfo is None or timestamp.tzinfo.utcoffset(timestamp) is None:
            # Assume timestamp is in UTC if no timezone info is present
            timestamp = timestamp.replace(tzinfo=ZoneInfo('UTC'))
        return timestamp.astimezone(ZoneInfo(user_timezone))

# n [1]: %run website/models.py

# In [2]: ctx.push()

# In [3]: user_timezone = 'America/New_York'

# In [4]: journal_entry = Journal.query.get(2 # Get the journal entry
#    ...: from the database
#    ...: )

# In [5]: date_string, time_diff = Journal.local_modified_at(journal_e
#    ...: ntry.modified_at, user_timezone)

# In [6]: time_diff
# Out[6]: '1 hour ago'

# In [7]: date_string
# Out[7]: '02-20-2024'

# timezonefinder_obj = TimezoneFinder()

#         for timezone in pytz.all_timezones:
#             local_datetime=dt.now(pytz.timezone(timezone))
#             print(f"{timezone} : {local_datetime.strftime('%Y:%m:%d %H:%M:%S %Z %z')}")


# message_id = db.Column(
#         db.Integer,
#         db.ForeignKey('messages.id', ondelete='cascade'),
#         unique=True
#     )


# In [1]: %run website/models.py
# In [13]: user_timezone = 'America/Los_Angeles'  # Example timezone
#     ...: utc_now = dt.utcnow().replace(tzinfo=ZoneInfo('UTC'))
#     ...: user_tzinfo = ZoneInfo(user_timezone)
#     ...: localized_now = utc_now.astimezone(user_tzinfo)

# In [14]: localized_reminder_time = localized_now + timedelta(minutes=2)
#     ...:

# In [15]: test_goal = Goal(
#     ...:     user_id=6,  # Assuming this user exists in your database
#     ...:     goal_text='Test Goal 22',
#     ...:     days_of_week=[localized_now.weekday()],  # Use the localized current day
#     ...:     reminder_time=localized_reminder_time,  # Use the localized future remind
#     ...: er time
#     ...:     start_date=localized_now,  # Use the localized current time as start
#     ...:     end_date=localized_now + timedelta(days=7)  # End date 7 days from start
#     ...: )

# In [16]: should_send = test_goal.should_send_reminder(user_timezone)
# Current Day: 6, Reminder Day(s): [6]
# Current Time: 23:22:30, Reminder Time: 23:23:51, Window End: 23:28:51
# Is current day in days_of_week? Yes
# Is current time within reminder window? No

# In [17]: should_send = test_goal.should_send_reminder(user_timezone)
# Current Day: 6, Reminder Day(s): [6]
# Current Time: 23:22:50, Reminder Time: 23:23:51, Window End: 23:28:51
# Is current day in days_of_week? Yes
# Is current time within reminder window? No

# In [18]: should_send = test_goal.should_send_reminder(user_timezone)
# Current Day: 6, Reminder Day(s): [6]
# Current Time: 23:23:13, Reminder Time: 23:23:51, Window End: 23:28:51
# Is current day in days_of_week? Yes
# Is current time within reminder window? No

# In [19]: should_send = test_goal.should_send_reminder(user_timezone)
# Current Day: 6, Reminder Day(s): [6]
# Current Time: 23:23:44, Reminder Time: 23:23:51, Window End: 23:28:51
# Is current day in days_of_week? Yes
# Is current time within reminder window? No

# In [20]: should_send = test_goal.should_send_reminder(user_timezone)
# Current Day: 6, Reminder Day(s): [6]
# Current Time: 23:23:53, Reminder Time: 23:23:51, Window End: 23:28:51
# Is current day in days_of_week? Yes
# Is current time within reminder window? Yes

# In [21]: should_send
# Out[21]: True
