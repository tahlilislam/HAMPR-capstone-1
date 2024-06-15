# __init__.py makes the enclosing folder, a python package
# what that means is that you can import the folder and whatever is in folder will run automatically
import os
from os import path
from flask import Flask, request, session
from flask_wtf.csrf import CSRFProtect
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_debugtoolbar import DebugToolbarExtension
from celery import Celery, Task
from celery.schedules import crontab
from flask_mail import Mail, Message
# from flask_mailman import Mail, EmailMessage

db = SQLAlchemy()
migrate = Migrate()
# mail = Mail()

DB_NAME = "hampr_db"


# def timezone_middleware(app):

#         @app.route('/get-timezone', methods=['POST'])
#         def update_timezone():
#                     timezone = request.json.get('timezone')
#                     if timezone:
#                         session['timezone'] = timezone
#                         return 'Timezone updated successfully', 200
#                     else:
#                         return 'Timezone not provided', 400

# timezone = request.json.get('timezone')
# if timezone:
#     session['timezone'] = timezone

# @csrf.protect
# @app.route('/get-timezone', methods=['POST'])
# def update_timezone():
#             timezone = request.json.get('timezone')
#             if timezone:
#                 session['timezone'] = timezone
#                 return 'Timezone updated successfully', 200
#             else:
#                 return 'Timezone not provided', 400


def create_app():
    app = Flask(__name__)
    # encrypt cookies and session data related to the website, in production dont want to share secret key
    app.config['SECRET_KEY'] = 'I have a secret!'
    # Get DB_URI from environ variable (useful for production/testing) or,
    # if not set there, use development local db.
    app.config['SQLALCHEMY_DATABASE_URI'] = (
        os.environ.get('DATABASE_URL', f'postgresql:///{DB_NAME}'))

    app.config['ACCESS_TOKEN'] = os.environ.get('ACCESS_TOKEN')
    app.config['PROJECT_ID'] = os.environ.get('PROJECT_ID')
    app.config['ENDPOINT_ID'] = os.environ.get('ENDPOINT_ID')

    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ECHO'] = False
    app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 465
    app.config['MAIL_USERNAME'] = 'dummieuserexperience@gmail.com'
    app.config['MAIL_PASSWORD'] = "nxfh rsnq wseo fhgh"
    app.config['MAIL_USE_TLS'] = False
    app.config['MAIL_USE_SSL'] = True

    # app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', "it's a secret")
    toolbar = DebugToolbarExtension(app)
    with app.app_context():
        db.init_app(app)
        migrate.init_app(app, db)
        # migrate = Migrate(app, db)

    # IF YOU ARE RUNNING THE MODEL FILE IN THE TERMINAL COMMENT THE FUNCTION BELOW TO PREVENT CIRCULAR IMPORTS AND ERRORS
        login_helper(app)
    ######

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
    from .text_classify import text_classify

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')
    app.register_blueprint(text_classify, url_prefix='/')

    from .models import User, Journal

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
            "schedule": crontab()  # set schedule time !
            # "schedule": 60.0  # set schedule time !
        },
        'mark-missed-goals-every-morning': {
            'task': 'website.tasks.mark_missed_goals',
            # 'schedule': crontab(hour=0, minute=0),  # Runs daily at midnight
            "schedule": crontab()
        }
    }


def celery_init_app(app: Flask) -> Celery:
    class FlaskTask(Task):
        def __call__(self, *args: object, **kwargs: object) -> object:
            with app.app_context():
                return self.run(*args, **kwargs)

    celery_app = Celery(app.name, task_cls=FlaskTask)

    celery_app.config_from_object(CeleryConfig)
    celery_app.set_default()
    app.extensions["celery"] = celery_app
    return celery_app


def create_db(app):
    if not path.exists('website/' + DB_NAME):
        db.create_all(app=app)
        # If the database doesn't exist, initialize Flask-Migrate to handle migrations
        # migrate = Migrate(app, db)
        print('Created Database!')
