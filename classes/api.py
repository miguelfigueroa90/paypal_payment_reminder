import os
import requests
from requests.api import head

class Api():
    """Perform Api operatios in Paypal."""
    def __init__(self) -> None:
        """Api Constructor."""
        super().__init__()

        self.access_token_filename = 'access_token.txt'
        self.base_url = os.getenv('PAYPAL_BASE_URL')
        self.basic_credentials = (
            os.getenv('PAYPAL_CLIENT_ID'),
            os.getenv('PAYPAL_SECRET'),
        )
        self.check_token()

    def check_token(self):
        """Try to get the access token received from Paypal.
        If token file does no exist, it try to create a new one.
        """
        try:
            f = open(self.access_token_filename, "r")

            self.access_token = f.read()
        except FileNotFoundError:
            print(f'the file {self.access_token_filename} was not found.')
            print('generating new token...')

            self.generate_token()

    def check_invoices(self):
        """Get Paypal invoices, check if there is no payed invoices.
        If there is pending invoices, send a reminder."""
        url = f'{self.base_url}/v2/invoicing/invoices'

        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.access_token}'
        }

        response = self.get(url, headers)

        if response.status_code == 200:
            items = response.json()

            for item in items['items']:
                status = item['status']

                if ('UNPAID' == status
                    or 'SENT' == status
                    or 'PARTIALLY_PAID' == status):
                    # Send the reminder.
                    self.send_reminder(item)
        else:
            self.notify_response_code(response)

    def send_reminder(self, item):
        """Send a reminder for an invoice."""
        invoice_id = item['id']
        url = f'{self.base_url}/v2/invoicing/invoices/{invoice_id}/remind'
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.access_token}'
        }
        data = {
            "send_to_invoicer": "true",
            "send_to_recipient": "true",
        }

        response = self.post(url, headers)

        if response.status_code == 204:
            print(f'a remider was sent to invoice with id {invoice_id}.')
        else:
            self.notify_response_code(response)

    def generate_token(self):
        """Send a request to Paypal to get a new token."""
        url = f'{self.base_url}/v1/oauth2/token'
        headers = {
            'Accept': 'application/json',
            'Accept-Language': 'en_US'
        }
        data = {
            'grant_type': 'client_credentials'
        }

        response = self.post(url, headers, data, self.basic_credentials)

        if response.status_code == 200:
            self.access_token = response.json()['access_token']

            # Try to create a new file. If file exists, overwrite the content.
            try:
                f = open(self.access_token_filename, "x")
            except Exception:
                f = open(self.access_token_filename, "w")

            f.write(self.access_token)
            f.close()
        else:
            self.notify_response_code(response)

    def notify_response_code(self, response):
        """Print a response code and exit."""
        message = 'the request get a response with status code '
        message += f'{response.status_code}.'

        print(message)
        exit()

    def post(self, url, headers, data={}, credentials={}):
        """Perform a POST request and return the response."""
        return requests.post(url, data, headers=headers, auth=credentials)

    def get(self, url, headers):
        """Perform a GET request and return the response."""
        return requests.get(url, headers=headers)