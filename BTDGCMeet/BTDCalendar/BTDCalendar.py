from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from datetime import datetime, timedelta
import os.path
import pickle
from BTDExceptions import CalendarDoesNotExist,EventDoesNotExist,UpdateEventKeyDoesNotExist,NotIsoFormat
from BTDCalendar.BTDCalendarModel import CreateEventModel,CreateCalendarModel
from googleapiclient.discovery import Resource

# https://medium.com/@ayushbhatnagarmit/supercharge-your-scheduling-automating-google-calendar-with-python-87f752010375
# https://developers.google.com/calendar/api/v3/reference/events/insert
class BTDCalendar:
    def __init__(self) -> None:
        SCOPES = ['https://www.googleapis.com/auth/calendar']
        creds = None
        self.event_fields = ['summary','location','description','start',"end","timeZone"]
        dir_path = os.path.dirname(os.path.realpath(__file__))

        if os.path.exists(f'{dir_path}/CalendarSecrets/token.pickle'):
            with open(f'{dir_path}/CalendarSecrets/token.pickle', 'rb') as token:
                creds = pickle.load(token)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    f'{dir_path}/CalendarSecrets/gccalendar_credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)

            with open(f'{dir_path}/CalendarSecrets/token.pickle', 'wb') as token:
                pickle.dump(creds, token)

        self.service : Resource = build('calendar', 'v3', credentials=creds)
    def get_calendars(self,verbose=0,only_names=1):
        # Feature 1: List all calendars
        if verbose == 1:    
            print("Fetching all calendars:")
        calendar_list = self.service.calendarList().list().execute().get('items', [])
        if only_names == 1:
            return [ calendar["summary"] for calendar in calendar_list]
        else:
            return calendar_list
    def get_calendar(self,calendar_name,only_names=0):
        if self.check_calendar_exists(calendar_name):
            calendar_list = self.get_calendars(only_names=0)
            calendar_found = list(filter(lambda calendar: calendar["summary"] == calendar_name,calendar_list))[0]
            if only_names == 1:
                return [calendar["summary"] for calendar in calendar_found]
            else:
                return calendar_found
        else:
            raise CalendarDoesNotExist("Calendar does not exist when using get_calendar.")



    def check_calendar_exists(self,calendar_name:str):
        if calendar_name in self.get_calendars(only_names=1):
            return True
        else:
            return False

    def create_calendar(self,calendar_name,timezone='Europe/London',verbose=0):
        # Feature 2: Create a new calendar
        
        self.check_calendar_exists(calendar_name=calendar_name)
        new_calendar = CreateCalendarModel.model_validate({'summary': calendar_name,'timeZone': timezone})
        created_calendar = self.service.calendars().insert(body=new_calendar.model_dump()).execute()
        if verbose == 1:
            print("Created Calendar:",created_calendar)
            print(f"Created calendar: {created_calendar['id']}")
        return created_calendar
        # Feature 3: Insert an event
    def create_event(self,calendar_name,event,verbose=0):
        
        event = CreateEventModel.model_validate(event)
        if not self.check_calendar_exists(calendar_name):
            raise CalendarDoesNotExist("Calendar does not exist when using create_event.")
        else:
            calendar= self.get_calendar(calendar_name)
        created_event = self.service.events().insert(calendarId=calendar['id'], body=event.model_dump()).execute()
        if verbose == 1:
            print(f"Created event: {created_event['id']}")
            print("Create Event:",created_event)
        return created_event
    def check_event_exists(self,calendar_name,event_name):
        if event_name in  self.get_events(calendar_name,only_names=1):
            return True
        else:
            return False

    def get_events(self,calendar_name,only_names=0):
        if self.check_calendar_exists(calendar_name):
            calendar = self.get_calendar(calendar_name,only_names=0)
        else:
            raise CalendarDoesNotExist("Calendar does not exist when using get_events.")
  
        events = self.service.events().list(calendarId=calendar["id"]).execute().get('items', [])
        if only_names == 1:
            return [ calendar["summary"] for calendar in events]
        else:
            return events
        
    def get_event(self,calendar_name,event_name):
        if self.check_calendar_exists(calendar_name):
            if self.check_event_exists(calendar_name,event_name):
                events = self.get_events(calendar_name,only_names=0)
                return list(filter(lambda calendar: calendar["summary"] == event_name,events))[0]
            else:
                raise EventDoesNotExist("Event does not exist using get_event.")
        else:
            raise CalendarDoesNotExist("Calendar does not exist when using get_calendar.")
    def datetime_valid(self,dt_str):
        try:
           datetime.fromisoformat(dt_str)
        except:
            return False
        return True
    def update_event(self,calendar_name,event_name,event_key,event_value):
        if self.check_calendar_exists(calendar_name):
            if self.check_event_exists(calendar_name,event_name):
                event = self.get_event(calendar_name,event_name)
                calendar = self.get_calendar(calendar_name,only_names=0)
                # Feature 4: Update an event
                if event_key in self.event_fields:
                    if event_key == "start" or event_key == "end":
                        if self.datetime_valid(event_value):
                            event[event_key]["dateTime"] = event_value
                        else:
                            raise NotIsoFormat("Datetime is not in iso format.")
                    elif event_key == "timeZone":
                        event["start"][event_key] = event_value
                        event["end"][event_key] = event_value
                    updated_event = self.service.events().update(calendarId=calendar['id'], eventId=event['id'], body=updated_event).execute()
                    return updated_event
                else:
                    raise UpdateEventKeyDoesNotExist(f"Event Keys are: {self.event_fields}")
            else:
                raise EventDoesNotExist("Event does not exist using get_event.")
        else:
            raise CalendarDoesNotExist("Calendar does not exist when using get_calendar.")

        #print(f"Updated event: {updated_event['id']}")
    def delete_event(self,calendar_name,event_name):
        if self.check_calendar_exists(calendar_name):
            if self.check_event_exists(calendar_name,event_name):
                event = self.get_event(calendar_name,event_name)
                calendar = self.get_calendar(calendar_name,only_names=0)
                self.service.events().delete(calendarId=calendar['id'], eventId=event['id']).execute()
            else:
                raise EventDoesNotExist("Event does not exist using get_event.")
        else:
            raise CalendarDoesNotExist("Calendar does not exist when using get_calendar.")
        # Feature 5: Delete an event
    def get_colors(self):
        colors = self.service.colors().get().execute()
        for id, color in colors['event'].items():
            print ('colorId: %s' % id)
            print ('  Background: %s' % color['background'])
            print('  Foreground: %s' % color['foreground'])

                
