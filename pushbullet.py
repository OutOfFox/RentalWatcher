import logging, requests

class Pushbullet:
    def __init__(self, access_token):
        self.access_token = access_token
        self.PUSHBULLET_URL = 'https://api.pushbullet.com/v2/pushes'
        self.headers = {
            'Authorization': 'Bearer ' + self.access_token,
            'Content-Type': 'application/json'
        }

    def send_message(self, message, link, body):
        payload = {
            'type': 'link',
            'title': message,
            'url': link,
            'body': body
        }

        response = requests.post(self.PUSHBULLET_URL, json=payload, headers=self.headers)
        if response.status_code != 200:
            logging.error('Pushbullet message could not be sent.')
            logging.debug(response)
            return False
        return True
