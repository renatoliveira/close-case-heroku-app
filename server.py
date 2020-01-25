import os
import logging
import json

from flask import Flask, request, redirect, jsonify
import requests
from requests_oauthlib import OAuth2Session


client_id = os.environ.get('SF_CLIENT_ID')
client_secret = os.environ.get('SF_CLIENT_SECRET')
redirect_uri = os.environ.get('SF_CLIENT_REDIRECT_URI')
salesforce_env = os.environ.get('SF_ENV', default='login')

logging.basicConfig(level=logging.INFO)

logging.info('Client ID: {}'.format(client_id))
logging.info('Client Secret: {}'.format(client_secret))
logging.info('Client Refresh Token: {}'.format(redirect_uri))

ACCESS_TOKEN = None
REFRESH_TOKEN = None
INSTANCE_URL = None


app = Flask(__name__)


@app.route('/authorize', methods=['GET'])
def handle_authorization():
    logging.info('Handling GET from the authorization method')

    oauth = OAuth2Session(
        client_id=client_id,
        redirect_uri=redirect_uri,
        scope=['refresh_token', 'api', 'web']
    )

    auth_url, state = oauth.authorization_url(
        'https://{}.salesforce.com/services/oauth2/authorize'.format(salesforce_env)
    )

    logging.info(state)
    logging.info(auth_url)

    return redirect(auth_url, code=302)

@app.route('/token', methods=['GET'])
def handle_token():
    global ACCESS_TOKEN
    global REFRESH_TOKEN
    global INSTANCE_URL

    logging.info('Handling GET from the authorization method')

    oauth = OAuth2Session(
        client_id=client_id,
        redirect_uri=redirect_uri,
        scope=['refresh_token', 'api', 'web']
    )

    token = oauth.fetch_token(
        'https://{}.salesforce.com/services/oauth2/token'.format(salesforce_env),
        authorization_response=request.url.replace('http://', 'https://'),
        client_secret=client_secret
    )

    ACCESS_TOKEN = token['access_token']
    REFRESH_TOKEN = token['refresh_token']
    INSTANCE_URL = token['instance_url']

    logging.info('Instance URL is now recognized as {}'.format(INSTANCE_URL))

    # Remove sensitive data, because we will return a JSON to the user
    del token['access_token']
    del token['refresh_token']

    return jsonify(token)

@app.route('/<org_id>/<record_id>')
def close_case(org_id, record_id):
    global INSTANCE_URL
    global ACCESS_TOKEN

    logging.info('Closing case {} at org {}'.format(record_id, org_id))
    logging.info(INSTANCE_URL)

    response = requests.post(
        '{}/services/apexrest/closeCase'.format(INSTANCE_URL),
        json={
            'req': {
                'caseId': record_id,
                'reason': 'User clicked the button on the email.'
            }
        },
        headers={
            'Authorization': 'Bearer {token}'.format(token=ACCESS_TOKEN),
            'Content-Type': 'application/json'
        }
    )

    if response.status_code >= 300:

        logging.error(response.json())

        return jsonify({
            'error': True
        })

    return redirect(response.json()['redirect_url'], code=302)


if not os.environ.get('IS_HEROKU', None) and __name__ == '__main__':
    app.run(host='localhost', port=8080, debug=True)

app.run(host='0.0.0.0', port=os.environ.get('PORT', default=5000), debug=False)
