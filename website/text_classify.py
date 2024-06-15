from flask import Blueprint, render_template, url_for, redirect, flash, session, jsonify, request
from flask_login import login_required, current_user
import requests
# from .forms import JournalForm
import google.cloud
import google.auth
from google.auth.transport.requests import Request
import requests


text_classify = Blueprint('text_classify', __name__)


@text_classify.route('/textclassify', methods=['POST'])
# @login_required
def text_classify_results():
    from website import create_app
    app = create_app()
    # form= JournalForm()

    # if request.method == 'POST':
    #     text_entry = form.text_entry.data

    with app.app_context():

        credentials, _ = google.auth.default()
        access_token = credentials.token

        ACCESS_TOKEN = access_token
        PROJECT_ID = app.config['PROJECT_ID']
        ENDPOINT_ID = app.config['ENDPOINT_ID']

        print(
            f'ACCESS_TOKEN: ${ACCESS_TOKEN}, PROJECT_ID: ${PROJECT_ID}, ENDPOINT_ID: ${ENDPOINT_ID}')

        # content = request.form.get('content', '')

        url = f"https://us-central1-aiplatform.googleapis.com/ui/projects/${PROJECT_ID}/locations/us-central1/endpoints/${ENDPOINT_ID}:predict"

        headers = {
            "Authorization": f"Bearer ${ACCESS_TOKEN}",
            "Content-Type": "application/json"
        }

        data = {
            "instances": {
                "mimeType": "text/plain",
                "content": "I like being happy"
            }
        }

        response = requests.post(url, headers=headers, data=data)

        print(jsonify(response.json()))

        return jsonify(response.json())

        # return render_template("home.html", form=form)

        # requests.get()


 #     # Obtain credentials
    # creds, project_id = default(
    #     scopes=["https://www.googleapis.com/auth/cloud-platform"])

    #     # If credentials are expired or missing, refresh them
    #     if creds.expired and creds.refresh_token:
    #         creds.refresh(Request())