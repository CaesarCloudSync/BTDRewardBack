import json
import requests
#def test():
from CaesarSQLDB.caesarcrud import CaesarCRUD
import base64
caesarcrud = CaesarCRUD()
#action_details_str = json.dumps(action_details)
#action_details_hash = base64.b64encode(action_details_str.encode()).decode()
with open("FreeMembers.json","r") as f:
    member2024 = json.load(f)["members"]
for member in member2024:
    caesarcrud.update_data(("membership",),("FREE MEMBERSHIP",),"userleads",f"email = '{member}'")
    action_details_str = json.dumps({
        "tag":{
        "tag_id":r"{{tag_id}}",
        "tag_name":"FREE MEMBERSHIP"
    }})
    action_details_hash = base64.b64encode(action_details_str.encode()).decode()
    res = caesarcrud.update_data(("actiondetailsb64",),(action_details_hash,),"rewardactionlogs",f"reward = 0")
    print(member)

#caesarcrud.delete_data("rewardleads","reward = 0")
#caesarcrud.delete_data("rewardactionlogs","reward = 0")
#for i in member2024:
#    res = caesarcrud.delete_data("userleads",f"email = '{i}'")
#    print(i)
def test():
    with open("event_tag_template.json","r") as f:
        event_read = json.load(f)


        
    with open("Membership2024.json","r") as f:
        member2024 = json.load(f)["members"]
    for member in member2024:
        # userleads, /rewardleads, rewardleadlogs
        # TODO Change the base64 for rewardleadlogs from  {"tag":{"tag_id":"{{tag_id}}","tag_name":"{{tag_name}}"}} with the tag ID when collected from the kartra_inbound_api
        event_read["lead"]["email"] = member
        event_read["lead"]["username"] = member.split("@")[0]
        event_read["action_details"]["tag"]["tag_name"] = "Membership 2024 Member"
        event_read["lead"]["first_name"] = member.split("@")[0]
        event_read["lead"]["last_name"] = member.split("@")[0]
        #print(event_read)
        response = requests.post("http://127.0.0.1:8080/v1/rewardlead?&reward=0&api_key=fPvimQSo&api_pass=xfdgUTCcYEqD&amariverbose=true",json=event_read)
        
        print(response.json())
# 

#print(len(data_html["members"]))