from flask import Blueprint, render_template, url_for, redirect, flash, session, jsonify, request
from flask_login import login_required, current_user
import requests
import google.auth
import google.auth.transport.requests
import google.oauth2.credentials

import requests


classify = Blueprint('classify', __name__)


@classify.route('/textclassify', methods=['POST'])
@login_required
def text_classify_results():
    from website import create_app
    app = create_app()

    with app.app_context():

        credentials, _ = google.auth.default(scopes=['https://www.googleapis.com/auth/cloud-platform'])
        # credentials = google.oauth2.credentials.Credentials(
    # 'access_token')

        auth_req = google.auth.transport.requests.Request()
        credentials.refresh(auth_req)

        # for attr in dir(credentials):
        #     print("obj.%s = %r" % (attr, getattr(credentials, attr)))

        access_token = credentials.token

        ACCESS_TOKEN = access_token
        PROJECT_ID = app.config['PROJECT_ID']
        ENDPOINT_ID = app.config['ENDPOINT_ID']

        # print(
        #     f'ACCESS_TOKEN: ${access_token}, PROJECT_ID: ${PROJECT_ID}, ENDPOINT_ID: ${ENDPOINT_ID}')


        url = f"https://us-central1-aiplatform.googleapis.com/ui/projects/{PROJECT_ID}/locations/us-central1/endpoints/{ENDPOINT_ID}:predict"

        headers = {
            "Authorization": f"Bearer {ACCESS_TOKEN}",
            "Content-Type": "application/json"
        }

        # Get content from the request JSON
        data = request.get_json()
        # print(data)
        content = data.get('content', '')

        if not content:
            return jsonify({'error': 'No content provided'}), 400
        
        request_data = {
            "instances": {
                "mimeType": "text/plain",
                "content": content 
            }
        }

        response = requests.post(url, headers=headers, json=request_data)
        # response = requests.post(url, headers=headers, json=data)
        # for attr in dir(response):
        #     print("obj.%s = %r" % (attr, getattr(response, attr)))
        # breakpoint()
        # print(jsonify(response.json()))

        return jsonify(response.json())
