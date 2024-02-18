import os
import json
from CaesarAICronEmail.CaesarAIEmail import CaesarAIEmail
from google.auth.transport import requests
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.apps import meet_v2 as meet
from google.cloud import pubsub_v1
import threading
from datetime import datetime,timedelta
import time
#from BTDGCMeet.BTDRedis import BTDRedis
from BTDRedis import BTDRedis
os.environ["GOOGLE_APPLICATION_CREDENTIALS"]  = "google_credentials.json"
class BTDGCMeet:
    def __init__(self) -> None:
        self.USER_CREDENTIALS = self.authorize()
        self.TOPIC_NAME = "projects/blacktechdivision/topics/workspace-events"
        self.SUBSCRIPTION_NAME = "projects/blacktechdivision/subscriptions/workspace-events-sub"
        self.btdredis = BTDRedis()
        # Redis Format: time_spent = "0:00:31.058324"
        # Redis Format: space_info = "https://meet.google.com/cjj-reyw-vak|1:00:00.000018|RRULE:FREQ=WEEKLY;COUNT=3|0|"


    def authorize(self) -> Credentials:
        """Ensure valid credentials for calling the Meet REST API."""
        CLIENT_SECRET_FILE = "./MeetSecret/client_secret.json"
        credentials = None
        dir_path = os.path.dirname(os.path.realpath(__file__))

        if os.path.exists(f'{dir_path}/MeetSecret/token.json'):
            credentials = Credentials.from_authorized_user_file(f'{dir_path}/MeetSecret/token.json')

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
            with open(f"{dir_path}/MeetSecret/token.json", "w") as f:
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
    def format_participant_id(self,participant: meet.Participant):
        """Formats a participant for display on the console."""
        if participant.anonymous_user:
            return False

        if participant.signedin_user:
            return participant.signedin_user.user

        if participant.phone_user:
            return False

        return "Unknown participant"
    def parse_prefix(lself,line, fmt):
        try:
            t = datetime.strptime(line, fmt)
        except ValueError as v:
            if len(v.args) > 0 and v.args[0].startswith('unconverted data remains: '):
                line = line[:-(len(v.args[0]) - 26)]
                t = datetime.strptime(line, fmt)
            else:
                raise
        return t.time()
    def delete_space_if_all_hosted(self,space_id,space_info):
        overall_number_of_meetings = int(space_info.split("|")[2].split("=")[-1])
        number_times_hosted = int(space_info.split("|")[3])
        if overall_number_of_meetings == number_times_hosted+1:
            # delete space in redis
            self.btdredis.delete_space(space_id)
        else:
            number_times_hosted += 1
            space_info_list = space_info.split("|")
            space_info_list[3] = str(number_times_hosted)
            final_space_info = '|'.join(space_info_list)
            # set redis again
            self.btdredis.set_space(space_id,final_space_info)
        


    def fetch_percentage_time_spent(self,time_spent,duration):
        time_spent_strp = self.parse_prefix(time_spent,'%H:%M:%S')
        duration_strp = self.parse_prefix(duration,'%H:%M:%S')
        time_spent_delta = timedelta(hours=time_spent_strp.hour, minutes=time_spent_strp.minute, seconds=time_spent_strp.second)
        duration_delta = timedelta(hours=duration_strp.hour, minutes=duration_strp.minute, seconds=duration_strp.second)
        return (time_spent_delta/duration_delta) * 100
    def fetch_space_from_message(self,message: pubsub_v1.subscriber.message.Message):
        space = message.attributes.get("ce-subject").split("/")[-2] + "/" + message.attributes.get("ce-subject").split("/")[-1]
        return space
    def fetch_time_spent_and_conference_id(self,participant_info) -> str:
        conference_id,start_time_participant = participant_info.split("|")[0],participant_info.split("|")[1]
        time_spent_in_session = str(datetime.now() - datetime.fromisoformat(start_time_participant))
        return conference_id,time_spent_in_session




    def fetch_participant_from_session(self,session_name: str) -> meet.Participant:
        """Fetches the participant for a given session."""
        client = meet.ConferenceRecordsServiceClient(credentials=self.USER_CREDENTIALS)
        # Use the parent path of the session to fetch the participant details
        parsed_session_path = client.parse_participant_session_path(session_name)
        participant_resource_name = client.participant_path(
            parsed_session_path["conference_record"],
            parsed_session_path["participant"])
        return client.get_participant(name=participant_resource_name)
    def fetch_conference_from_session(self,session_name:str):
        client = meet.ConferenceRecordsServiceClient(credentials=self.USER_CREDENTIALS)
        parsed_session_path = client.parse_participant_session_path(session_name)
        return f"conferenceRecords/{parsed_session_path['conference_record']}"
    def fetch_conference_from_participant(self,resource_name):
        conference = resource_name.split("/")[0] + "/" + resource_name.split("/")[1]
        return conference
    def fetch_google_id(self,participant_id):
        return participant_id.split("/")[-1]



    def on_conference_started(self,message: pubsub_v1.subscriber.message.Message):
        """Display information about a conference when started."""
        payload = json.loads(message.data)
        resource_name = payload.get("conferenceRecord").get("name")
        client = meet.ConferenceRecordsServiceClient(credentials=self.USER_CREDENTIALS)
        conference = client.get_conference_record(name=resource_name)

        #self.btdredis.set_conference(conference.name,datetime.now().isoformat())
        print(f"Conference (ID {conference.name}) started at {conference.start_time.rfc3339()}")

    def on_conference_ended(self,message: pubsub_v1.subscriber.message.Message):
        """Display information about a conference when ended."""
        payload = json.loads(message.data)
        resource_name = payload.get("conferenceRecord").get("name")
        client = meet.ConferenceRecordsServiceClient(credentials=self.USER_CREDENTIALS)
        conference = client.get_conference_record(name=resource_name)
        space = self.fetch_space_from_message(message)
        space_info = self.btdredis.get_space(space)
        if space_info:
            self.delete_space_if_all_hosted(space,space_info)
        print(f"Conference (ID {conference.name}) ended at {conference.end_time.rfc3339()}")


    def on_participant_joined(self,message: pubsub_v1.subscriber.message.Message):
        """Display information about a participant when they join a meeting."""
        payload = json.loads(message.data)
        resource_name = payload.get("participantSession").get("name")
        client = meet.ConferenceRecordsServiceClient(credentials=self.USER_CREDENTIALS)
        session = client.get_participant_session(name=resource_name)
        conference = self.fetch_conference_from_participant(resource_name)
        participant = self.fetch_participant_from_session(resource_name)

        display_name = self.format_participant(participant)
        participant_id = self.format_participant_id(participant)
        self.btdredis.set_participant_session(participant_id,f"{conference}|{datetime.now().isoformat()}")
        print(f"{display_name} joined at {session.start_time.rfc3339()}")


    def on_participant_left(self,message: pubsub_v1.subscriber.message.Message):
        """Display information about a participant when they leave a meeting."""
        payload = json.loads(message.data)
        resource_name = payload.get("participantSession").get("name")
        client = meet.ConferenceRecordsServiceClient(credentials=self.USER_CREDENTIALS)
        session = client.get_participant_session(name=resource_name)
        participant = self.fetch_participant_from_session(resource_name)
        display_name = self.format_participant(participant)
        participant_id = self.format_participant_id(participant)
        participant_info = self.btdredis.get_participant_session(participant_id)
        if participant_info:
            conference_id,time_spent = self.fetch_time_spent_and_conference_id(participant_info)
            space = self.fetch_space_from_message(message)
            space_info = self.btdredis.get_space(space)
            if space_info: # This makes sure that expired events don't get reused to increase tokens.
                duration = space_info.split("|")[1]
                percent_spent = self.fetch_percentage_time_spent(time_spent,duration)
                if percent_spent > 80:
                    google_id = self.fetch_google_id(participant_id)
                    # TODO assign tokens use SQL database from mobile apps signup to match to google_id
            self.btdredis.delete_participant_session(participant_id)
                
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
            #try:
            future.result()

            #except KeyboardInterrupt:
            #    future.cancel()
        print("Done")
    def subscribe_futures(self,subscription_name: str = None):
        """Subscribe to events on the given subscription."""
        subscriber = pubsub_v1.SubscriberClient()
        future = subscriber.subscribe(subscription_name, callback=self.on_message)
        return future.result()
    def listen_redis(self):
        
        for spaceredis in self.btdredis.get_all_spaces():   
            space_name_session =list(spaceredis.keys())[0]
            space_name = space_name_session.split(":")[1]
            #print(space_name)
            meeting_uri =list(spaceredis.values())[0]
            print(f"Subscribing to meeting at {meeting_uri}, {space_name}")
            subscription =self.subscribe_to_space(topic_name=self.TOPIC_NAME, space_name=space_name)
            #print(subscription.json())
            #.delete_space(space_name)
        self.listen_for_events(subscription_name=self.SUBSCRIPTION_NAME)

    def create_listen(self):
        for i in range(3):
            space =  self.create_space()
            print(f"Join the meeting at {space.meeting_uri}")
            subscription = self.subscribe_to_space(topic_name=self.TOPIC_NAME, space_name=space.name)
            #print(subscription.json())
        self.listen_for_events(subscription_name=self.SUBSCRIPTION_NAME)
