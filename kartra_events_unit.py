import json
import requests
import unittest
import sys

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
        response = requests.post(f"{uri}/v1/rewardlead?&reward=20&api_key=fPvimQSo&api_pass=xfdgUTCcYEqD&amariverbose=true",json=assign_daily)
        #print(response.json())
        self.assertEqual(response.json().get("error"),None)
        self.assertNotEqual(response.json().get("error"),"you have already done this action can't gain tokens.")


if __name__ == "__main__":
    unittest.main()