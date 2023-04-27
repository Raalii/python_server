import datetime

import cv2
import numpy as np
from camera.CameraRecorder import CameraRecorder
from lib.lib import Lib
from ai.Alert import Alert
import pygame


class PersonDetector:
    def __init__(self, api_handler, cap):
        self.api_handler = api_handler
        self.alert = None
        self.cap = cap
        self.person_detected = False
        frame_size = (1920, 1080)
        # Créez un horodatage unique
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')

        # Créez le nom de fichier avec l'horodatage
        filename = f"./videos/video_{timestamp}.mp4"

        self.camera_recorder = CameraRecorder(filename, 10, frame_size, api_handler)
    

    def detect_persons_in_polygons(self, frame):
        # TODO : implémenter la fonctionnalité de détéction via l'API
        self.camera_recorder.handle_recording(frame, self.person_detected)
        self.alert_handler(self.cap.id, self.cap.url)
                            
        return frame


    def draw_detection_zone(self, image, points, color=(0, 255, 0), thickness=2):
        pts = np.array(points, np.int32)
        pts = pts.reshape((-1, 1, 2))
        return cv2.polylines(image, [pts], True, color, thickness)
    

    def alert_handler(self, camera_id, camera_url):
            if self.person_detected:
                # if not self.sound_played:
                if self.alert is None:
                    timestamp = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
                    self.alert = Alert(camera_id, timestamp, self.api_handler)
                    self.alert.lancer_alerte(camera_id, "Foire de Paris_Stand C10 - Caméra 1", camera_url)

            else:
                if self.alert is not None and not self.camera_recorder.recording:
                    new_url = self.api_handler.upload(self.camera_recorder.video_file_path)[0]['url']
                    self.alert.mettre_a_jour_url_camera(new_url)               
                    self.alert = None

        