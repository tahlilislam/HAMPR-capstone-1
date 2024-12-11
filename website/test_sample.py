import os
# from unittest import TestCase
import unittest
from flask import json, session, Flask
from flask_login import FlaskLoginClient
from website.models import User
from website import create_app, db, login_helper

TEST_DB_NAME = "hampr_db_test"

# Set the test database URL
os.environ['DATABASE_URL'] = f"postgresql:///{TEST_DB_NAME}"

app = Flask(__name__)


with app.app_context():
    app.config['SQLALCHEMY_DATABASE_URI'] = (
        os.environ.get('DATABASE_URL', f'postgresql:///{TEST_DB_NAME}'))
    login_helper(app)
    db.init_app(app)
    db.drop_all()
    db.create_all()




class AuthViewTestCase(unittest.TestCase):
    """Test views for authentication."""

    # @classmethod
    # def setUpClass(cls):
       
    #     # Initialize FlaskLoginClient


    #     cls.client = app.test_client()

    #     # Create the test database
    #     with app.app_context():
    #         db.create_all()


    def setUp(self):
        """Create test client, add sample data."""
        # app.config['WTF_CSRF_ENABLED'] = False  # Disable CSRF protection for testing
        # app.config['TESTING'] = True
        # app.config['DEBUG'] = False

        print("TESTTINGGNGNNG")
        with app.app_context():
            app.testing = True
            app.config['WTF_CSRF_ENABLED'] = False  # Disable CSRF protection for testing
            app.config['SECRET_KEY'] = 'I have a secret!'



            # db.drop_all()
            # db.create_all()

            # self.test_user = User.signup(
            #     username="testuser",
            #     email="test@test.com",
            #     password="testpassword",
            #     first_name="Test",
            #     last_name="User",
            #     age=25,
            #     ethnicity="None",
            #     profession="None",
            #     financial_status_range="None",
            #     education_level="None",
            #     location_general="None"
            # )
            # self.test_user_id = self.test_user.id
            # db.session.commit()

            self.client = app.test_client()

    # def test_simple(self):
    #     self.assertEqual(True, True)

    def tearDown(self):
        """Rollback any changes made to the database"""
        # with app.app_context():

        #     db.session.rollback()
        #     db.drop_all()


    # Test for user signup
    def test_signngngndgn(self):
        """Test user signup"""
        with app.app_context():

            with self.client as c:
                response = c.get('/test')
                # Redirects after signup
                self.assertEqual(response.status_code, 200)
                self.assertIn(b'HELLO from test', response.data)

    #  Test for user signup
    def test_signup(self):
        """Test user signup"""
        with self.client as c:
            response = c.post('/sign-up', json={
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
            # Redirects after signup
            self.assertEqual(response.status_code, 200)
            self.assertIn(b"What's on your mind", response.data)


if __name__ == '__main__':
    unittest.main()