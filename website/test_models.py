import os
import unittest
from flask import Flask
from flask_login import current_user
from website import db, login_helper
from website.models import User, Journal, Goal, GoalProgress
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo


TEST_DB_NAME = "hampr_db_test"

# create a new app variable so that configuration from the create app() function used isn't also imported
# This will prevent overwriting actual database
app = Flask(__name__)


class ModelsTestCase(unittest.TestCase):

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

    def test_user_model(self):
        """Test the User model."""

        with self.app.app_context():
            db.drop_all()
            db.create_all()

            user = User.signup(
                username="testuser",
                email="test@test.com",
                password="testpassword",
                first_name="Test",
                last_name="User",
                age=25,
                ethnicity="Asian",
                profession="Engineer",
                education_level="Bachelor's",
                financial_status_range="Medium",
                location_general="12345"
            )
            db.session.commit()

            # Verify user attributes
            self.assertEqual(user.username, "testuser")
            self.assertTrue(user.password.startswith(
                "$2b$"))  # Check hashed password
            self.assertEqual(user.age, 25)
            self.assertEqual(user.timezone, "UTC")  # Default timezone

            # Authenticate user
            authenticated_user = User.authenticate("testuser", "testpassword")
            self.assertIsNotNone(authenticated_user)
            self.assertEqual(authenticated_user.id, user.id)

    def test_journal_model(self):
        """Test the Journal model."""
        with self.app.app_context():

            user = User.signup(
                username="testuser2",
                email="test2@test.com",
                password="testpassword",
                first_name="Test",
                last_name="User2",
                age=30,
                ethnicity="Hispanic",
                profession="Teacher",
                education_level="Master's",
                financial_status_range="Low",
                location_general="67890"
            )
            db.session.commit()

            journal = Journal(
                title="My First Journal",
                text_entry="This is a test journal entry.",
                user_id=user.id
            )
            db.session.add(journal)
            db.session.commit()

            # Verify journal attributes
            self.assertEqual(journal.title, "My First Journal")
            self.assertEqual(journal.text_entry,
                             "This is a test journal entry.")
            self.assertEqual(journal.author.id, user.id)

            # Test local_modified_at
            localized_time = journal.local_modified_at("America/New_York")
            self.assertIn("Last Edited:", localized_time)

    def test_goal_model(self):
        """Test the Goal model."""
        with self.app.app_context():

            user = User.signup(
                username="goaluser",
                email="goal@test.com",
                password="goalpassword",
                first_name="Goal",
                last_name="User",
                age=40,
                ethnicity="Black",
                profession="Manager",
                education_level="Doctorate",
                financial_status_range="High",
                location_general="11223"
            )
            db.session.commit()

            goal = Goal(
                user_id=user.id,
                goal_text="Test Goal",
                days_of_week=[0, 1, 2],  # Monday, Tuesday, Wednesday
                reminder_time=datetime.utcnow() + timedelta(hours=1),
                start_date=datetime.utcnow(),
                end_date=datetime.utcnow() + timedelta(days=7),
                completed=False
            )
            db.session.add(goal)
            db.session.commit()

            # Verify goal attributes
            self.assertEqual(goal.goal_text, "Test Goal")
            self.assertFalse(goal.completed)

            # Test should_send_reminder
            utc_now = datetime.utcnow()
            should_remind = goal.should_send_reminder(user.timezone, utc_now)
            self.assertTrue(isinstance(should_remind, bool))

            # Test create_progress_entries
            goal.create_progress_entries()
            progress_count = GoalProgress.query.filter_by(
                goal_id=goal.id).count()
            # Three progress entries for Mon, Tue, Wed
            self.assertEqual(progress_count, 3)

    def test_goal_progress_model(self):
        """Test the GoalProgress model."""
        with self.app.app_context():

            user = User.signup(
                username="progressuser",
                email="progress@test.com",
                password="progresspassword",
                first_name="Progress",
                last_name="User",
                age=35,
                ethnicity="White",
                profession="Analyst",
                education_level="Bachelor's",
                financial_status_range="Medium",
                location_general="33445"
            )
            db.session.commit()

            goal = Goal(
                user_id=user.id,
                goal_text="Test Progress Goal",
                days_of_week=[0, 1, 2],  # Monday, Tuesday, Wednesday
                reminder_time=datetime.utcnow() + timedelta(hours=1),
                start_date=datetime.utcnow(),
                end_date=datetime.utcnow() + timedelta(days=7),
                completed=False
            )
            db.session.add(goal)
            db.session.commit()

            progress = GoalProgress(
                goal_id=goal.id,
                date=datetime.utcnow(),
                completed=True
            )
            db.session.add(progress)
            db.session.commit()

            # Verify progress attributes
            self.assertTrue(progress.completed)
            self.assertEqual(progress.goal.id, goal.id)


if __name__ == "__main__":
    unittest.main()
