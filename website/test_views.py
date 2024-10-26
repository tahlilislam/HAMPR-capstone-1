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
app = Flask(__name__)

class ViewsTestCase(unittest.TestCase):
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

            self.test_user = User.signup(
                username="testuser",
                email="test@test.com",
                password="testpassword",
                first_name="Test",
                last_name="User",
                age=25,
                ethnicity="None",
                profession="None",
                financial_status_range="None",
                education_level="None",
                location_general="None"
            )
        
            self.test_user_id = self.test_user.id
            db.session.commit()

            self.client.post('/login', data={
                'username': 'testuser',
                'password': 'testpassword',
            })

    def tearDown(self):
        """Rollback any changes made to the database"""
        with self.app.app_context():
            db.session.rollback()

    @classmethod
    def tearDownClass(cls):
        """Drop all tables after all tests"""
        with cls.app.app_context():
            db.drop_all()


    def test_home(self):
        """Test home route, a GET request"""
        with self.client as c:
            response = c.get('/', follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            self.assertIn(b"What's on your mind?", response.data)

    def test_set_goal(self):
        """Test setting a new goal"""
        with self.client as c:
            response = c.post('/set-goal', data={
                'goal_text': 'Test Goal',
                'start_date': (datetime.utcnow() + timedelta(days=1)).strftime('%Y-%m-%d'),
                'reminder_time': (datetime.utcnow() + timedelta(hours=1)).strftime('%H:%M:%S'),
                'days_of_week': ['0', '1', '2']  # Monday, Tuesday, Wednesday
            }, follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'Test Goal', response.data)


    def test_set_goal_existing_active_goal(self):
        """Test setting a new goal when an active goal already exists"""
        with self.client as c:
            # Create an active goal
            with self.app.app_context():
                goal = Goal(
                    user_id=self.test_user_id,
                    goal_text='Active Goal',
                    days_of_week=[0, 1],
                    reminder_time=datetime.utcnow(),
                    start_date=datetime.utcnow(),
                    end_date=datetime.utcnow() + timedelta(days=7),
                    completed=False
                )
                db.session.add(goal)
                db.session.commit()

            # Attempt to create a new goal
            response = c.post('/set-goal', data={
                'goal_text': 'New Goal',
                'start_date': (datetime.utcnow() + timedelta(days=8)).strftime('%Y-%m-%d'),
                'reminder_time': (datetime.utcnow() + timedelta(hours=2)).strftime('%H:%M:%S'),
                'days_of_week': ['1', '2', '3']  # Tuesday, Wednesday, Thursday
            }, follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            # print(response.data.decode('utf-8'))




            # self.assertIn(b'Hello, test
            # user!', response.data)
            # self.assertIn('You already have an active goal', str(response.data))

            # Ensure the new goal was not created by checking the goal count
        with self.app.app_context():
            goal_count = Goal.query.filter_by(user_id=self.test_user_id).count()
            self.assertEqual(goal_count, 1)  # There should still only be one goal


            # self.assertIn(b'New Goal', response.data)
            # self.assertIn(b'Active Goal', response.data)


    # def test_my_goals(self):
    #     """Test my goals route"""
    #     with self.client as c:
    #         # Create a goal
    #         goal = Goal(
    #             user_id=self.test_user_id,
    #             goal_text='Test Goal',
    #             days_of_week=[0, 1],
    #             reminder_time=datetime.utcnow(),
    #             start_date=datetime.utcnow() - timedelta(days=1),
    #             end_date=datetime.utcnow() + timedelta(days=7)
    #         )
    #         db.session.add(goal)
    #         db.session.commit()
    #         # Create progress entry
    #         progress = GoalProgress(
    #             goal_id=goal.id,
    #             date=datetime.utcnow().date(),
    #             completed=True
    #         )
    #         db.session.add(progress)
    #         db.session.commit()
    #         response = c.get('/mygoals', follow_redirects=True)
    #         self.assertEqual(response.status_code, 200)
    #         self.assertIn(b'Test Goal', response.data)
    # def test_update_goal_progress(self):
    #     """Test updating goal progress"""
    #     with self.client as c:
    #         # Create a goal
    #         goal = Goal(
    #             user_id=self.test_user_id,
    #             goal_text='Test Goal',
    #             days_of_week=[0],
    #             reminder_time=datetime.utcnow(),
    #             start_date=datetime.utcnow() - timedelta(days=1),
    #             end_date=datetime.utcnow() + timedelta(days=7)
    #         )
    #         db.session.add(goal)
    #         db.session.commit()
    #         # Update progress
    #         date_str = (datetime.utcnow().date()).strftime('%Y-%m-%d')
    #         response = c.post(f'/update-goal-progress/{goal.id}/{date_str}', json={
    #             'completed': True
    #         })
    #         self.assertEqual(response.status_code, 200)
    #         self.assertIn(b'GoalProgress updated successfully', response.data)
    # def test_update_goal_progress_invalid_goal(self):
    #     """Test updating progress for a non-existent or unauthorized goal"""
    #     with self.client as c:
    #         # Attempt to update progress for a non-existent goal
    #         date_str = (datetime.utcnow().date()).strftime('%Y-%m-%d')
    #         response = c.post(f'/update-goal-progress/999999/{date_str}', json={
    #             'completed': True
    #         })
    #         self.assertEqual(response.status_code, 404)
    #         self.assertIn(b'Goal not found or does not belong to the current user', response.data)
if __name__ == '__main__':
    unittest.main()
