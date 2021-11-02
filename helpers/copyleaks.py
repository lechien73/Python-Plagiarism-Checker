import requests
import json
from datetime import datetime, timedelta
import dateutil.parser
import pytz


API_SERVER_URI = 'https://api.copyleaks.com'
IDENTITY_SERVER_URI = 'https://id.copyleaks.com'

USER_AGENT = 'python-sdk/3.0'


class Products:
    BUSINESSES = 'businesses'
    EDUCATION = 'education'


class Copyleaks(object):

    @staticmethod
    def login(email, key):

        assert email and key

        url = f"{IDENTITY_SERVER_URI}/v3/account/login/api"
        payload = {
            'email': email,
            'key': key
        }

        headers = {
            'Content-Type': 'application/json',
            'User-Agent': USER_AGENT
        }

        response = requests.post(url, headers=headers, data=json.dumps(payload))
        
        if response.ok:
            return response.json()


    @staticmethod
    def verify_auth_token(auth_token):
        '''
            Verify that Copyleaks authentication token is exists and not expired.

            Parameters:
                auth_token: Copyleaks authentication token

            Raises:
                `AuthExipredError`: authentication expired. Need to login again.
        '''
        assert auth_token and auth_token['.expires'] and auth_token['access_token']

        now = pytz.UTC.localize(datetime.utcnow() + timedelta(0, 5 * 60))  # adds 5 minutes ahead for a safety shield.
        upTo = dateutil.parser.parse(auth_token['.expires'])


    @staticmethod
    def submit_url(product, auth_token, scan_id, submission):
        
        assert product
        url = f"{API_SERVER_URI}/v3/{product}/submit/url/{scan_id}"

        Copyleaks.verify_auth_token(auth_token)

        headers = {
            'Content-Type': 'application/json',
            'User-Agent': USER_AGENT,
            'Authorization': f"Bearer {auth_token['access_token']}"
        }

        response = requests.put(url, headers=headers, data=json.dumps(submission))
        if response.ok:
            return  # Completed successfully
