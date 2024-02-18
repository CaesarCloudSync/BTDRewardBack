import json
import requests
import unittest
import sys
from datetime import datetime, timedelta

uri = "http://127.0.0.1:8080" #"https://blacktechdivisionreward-hrjw5cc7pa-uc.a.run.app"


class GCPMeetCase(unittest.TestCase):
    def test_create_event(self):
        event = {
        "summary": "Google I/O 2038",
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