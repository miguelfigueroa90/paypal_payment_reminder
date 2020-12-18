import os
import requests
from requests.api import head

class Api():
    """Perform Api operatios in Paypal."""
    def __init__(self) -> None:
        """Api Constructor."""
        super().__init__()

        self.check_token()

    def check_token(self):
        """Try to get the access token received from Paypal.
        If token file does no exist, it try to create a new one.
        """
        access_token_filename = 'access_token.txt'

        try:
            f = open(access_token_filename, "r")

            self.access_token = f.read()
        except FileNotFoundError:
            print(f'the file {access_token_filename} was not found.')
            print('generating new token...')

            self.generate_token(access_token_filename)

    def generate_token(self, access_token_filename):
        """Send a request to Paypal to get a new token."""
        url = 'https://api.sandbox.paypal.com/v1/oauth2/token'
        headers = {
            'Accept': 'application/json',
            'Accept-Language': 'en_US'
        }
        data = {
            'grant_type': 'client_credentials'
        }

        response = self.post(url, headers, data)

        if response.status_code == 200:
            self.access_token = response.json()['access_token']

            # Try to create a new file. If file exists, overwrite the content.
            try:
                f = open(access_token_filename, "x")
            except Exception:
                f = open(access_token_filename, "w")

            f.write(self.access_token)
            f.close()
        else:
            message = 'the request get a response with status code '
            message += f'{response.status_code}.'

            print(message)
            exit()

    def post(self, url, headers, data):
        """Perform a POST request and return the response."""
        auth = (
            os.getenv('PAYPAL_CLIENT_ID'),
            os.getenv('PAYPAL_SECRET'),
        )

        return requests.post(url, data, headers, auth=auth)