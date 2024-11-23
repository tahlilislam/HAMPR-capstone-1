import os
import unittest
from flask import Flask
from flask_login import current_user

from website.models import User
from website import db, login_helper

TEST_DB_NAME = "hampr_db_test"

# create a new app variable so that configuration from the create app() function used isn't also imported
app = Flask(__name__)


class AuthViewTestCase(unittest.TestCase):
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


    def tearDown(self):
        """Rollback any changes made to the database"""
        with self.app.app_context():
            db.session.rollback()

    @classmethod
    def tearDownClass(cls):
        """Drop all tables after all tests"""
        with cls.app.app_context():
            db.drop_all()

    def test_signup(self):
        """Test user signup"""
        with self.client as c:
            # Since this is a wtf FORM make sure the values inputted are valid in your form. For example,
            # a "None" value might be appropriate for database. But your flask form doesn't have an option for "None".
            # Otherwise you might hit integrity error setup in the app that will redirect you.
            response = c.post('/sign-up', data={
                'username': 'newuser',
                'password': 'newpassword',
                'email': 'newuser@test.com',
                'first_name': 'New',
                'last_name': 'User',
                'age': '30',
                'ethnicity': 'asian',
                'profession': 'legal',
                'financial_status_range': 'low',
                'education_level': 'other',
                'location_general': '92222'
            }, follow_redirects=True)

            # Redirects after signup, follow redirects is set to True so status code is 200
            self.assertEqual(response.status_code, 200)
            self.assertIn(b"What's on your mind?", response.data)

    def test_signup_duplicate_username(self):
        """Test signup with an existing username"""
        # Use current_user provided by Flask-Login instead of user to avoid issues when user is not defined.
        with self.client as c:
            response = c.post('/sign-up', data={
                'username': 'testuser',  # existing username
                'password': 'testpassword',
                'email': 'duplicate@test.com',
                'first_name': 'Duplicate',
                'last_name': 'User',
                'age': '30',
                'ethnicity': 'asian',
                'profession': 'legal',
                'financial_status_range': 'high',
                'education_level': 'other',
                'location_general': '95555'
            })
            self.assertEqual(response.status_code, 200)  # Shows form again
            self.assertIn(b'Username already taken', response.data)

    def test_signup_form_validation(self):
        """Test signup form validation"""
        with self.client as c:
            response = c.post('/sign-up', data={
                'username': '',  # Missing username
                'password': 'short',  # Short password
                'email': 'invalid-email',  # Invalid email format
                'first_name': 'Test',
                'last_name': 'User',
                'age': '25',
                'ethnicity': 'None',
                'profession': 'None',
                'financial_status_range': 'None',
                'education_level': 'None',
                'location_general': 'None'
            })

            # Expecting a validation error or re-presentation of the form
            self.assertEqual(response.status_code, 200)

            self.assertIn(b'Invalid email address', response.data)

    def test_current_user(self):
        """Testing current_user for flask login and ensuring user is authenticated"""
        with self.client as c:
            # Log the user in
            c.post('/login', data={
                'username': 'testuser',
                'password': 'testpassword',
            })

        # Check the current user in a protected route
            response = c.get('/')  # Protected route
            # Ensure user is authenticated
            self.assertTrue(current_user.is_authenticated)
            # Ensure current user is correct
            self.assertEqual(current_user.username, 'testuser')

    def test_login(self):
        """Test user login"""
        with self.client as c:
            response = c.post('/login', data={
                'username': 'testuser',
                'password': 'testpassword'
            }, follow_redirects=True)
            # Redirects after login, since follows redirects is set to True, status code will just be 200 ok
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'Hello, testuser!', response.data)

    def test_login_invalid_credentials(self):
        """Test login with invalid credentials"""
        with self.client as c:
            response = c.post('/login', data={
                'username': 'testuser',
                'password': 'wrongpassword'
            })
            self.assertEqual(response.status_code, 200)  # Shows form again
            self.assertIn(b'Invalid credentials.', response.data)

    def test_logout(self):
        """Test user logout"""
        with self.client as c:
            response = c.get('/logout', follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'Log in to your HaMPR account', response.data)

    def test_set_timezone(self):
        with self.client as c:
            # Log the user in
            with c.session_transaction() as sess:
                # this key is used to determine id the user's session is fresh in flask login 
                # which means the user has recently authenticated with their initials
                sess['_fresh'] = True

            timezone_data = {'timezone': 'America/New_York'}
            response = c.post('/set-timezone', json=timezone_data)

            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.data.decode('utf-8'),
                             'Timezone updated successfully')

            with c.session_transaction() as sess:
                self.assertEqual(sess['timezone'], 'America/New_York')

    def test_get_timezone(self):
        with self.client as c:
            with c.session_transaction() as sess:
                sess['_fresh'] = True
                sess['timezone'] = 'Europe/London'

            response = c.get('/get-timezone')

            self.assertEqual(response.status_code, 200)
            self.assertIn(b'Europe/London', response.data)


if __name__ == '__main__':
    unittest.main()
