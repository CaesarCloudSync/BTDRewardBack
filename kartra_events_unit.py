import json
import requests
uri = "http://127.0.0.1:8080" # https://blacktechdivisionreward-hrjw5cc7pa-uc.a.run.app
with open("kartra_events/assign_daily_token.json","r") as f:
    assign_daily = json.load(f)

response = requests.post(f"{uri}/v1/rewardlead?&reward=20&api_key=fPvimQSo&api_pass=xfdgUTCcYEqD&amariverbose=true",json=assign_daily)
print(response.json())

