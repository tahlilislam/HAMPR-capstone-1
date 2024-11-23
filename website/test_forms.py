from website.forms import GoalForm
import os
import unittest
from flask import Flask
from flask_login import current_user
from website import db, login_helper
# from website.models import User, Journal, Goal, GoalProgress
from datetime import datetime, timedelta
# from zoneinfo import ZoneInfo


TEST_DB_NAME = "hampr_db_test"

# create a new app variable so that configuration from the create app() function used isn't also imported
# This will prevent overwriting actual database
app = Flask(__name__)


class TestGoalForm(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Set up the test client and create a test database."""
        app.config['TESTING'] = True
        # Disable CSRF protection for testing
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['SECRET_KEY'] = 'I have a secret!'

        cls.app = app  # Use the testing configuration
        cls.client = cls.app.test_client()

        with cls.app.app_context():
            app.config['SQLALCHEMY_DATABASE_URI'] = (
                os.environ.get('DATABASE_URL', f'postgresql:///{TEST_DB_NAME}'))
            login_helper(cls.app)
            db.init_app(cls.app)
            # db.drop_all()
            db.create_all()

    def setUp(self):
        """Create test client, add sample data."""

        # print("TESTTINGGNGNNG")

        with self.app.app_context():
            db.drop_all()
            db.create_all()

    def tearDown(self):
        """Rollback any changes made to the database"""
        with self.app.app_context():
            db.session.rollback()

    @classmethod
    def tearDownClass(cls):
        """Drop all tables after all tests"""
        with cls.app.app_context():
            db.drop_all()

    def test_valid_goal_form(self):
        """Test if the GoalForm validates with valid data."""
        with self.app.app_context():

            form = GoalForm(data={
                'goal_text': 'Test Goal',
                'days_of_week': [0, 1, 2],  # Monday, Tuesday, Wednesday
                'reminder_time': (datetime.utcnow() + timedelta(hours=1)).strftime('%H:%M'),
                'start_date': (datetime.utcnow() + timedelta(days=1)).strftime('%Y-%m-%d'),
                'end_date': (datetime.utcnow() + timedelta(days=15)).strftime('%Y-%m-%d'),
            })
            self.assertTrue(form.validate(), form.errors)

    # def test_missing_required_fields(self):
    #     """Test if the GoalForm detects missing required fields."""
    #     form = GoalForm(data={})
    #     self.assertFalse(form.validate())
    #     self.assertIn('goal_text', form.errors)
    #     self.assertIn('days_of_week', form.errors)
    #     self.assertIn('reminder_time', form.errors)
    #     self.assertIn('start_date', form.errors)

    # def test_invalid_date_range(self):
    #     """Test if the GoalForm catches an invalid date range."""
    #     form = GoalForm(data={
    #         'goal_text': 'Test Goal',
    #         'days_of_week': [0, 1, 2],  # Monday, Tuesday, Wednesday
    #         'reminder_time': (datetime.utcnow() + timedelta(hours=1)).strftime('%H:%M'),
    #         # Invalid: Start date in the past
    #         'start_date': (datetime.utcnow() - timedelta(days=1)).strftime('%Y-%m-%d'),
    #         'end_date': (datetime.utcnow() + timedelta(days=15)).strftime('%Y-%m-%d'),
    #     })
    #     self.assertFalse(form.validate())
    #     self.assertIn('start_date', form.errors)

    # def test_end_date_readonly(self):
    #     """Test if the GoalForm end_date field is set to readonly."""
    #     form = GoalForm()
    #     self.assertIn('readonly', form.end_date.render_kw)


if __name__ == '__main__':
    unittest.main()
