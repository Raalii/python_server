import requests
import json

class EventSender:
    def __init__(self, base_url_socket):
        self.base_url_socket = base_url_socket

    def send_event(self, event_data):
        node_server_url = f'{self.base_url_socket}/api/events'
        headers = {'Content-Type': 'application/json'}
        response = requests.post(node_server_url, data=json.dumps(event_data), headers=headers)

        if response.status_code != 200:
            print(f"Failed to send event to Node.js server: {response.text}")
