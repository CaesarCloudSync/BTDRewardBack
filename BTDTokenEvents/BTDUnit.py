import json
import requests
import unittest
import sys
from datetime import datetime, timedelta

uri = "http://127.0.0.1:8080" #"https://blacktechdivisionreward-hrjw5cc7pa-uc.a.run.app"

class KartraEvents(unittest.TestCase):
    def test_assign_daily_tokens(self):
        """
        Test Brief:
        This tests the assignment of tokens for daily tokenes or more generally repeatable actions.
        Normally it would block repeated actions to avoid duplicate tokens. It uses rewardactionlogs as a hash of the whole action_details object to determine if the action has been done before.
        To allow for repeatable tasks to be made a list of tags that are assigned on kartra is made, if the tag of the kartra event is the repeatable tags list it will generate a random number and add it to the hash.
        This will make the hash differenet.
        Vulnerability and Risks:
        - If kartra tag name changes, it has to be changed in:
            -  kartra api integrations
            - /v1/rewardleads
            - kartra tags
        - The random number is a 10 digit long random number, its unlikely but it is possible to have a hash collision.
        - Karta tag expiration stops duplicate token assignment, so expiration needs to be specified in kartra.
        """
        with open("kartra_events/assign_daily_token.json","r") as f:
            assign_daily = json.load(f)
        #for i in range(300):
        response = requests.post(f"{uri}/v1/rewardlead?&reward=20&api_key=fPvimQSo&api_pass=xfdgUTCcYEqD&amariverbose=true",json=assign_daily)
        print(response.json())
        self.assertEqual(response.json().get("error"),None)
        self.assertNotEqual(response.json().get("error"),"you have already done this action can't gain tokens.")
class KartraAuthTokens(unittest.TestCase):
    def test_auth_kartra_user(self):
        response = requests.get(f"{uri}/v1/authenticatebtdtokenkartra?kref=CdAaTisnL3Za&lid=10") # amari.lawal@gmail.com - get this from supabase kartraid userleads table
        # API log Success = INFO - Kartra Authentication Worked
        response = requests.get(f"{uri}/v1/authenticatebtdtokenkartra?kref=CdAaTisnL3Za&lid=11") # amari.lawal05@gmail.com - get this from supabase kartraid userleads table
        # API log Success = INFO - Kartra Authentication Worked
    def test_daily_tokens(self):
        response = requests.get(f"{uri}/v1/authenticatebtdtokenkartra?kref=5iGhjmo0NqCp&lid=10") # amari.lawal@gmail.com - get this from supabase kartraid userleads table
        # API log Success = INFO - Daily Tokens Authentication Worked
        response = requests.get(f"{uri}/v1/authenticatebtdtokenkartra?kref=5iGhjmo0NqCp&lid=11") # amari.lawal05@gmail.com - get this from supabase kartraid userleads table
        # API log Success = INFO - Daily Tokens Authentication Worked
class KartraShopTest(unittest.TestCase):
    def test_buy_item_1(self):
        response = requests.get(f"{uri}/v1/authenticatebtdtokenkartra?kref=NPzfqk58IZdT&lid=11") # amari.lawal@gmail.com - get this from supabase kartraid userleads table
        # API log Success = INFO - Shop Item 1 Redirect Works
        print(response.headers)
    def test_buy_item_2(self):
        response = requests.get(f"{uri}/v1/authenticatebtdtokenkartra?kref=rbGW6nusecZa&lid=11") # amari.lawal@gmail.com - get this from supabase kartraid userleads table
        # API log Success = INFO - Shop Item 2 Redirect Works

        print(response.headers)

class GCPMeetCase(unittest.TestCase):
    def test_create_event(self):
        event = {
        "summary": "Google I/O 2024",
        "location": "800 Howard St., San Francisco, CA 94103",
        "description": f"A chance to hear more about Google\"s developer products.",
        "start": {
            "dateTime": (datetime.utcnow() + timedelta(days=1)).isoformat(),
            "timeZone": "Europe/London",

        },
        "end": {
            "dateTime": (datetime.utcnow() + timedelta(days=1, hours=1)).isoformat(),
            "timeZone": "Europe/London",
        },
        "recurrence": [
            "RRULE:FREQ=WEEKLY;COUNT=3"
        ],
        "attendees": [
            {"email": "amari.lawal@gmail.com"},
            {"email": "bobhillus@gmail.com"},
        ],
        "reminders": {
            "useDefault": False,
            "overrides": [
            {"method": "email", "minutes": 24 * 60},
            {"method": "popup", "minutes": 10},
            ],
        },
        "organizer": {

                "email": "amari.lawal@gmail.com",

            }
        }
        response = requests.post(f"{uri}/v1/create_google_meet_event",json=event)
        print(response.json())

if __name__ == "__main__":
    unittest.main()