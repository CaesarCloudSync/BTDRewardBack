import os
import json
from CaesarAICronEmail.CaesarAIEmail import CaesarAIEmail
from google.auth.transport import requests
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.apps import meet_v2 as meet
from google.cloud import pubsub_v1
import threading
class BTDGCMeet:
    def __init__(self) -> None:
        self.USER_CREDENTIALS = self.authorize()


    def authorize(self) -> Credentials:
        """Ensure valid credentials for calling the Meet REST API."""
        CLIENT_SECRET_FILE = "./client_secret.json"
        credentials = None
        dir_path = os.path.dirname(os.path.realpath(__file__))

        if os.path.exists(f'{dir_path}/token.json'):
            credentials = Credentials.from_authorized_user_file(f'{dir_path}/token.json')

        if credentials is None:
            flow = InstalledAppFlow.from_client_secrets_file(
                CLIENT_SECRET_FILE,
                scopes=[
                    'https://www.googleapis.com/auth/meetings.space.created',
                ])
            flow.run_local_server(port=0)
            credentials = flow.credentials

        if credentials and credentials.expired:
            credentials.refresh(requests.Request())

        if credentials is not None:
            with open(f"{dir_path}/token.json", "w") as f:
                f.write(credentials.to_json())

        return credentials


    def create_space(self) -> meet.Space:
        """Create a new meeting space."""
        client = meet.SpacesServiceClient(credentials=self.USER_CREDENTIALS)
        request = meet.CreateSpaceRequest()
        return client.create_space(request=request)
    def subscribe_to_space(self,space_name: str = None, topic_name: str = None):
        """Subscribe to events for a given meeting space."""
        session = requests.AuthorizedSession(self.USER_CREDENTIALS)
        body = {
            'targetResource': f"//meet.googleapis.com/{space_name}",
            "eventTypes": [
                "google.workspace.meet.conference.v2.started",
                "google.workspace.meet.conference.v2.ended",
                "google.workspace.meet.participant.v2.joined",
                "google.workspace.meet.participant.v2.left",
                "google.workspace.meet.recording.v2.fileGenerated",
                "google.workspace.meet.transcript.v2.fileGenerated",
            ],
            "payloadOptions": {
                "includeResource": False,
            },
            "notificationEndpoint": {
                "pubsubTopic": topic_name
            },
            "ttl": "86400s",
        }
        response = session.post("https://workspaceevents.googleapis.com/v1/subscriptions", json=body)
        return response
    def format_participant(self,participant: meet.Participant) -> str:
        """Formats a participant for display on the console."""
        if participant.anonymous_user:
            return f"{participant.anonymous_user.display_name} (Anonymous)"

        if participant.signedin_user:
            return f"{participant.signedin_user.display_name} (ID: {participant.signedin_user.user})"

        if participant.phone_user:
            return f"{participant.phone_user.display_name} (Phone)"

        return "Unknown participant"


    def fetch_participant_from_session(self,session_name: str) -> meet.Participant:
        """Fetches the participant for a given session."""
        client = meet.ConferenceRecordsServiceClient(credentials=self.USER_CREDENTIALS)
        # Use the parent path of the session to fetch the participant details
        parsed_session_path = client.parse_participant_session_path(session_name)
        participant_resource_name = client.participant_path(
            parsed_session_path["conference_record"],
            parsed_session_path["participant"])
        return client.get_participant(name=participant_resource_name)


    def on_conference_started(self,message: pubsub_v1.subscriber.message.Message):
        """Display information about a conference when started."""
        payload = json.loads(message.data)
        resource_name = payload.get("conferenceRecord").get("name")
        client = meet.ConferenceRecordsServiceClient(credentials=self.USER_CREDENTIALS)
        conference = client.get_conference_record(name=resource_name)
        print(f"Conference (ID {conference.name}) started at {conference.start_time.rfc3339()}")
        CaesarAIEmail.send(**{"email":"amari.lawal@gmail.com","subject":f"Conference Started: {conference.name} at {conference.start_time.rfc3339()}","message":f"Conference Started: {conference.name} at {conference.start_time.rfc3339()}"})


    def on_conference_ended(self,message: pubsub_v1.subscriber.message.Message):
        """Display information about a conference when ended."""
        payload = json.loads(message.data)
        resource_name = payload.get("conferenceRecord").get("name")
        client = meet.ConferenceRecordsServiceClient(credentials=self.USER_CREDENTIALS)
        conference = client.get_conference_record(name=resource_name)
        print(f"Conference (ID {conference.name}) ended at {conference.end_time.rfc3339()}")


    def on_participant_joined(self,message: pubsub_v1.subscriber.message.Message):
        """Display information about a participant when they join a meeting."""
        payload = json.loads(message.data)
        resource_name = payload.get("participantSession").get("name")
        client = meet.ConferenceRecordsServiceClient(credentials=self.USER_CREDENTIALS)
        session = client.get_participant_session(name=resource_name)
        participant = self.fetch_participant_from_session(resource_name)
        display_name = self.format_participant(participant)
        print(f"{display_name} joined at {session.start_time.rfc3339()}")


    def on_participant_left(self,message: pubsub_v1.subscriber.message.Message):
        """Display information about a participant when they leave a meeting."""
        payload = json.loads(message.data)
        resource_name = payload.get("participantSession").get("name")
        client = meet.ConferenceRecordsServiceClient(credentials=self.USER_CREDENTIALS)
        session = client.get_participant_session(name=resource_name)
        participant = self.fetch_participant_from_session(resource_name)
        display_name = self.format_participant(participant)
        print(f"{display_name} left at {session.end_time.rfc3339()}")


    def on_recording_ready(self,message: pubsub_v1.subscriber.message.Message):
        """Display information about a recorded meeting when artifact is ready."""
        payload = json.loads(message.data)
        resource_name = payload.get("recording").get("name")
        client = meet.ConferenceRecordsServiceClient(credentials=self.USER_CREDENTIALS)
        recording = client.get_recording(name=resource_name)
        print(f"Recording available at {recording.drive_destination.export_uri}")


    def on_transcript_ready(self,message: pubsub_v1.subscriber.message.Message):
        """Display information about a meeting transcript when artifact is ready."""
        payload = json.loads(message.data)
        resource_name = payload.get("transcript").get("name")
        client = meet.ConferenceRecordsServiceClient(credentials=self.USER_CREDENTIALS)
        transcript = client.get_transcript(name=resource_name)
        print(f"Transcript available at {transcript.docs_destination.export_uri}")


    def on_message(self,message: pubsub_v1.subscriber.message.Message) -> None:
        """Handles an incoming event from pub/sub API."""
        event_type = message.attributes.get("ce-type")
        handler = {
            "google.workspace.meet.conference.v2.started": self.on_conference_started,
            "google.workspace.meet.conference.v2.ended": self.on_conference_ended,
            "google.workspace.meet.participant.v2.joined": self.on_participant_joined,
            "google.workspace.meet.participant.v2.left": self.on_participant_left,
            "google.workspace.meet.recording.v2.fileGenerated": self.on_recording_ready,
            "google.workspace.meet.transcript.v2.fileGenerated": self.on_transcript_ready,
        }.get(event_type)

        try:
            if handler is not None:
                handler(message)
            message.ack()
        except Exception as error:
            print("Unable to process event")
            print(error)


    def listen_for_events(self,subscription_name: str = None):
        """Subscribe to events on the given subscription."""
        subscriber = pubsub_v1.SubscriberClient()
        with subscriber:
            future = subscriber.subscribe(subscription_name, callback=self.on_message)
            print("Listening for events")
            try:
                future.result()

            except KeyboardInterrupt:
                future.cancel()
        print("Done")
    def subscribe_futures(self,subscription_name: str = None):
        """Subscribe to events on the given subscription."""
        subscriber = pubsub_v1.SubscriberClient()
        future = subscriber.subscribe(subscription_name, callback=self.on_message)
        return future.result()
if __name__ == "__main__":
    TOPIC_NAME = "projects/blacktechdivision/topics/workspace-events"
    SUBSCRIPTION_NAME = "projects/blacktechdivision/subscriptions/workspace-events-sub"
    btdgcmeet = BTDGCMeet()
    subscriber_shutdown = threading.Event()
    subscriber_futures = []
    space =  btdgcmeet.create_space()
    print(f"Join the meeting at {space.meeting_uri}")
    #print(space.name)
    subscription =btdgcmeet.subscribe_to_space(topic_name=TOPIC_NAME, space_name=space.name)
    btdgcmeet.listen_for_events(subscription_name=SUBSCRIPTION_NAME)