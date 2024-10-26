import os
from unittest import TestCase
from flask import json, session, Flask
from flask_login import FlaskLoginClient
from flask_sqlalchemy import SQLAlchemy
from website.models import User
from website import create_app

app = Flask(__name__)
db = SQLAlchemy()

with app.app_context():
    db.init_app(app)

TEST_DB_NAME = "hampr_db_test"

# Set the test database URL
os.environ['DATABASE_URL'] = f"postgresql:///{TEST_DB_NAME}"

# Create the test client


class AuthViewTestCase(TestCase):
    """Test views for authentication."""

    @classmethod
    def setUpClass(cls):
        """Setup for the test case class"""
        app.config['WTF_CSRF_ENABLED'] = False  # Disable CSRF protection for testing
        app.config['TESTING'] = True
        app.config['DEBUG'] = False
        # Initialize FlaskLoginClient
        app.test_client_class = FlaskLoginClient

        cls.client = app.test_client()

        # Create the test database
        with app.app_context():
            db.create_all()

    def setUp(self):
        """Create a test user and clean the database."""
        with app.app_context():
        #     db.drop_all()
        #     db.create_all()

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

    def tearDown(self):
        """Rollback any changes made to the database"""
        # db.session.rollback()

    @classmethod
    def tearDownClass(cls):
        """Drop all tables after all tests"""
        # db.drop_all()

    # Test for user signup
    def test_signup(self):
        """Test user signup"""
        with self.client as c:
            response = c.post('/sign-up', data={
                'username': 'newuser',
                'password': 'newpassword',
                'email': 'newuser@test.com',
                'first_name': 'New',
                'last_name': 'User',
                'age': '30',
                'ethnicity': 'None',
                'profession': 'None',
                'financial_status_range': 'None',
                'education_level': 'None',
                'location_general': 'None'
            })
            # Redirects after signup
            self.assertEqual(response.status_code, 302)
            self.assertIn(b'Hello, newuser!', response.data)

    # Test for duplicate username during signup
    def test_signup_duplicate_username(self):
        """Test signup with an existing username"""
        with self.client as c:
            response = c.post('/sign-up', data={
                'username': 'testuser',  # existing username
                'password': 'testpassword',
                'email': 'duplicate@test.com',
                'first_name': 'Duplicate',
                'last_name': 'User',
                'age': '30',
                'ethnicity': 'None',
                'profession': 'None',
                'financial_status_range': 'None',
                'education_level': 'None',
                'location_general': 'None'
            })
            self.assertEqual(response.status_code, 200)  # Shows form again
            self.assertIn(b'Username already taken', response.data)

    # Test for user login
    def test_login(self):
        """Test user login"""
        with self.client as c:
            response = c.post('/login', data={
                'username': 'testuser',
                'password': 'testpassword'
            })
            # Redirects after login
            self.assertEqual(response.status_code, 302)
            self.assertIn(b'Hello, testuser!', response.data)

    # Test for invalid login credentials
    def test_login_invalid_credentials(self):
        """Test login with invalid credentials"""
        with self.client as c:
            response = c.post('/login', data={
                'username': 'testuser',
                'password': 'wrongpassword'
            })
            self.assertEqual(response.status_code, 200)  # Shows form again
            self.assertIn(b'Invalid credentials.', response.data)

    # Test for user logout
    def test_logout(self):
        """Test user logout"""
        with self.client(user=self.test_user) as c:
                    response = c.get('/logout', follow_redirects=True)
                    self.assertEqual(response.status_code, 200)
                    self.assertIn(b'Please log in', response.data)

    # Test timezone update
    def test_get_timezone(self):
        """Test updating timezone"""
        with self.client as c:
            response = c.post('/get-timezone', data=json.dumps({'timezone': 'UTC'}), content_type='application/json')
            self.assertEqual(response.status_code, 200)
            self.assertEqual(session.get('timezone'), 'UTC')

    # Test timezone update without timezone
    def test_get_timezone_missing_timezone(self):
        """Test updating timezone with missing timezone"""
        with self.client as c:
            response = c.post('/get-timezone', data=json.dumps({}), content_type='application/json')
            self.assertEqual(response.status_code, 400)
            self.assertNotIn('timezone', session)
