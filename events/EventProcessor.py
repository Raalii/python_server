import json
import re

import requests
from requests.auth import HTTPDigestAuth


class EventProcessor:
    def __init__(self, camera, username, password, event_sender, event_handler):
        self.camera = camera
        self.username = username
        self.password = password
        self.event_sender = event_sender
        self.event_handler = event_handler
        self.last_human_detection_timestamp = None

    def read_until_separator(self, separator, iterator):
        buffer = b""
        while True:
            chunk = next(iterator, None)
            if chunk is None:
                break
            buffer += chunk
            try:
                separator_index = buffer.index(separator)
                return buffer[:separator_index], buffer[separator_index + len(separator):]
            except ValueError:
                continue
        return None, buffer

    def parse_event_data(self, event_data_str):
        parts = re.split(r';', event_data_str)
        event_dict = {}
        for part in parts:
            key_value = part.split('=', 1)
            if len(key_value) == 2:
                key, value = key_value
                if key == 'data':
                    json_data = re.search(r'\{\s*\".*\}', value, re.DOTALL)
                    if json_data:
                        event_dict[key] = json.loads(json_data.group())
                elif key == 'index':
                    event_dict[key] = int(value)
                else:
                    event_dict[key] = value
        if 'data' not in event_dict:
            event_dict['data'] = {}
        return event_dict

    def process_stream(self):
        response = requests.get(self.camera.socket, auth=HTTPDigestAuth(
            self.username, self.password), stream=True)

        boundary = response.headers.get("Content-Type").split("boundary=")[1]

        content_iter = response.iter_content(chunk_size=1)
        buffer = b""
        while True:
            header_data, buffer = self.read_until_separator(
                b'\r\n\r\n', content_iter)
            if header_data is None:
                break
            headers = dict(line.split(b': ', 1)
                           for line in header_data.split(b'\r\n') if b': ' in line)
            content_length = int(headers.get(b'Content-Length', b'0'))
            event_data, buffer = self.read_until_separator(
                b'\r\n', content_iter)

            event_data_str = event_data.decode()
            print(
                f"Event data received for {self.camera.name}:", event_data_str)

            try:
                event_json = self.parse_event_data(event_data_str)
                print(f"Converted event data: {event_json}")

                event_json['camera'] = {"id": self.camera.id, "url": self.camera.url, "name": self.camera.name,
                                        "socket": self.camera.socket, "zones": self.camera.zones}
                if event_json:
                    self.event_handler(event_json, self, self.event_sender.send_event)
                    
            except Exception as e:
                print(f"Failed to parse event data: {event_data_str}")
                print(f"Error: {e}")
