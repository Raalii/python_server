import os
import threading
import time
from ai.Alert import Alert
from api.Strapi import StrapiClient
from api.WebhookHandler import WebhookHandler
from camera.CameraRecorder import CameraRecorder
from camera.CameraStream import CameraStream
from dotenv import load_dotenv
from events.EventProcessor import EventProcessor
from events.EventSender import EventSender

load_dotenv()


class DetectionManager:
    def __init__(self, strapi_base_url):
        self.strapi_client = StrapiClient(strapi_base_url)
        self.cameras = [CameraStream(id=camera_data["id"], url=camera_data["url"],
                                     polygons=camera_data["polygons"], name=camera_data["name"], socket=camera_data["socket"], api_handler=self.strapi_client) for camera_data in self.strapi_client.cameras]
        self.recorders = [CameraRecorder(video_file_path=f"{camera.id}_recording.mp4", fps=10, frame_size=(
            704, 576), api_handler=self.strapi_client) for camera in self.cameras]
        self.alerts = [Alert(camera_id=camera.id, timestamp=None,
                             api_handler=self.strapi_client) for camera in self.cameras]
 
    def handle_event(self, event, event_processor, event_sender):
        if event['Code'] == 'CrossRegionDetection' or event['Code'] == 'SmartMotionHuman':
            current_time = time.time()
            detection_delay_threshold = 10  # 10 second of delay

            if event_processor.last_human_detection_timestamp is None :
                event_processor.last_human_detection_timestamp = current_time
                event_sender(event)
                self.process_detection(event)
            elif (current_time - event_processor.last_human_detection_timestamp) >= detection_delay_threshold :
                event_processor.last_human_detection_timestamp = None
                # TODO : récupérer la vidéo et l'envoyer sur strapi.
                pass
            else :
                # TODO : faire l'enregistrement de la vidéo
                pass

    def process_detection(self, event_data):
        for camera, recorder, alert in zip(self.cameras, self.recorders, self.alerts):
            if event_data["camera"]["id"] == camera.id:
                person_detected = event_data["Code"] == 'CrossRegionDetection' or event_data["Code"] == 'SmartMotionHuman'
                if person_detected and not recorder.is_recording():
                    alert.lancer_alerte(
                        camera_id=camera.id, nom_alerte="Personne détectée", camera_url=camera.url)
                    recorder.start_recording()

    def run(self):
        event_sender = EventSender(
            base_url_socket=os.getenv("BASE_URL_SOCKET"))

        threads = []

        for camera in self.cameras:
            event_processor = EventProcessor(camera, os.getenv("USERNAME_CAM"), os.getenv(
                "PASSWORD_CAM"), event_sender, self.handle_event)
            thread = threading.Thread(target=event_processor.process_stream)
            thread.start()
            threads.append(thread)

        for thread in threads:
            thread.join()


def main():

    strapi_base_url = os.getenv("BASE_URL_API")

    detection_manager = DetectionManager(strapi_base_url)

    detection_manager.run()


if __name__ == "__main__":
    main()


# CrossRegionDetection, SmartMotionHuman
