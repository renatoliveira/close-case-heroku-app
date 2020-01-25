import os
import logging
import json

from flask import Flask, Response, request, redirect
from requests_oauthlib import OAuth2Session


client_id = os.environ.get('SF_CLIENT_ID')
client_secret = os.environ.get('SF_CLIENT_SECRET')
redirect_uri = os.environ.get('SF_CLIENT_REDIRECT_URI')
salesforce_env = os.environ.get('SF_ENV', default='login')

logging.basicConfig(level=logging.INFO)

logging.info('Client ID: {}'.format(client_id))
logging.info('Client Secret: {}'.format(client_secret))
logging.info('Client Refresh Token: {}'.format(redirect_uri))


app = Flask(__name__)


@app.route('/authorize', methods=['GET', 'POST'])
def handle_authorization():
    if request.method == 'POST':
        logging.info('Handling POST from the authorization method')

    elif request.method == 'GET':
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


@app.route('/<org_id>/<record_id>')
def close_case(org_id, record_id):

    logging.info('Closing case {} at org {}'.format(record_id, org_id))

    return Response(json.dumps({
        'org_id': org_id,
        'record_id': record_id
    }))


if not os.environ.get('IS_HEROKU', None) and __name__ == '__main__':
    app.run(host='localhost', port=8080, debug=True)

app.run(host='0.0.0.0', port=os.environ.get('PORT', default=5000), debug=False)
