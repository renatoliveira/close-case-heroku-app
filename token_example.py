# 'os' module to access environment variables
import os
# 'logging' to log things to the terminal
import logging

# 'requests_oauthlib's 'OAuth2Session' to handle the OAuth magic
from requests_oauthlib import OAuth2Session

logging.basicConfig(level=logging.INFO)

# Gets the basic connection info from the environment variables.
# If you don't want to assign the values to the env vars on your
# terminal session, then you can just replace the 'os.environ.get's
# with the values you've received and specified on your Connected
# App.

client_id = os.environ.get('SF_CLIENT_ID')
client_secret = os.environ.get('SF_CLIENT_SECRET')
redirect_uri = os.environ.get('SF_CLIENT_REDIRECT_URI')

# Remember that this is a demo script. It will show the sensitive
# data on your terminal with the following commands:
logging.info('Client ID: {}'.format(client_id))
logging.info('Client Secret: {}'.format(client_secret))
logging.info('Client Refresh Token: {}'.format(redirect_uri))

# Creates an authorization request
oauth = OAuth2Session(
    client_id=client_id,
    redirect_uri=redirect_uri,
    scope=['refresh_token', 'api', 'web']
)

# Posts the authorization request to an URL (the "authorization URL")
auth_url, state = oauth.authorization_url(
    'https://test.salesforce.com/services/oauth2/authorize'
)

# Prints it so you can click it (or copy and paste) on your browser.
# When you access this URL, you'll be redirected to Salesforce and
# will provide your username and password just like if you were
# authorizing Workbench or Marketing Cloud, for example!
print(auth_url)

# When you log in with your credentials you'll be redirected to
# the specified URL in your connected app (the "callback URL").
# It will likely contain extra arguments, but they will be handled
# by the oauth library. Just paste the whole URL to your terminal.
auth_response = input('Enter callback URL: ')

# Finally, having the authorization code on the URL (previous step)
# we can call Salesforce again and say that "the user has approved,
# here: proof" and it will issue a refresh token and an access token
# for us.
token = oauth.fetch_token(
    'https://test.salesforce.com/services/oauth2/token',
    authorization_response=auth_response,
    client_secret=client_secret
)

# 'token' is a JSON object containing the 'access_token' and
# 'refresh_token' that we'll need for other requests!

logging.info('Refresh token: {}'.format(token))

# This will get the endpoint that describes all the org's services
resource = oauth.get('https://test.salesforce.com/services/data/v47.0')

# If it is working, will pring a <Response [200]> in your terminal
print(resource)
