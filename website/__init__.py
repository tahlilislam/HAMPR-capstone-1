# __init__.py makes the enclosing folder, a python package
# what that means is that you can import the folder and whatever is in folder will run automatically
import os
from os import path
from dotenv import load_dotenv
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, FlaskLoginClient
from flask_migrate import Migrate
from flask_debugtoolbar import DebugToolbarExtension
from celery import Celery, Task
from celery.schedules import crontab


db = SQLAlchemy()
migrate = Migrate()

DB_NAME = "hampr_db"


import redis

 # Create a Redis connection
redis_client = redis.StrictRedis(host='127.0.0.1', port=6379, db=0, decode_responses=True)

# Loading environment variables
load_dotenv()


def create_app():
    app = Flask(__name__)
    # encrypt cookies and session data related to the website, in production dont want to share secret key
    app.config['SECRET_KEY'] = 'I have a secret!'
    # Get DB_URI from environ variable (useful for production/testing) or,
    # if not set there, use development local db.
    app.config['SQLALCHEMY_DATABASE_URI'] = (
        os.environ.get('DATABASE_URL', f'postgresql:///{DB_NAME}'))

    # app.config['ACCESS_TOKEN'] = os.environ.get('ACCESS_TOKEN')
    app.config['PROJECT_ID'] = os.environ.get('PROJECT_ID')
    app.config['ENDPOINT_ID'] = os.environ.get('ENDPOINT_ID')

    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ECHO'] = False
    app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 465
    app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
    app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
  
    app.config['MAIL_USE_TLS'] = False
    app.config['MAIL_USE_SSL'] = True

    app.config['CACHE_TYPE'] = 'simple'  # You can use other cache types as well

    # # Configure caching
    # app.config['CACHE_TYPE'] = 'redis'
    # app.config['CACHE_REDIS_URL'] = 'redis://127.0.0.1:6379/0'  # Adjust as necessary
    
    
    app.test_client_class = FlaskLoginClient

    # app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', "it's a secret")
    toolbar = DebugToolbarExtension(app)
    with app.app_context():
        db.init_app(app)

        # TO RECREATE THE DATABASE USE THIS CODE 
        # from .models import User
        # db.create_all()

        migrate.init_app(app, db)

    ##### IF YOU ARE RUNNING THE MODEL FILE IN THE TERMINAL COMMENT THE FUNCTION BELOW TO PREVENT CIRCULAR IMPORTS AND ERRORS
        login_helper(app)
    #######

    app.config.from_mapping(
        CELERY=dict(
            broker_url='amqp://guest:guest@127.0.0.1:5672//',
            result_backend='rpc://guest:guest@127.0.0.1:5672//',
            task_ignore_result=True,
        ),
    )
    with app.app_context():
        celery_init_app(app)
        # mail.init_app(app)

    return app    


def login_helper(app):
    # db must be created first before importing models
    from .views import views
    from .auth import auth
    from .classify import classify

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')
    app.register_blueprint(classify, url_prefix='/')

    from .models import User

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    # check for primary key using get and finds the user by id
    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))


class CeleryConfig:
    CELERY_IMPORTS = ('website.tasks')
    CELERY_TASK_RESULT_EXPIRES = 30
    CELERY_ACCEPT_CONTENT = ['json', 'msgpack', 'yaml']
    CELERY_TASK_SERIALIZER = 'json'
    CELERY_RESULT_SERIALIZER = 'json'
    # CELERY_TIMEZONE = 'Asia/Seoul'
    CELERY_ENABLE_UTC = False
# this is a place for scheduler with celery beat.
# so, you can change 'task' part whatever you want.
    CELERYBEAT_SCHEDULE = {
        "time_scheduler": {
            "task": "website.tasks.send_mail",
            # "schedule": crontab()  ##runs every minute using for testing only
            'schedule': crontab(hour=0, minute=0),  # Runs daily at midnight
        },
        'mark-missed-goals-every-morning': {
            'task': 'website.tasks.mark_missed_goals',
            'schedule': crontab(hour=0, minute=0),  # Runs daily at midnight
            # "schedule": crontab() ##runs every minute using for testing only
        }
    }


def celery_init_app(app: Flask) -> Celery:
    class FlaskTask(Task):
        def __call__(self, *args: object, **kwargs: object) -> object:
            with app.app_context():
                with app.test_request_context():
                    return self.run(*args, **kwargs)

    celery_app = Celery(app.name, task_cls=FlaskTask)

    celery_app.config_from_object(CeleryConfig)
    celery_app.set_default()

    ####33

    # @celery_app.on_after_configure.connect
    # def setup_periodic_tasks(sender, **kwargs):
    #     @sender.task
    #     def fetch_and_send_reminders():
    #         from website.models import User
    #         from website.tasks import send_mail
    #         users = User.query.all()
    #         user_timezones = {user.id: user.get_timezone() for user in users}  # Assuming you have a method to get the user's timezone

    #         send_mail.delay(user_timezones)

    #     sender.add_periodic_task(crontab(hour=0, minute=0), fetch_and_send_reminders)


    #########

    app.extensions["celery"] = celery_app
    return celery_app


def create_db(app):
    if not path.exists('website/' + DB_NAME):
        db.create_all(app=app)
        # If the database doesn't exist, initialize Flask-Migrate to handle migrations
        migrate = Migrate(app, db)
        print('Created Database!')
