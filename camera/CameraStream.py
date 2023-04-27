from threading import Thread

import cv2


class CameraStream:
    def __init__(self, id, url, polygons, name, socket, api_handler):
        self.stream = cv2.VideoCapture(url)
        self.ret, self.frame = self.stream.read()
        self.stopped = False
        self.polygons = polygons
        self.id = id
        self.url = url
        self.name = name
        self.socket = socket
        self.api_handler = api_handler
        self.zones = self.get_zone()

    def get_zone(self):
        zones_data = self.api_handler.get(f"camera-zones?camera={self.id}&_populate=zone")["data"]
        return zones_data
    

    def start(self):
        thread_stream = Thread(target=self.update, args=())
        thread_stream.daemon = True
        thread_stream.start()
        return self

    def update(self):
        while True:
            if self.stopped:
                return
            try : 
                self.ret, self.frame = self.stream.read()
            except:
                return


    def read(self):
        return self.frame

    def release(self):
        self.stopped = True
        self.stream.release()