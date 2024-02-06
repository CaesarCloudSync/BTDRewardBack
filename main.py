import os
import io
import json
import base64
import hashlib
import asyncio 
import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, Header,Request,File, UploadFile,status,Form
from fastapi.responses import StreamingResponse,FileResponse,Response
from typing import Dict,List,Any,Union
from CaesarSQLDB.caesarcrud import CaesarCRUD
from CaesarSQLDB.caesarhash import CaesarHash
from fastapi.responses import StreamingResponse
from fastapi import WebSocket,WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from CaesarJWT.caesarjwt import CaesarJWT
from CaesarSQLDB.caesar_create_tables import CaesarCreateTables
from CaesarJWT.caesarjwt import CaesarJWT
from CaesarAICronEmail.CaesarAIEmail import CaesarAIEmail
from typing import Annotated
import base64
from fastapi import FastAPI, File, Form, UploadFile
from fastapi.responses import RedirectResponse
import random
load_dotenv(".env")
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


caesarcrud = CaesarCRUD()
caesarjwt = CaesarJWT(caesarcrud)
maturityjwt = CaesarJWT(caesarcrud)
caesarcreatetables = CaesarCreateTables()
caesarcreatetables.create(caesarcrud)
JSONObject = Dict[Any, Any]
JSONArray = List[Any]
JSONStructure = Union[JSONArray, JSONObject]
KARTRA_API_KEY = os.getenv("KARTRA_API_KEY")
KARTRA_API_PASSWORD = os.getenv("KARTRA_API_PASSWORD")
KREF_DAILY_TOKENS = os.getenv("KREF_DAILY_TOKENS")
KREF_AUTHENTICATION = os.getenv("KREF_AUTHENTICATION")



connections: Dict[str, WebSocket] = {}
class ConnectionManager:
    """Class defining socket events"""
    def __init__(self):
        """init method, keeping track of connections"""
        self.active_connections = []
    
    async def connect(self, websocket: WebSocket):
        """connect event"""
        await websocket.accept()
        self.active_connections.append(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        """Direct Message"""
        await websocket.send_json(message)
    
    def disconnect(self, websocket: WebSocket):
        """disconnect event"""
        self.active_connections.remove(websocket)
manager = ConnectionManager()

@app.websocket("/get_downloadable_content/{client_id}")
async def get_downloadable_content(websocket: WebSocket, client_id: str):
    await manager.connect(websocket)

    try:
        while True:
            authinfo = await websocket.receive_json()
            try:
                #print(authinfo)
                authorization = authinfo["headers"]["Authorization"]
                current_user = maturityjwt.secure_decode(authorization.replace("Bearer ",""))["email"]
                email_exists = caesarcrud.check_exists(("*"),"users",f"email = '{current_user}'")

                if email_exists:
                    downloadables_exist = caesarcrud.check_exists(("*"),"downloadables")
                    if downloadables_exist:
                        for downloadable in caesarcrud.get_large_data(("downloadabletitle","kartralink","tokens","posterfiletype","poster"),"downloadables"):
                            downloadable = caesarcrud.tuple_to_json(("downloadabletitle","kartralink","tokens","posterfiletype","poster"),downloadable)
                            #print(downloadable["kartralink"])
                            downloadable["poster"] = downloadable["posterfiletype"] + caesarcrud.hex_to_base64(downloadable["poster"])
                            await manager.send_personal_message(downloadable,websocket)
                        await manager.send_personal_message({"finished":"all sent"},websocket)
                    else:
                        await manager.send_personal_message({"error":"downloadables don't exist."},websocket)
                else:
                    await manager.send_personal_message({"error":"unauthorized."},websocket)
            except Exception as ex:
                await manager.send_personal_message({"error":f"{type(ex)}-{ex}"},websocket)
                

                    
            # Do something with received data (optional)

    except WebSocketDisconnect:
        manager.disconnect(websocket)

@app.websocket("/admin_get_downloadable_content/{client_id}")
async def admin_get_downloadable_content(websocket: WebSocket, client_id: str):
    await manager.connect(websocket)

    try:
        while True:
            authinfo = await websocket.receive_json()
            try:
                if authinfo["api_key"] == KARTRA_API_KEY and authinfo["api_pass"] == KARTRA_API_PASSWORD:
                    downloadables_exist = caesarcrud.check_exists(("*"),"downloadables")
                    if downloadables_exist:
                        for downloadable in caesarcrud.get_large_data(("downloadabletitle","kartralink","tokens"),"downloadables"):
                            downloadable = caesarcrud.tuple_to_json(("downloadabletitle","kartralink","tokens"),downloadable)

                            await manager.send_personal_message(downloadable,websocket)
                        await manager.send_personal_message({"finished":"all sent"},websocket)
                    else:
                        await manager.send_personal_message({"error":"downloadables don't exist."},websocket)
                else:
                    await manager.send_personal_message({"error":"unauthorized."},websocket)
            except Exception as ex:
                await manager.send_personal_message({"error":f"{type(ex)}-{ex}"},websocket)
                

                    
            # Do something with received data (optional)

    except WebSocketDisconnect:
        manager.disconnect(websocket)
@app.post("/upload_downloadable")
async def upload_downloadable(poster: Annotated[bytes, File()],downloadabletitle: Annotated[str, Form()],kartralink: Annotated[str, Form()],tokens: Annotated[str, Form()]):
    try:
        #print(poster)
        encoded_post = base64.b64encode(poster).decode("utf-8")
        if "/9j" in encoded_post[:10]:
            prefix = "data:image/jpeg;base64,"
        if "iVB" in encoded_post[:10]:
            prefix = "data:image/png;base64,"
        downloadable_exists = caesarcrud.check_exists(("*"),"downloadables",f"kartralink = '{kartralink}' OR downloadabletitle = '{downloadabletitle}'")
        if downloadable_exists:
            return {"error":"downloadable already exists."}
        else:
            res = caesarcrud.post_data(("downloadabletitle","kartralink","tokens","posterfiletype"),(downloadabletitle,kartralink,tokens,prefix),"downloadables")
            res = caesarcrud.update_blob("poster",encoded_post,"downloadables",f"kartralink = '{kartralink}' OR downloadabletitle = '{downloadabletitle}'")
            return {"message":"downloadable was uploaded."}
    except Exception as ex:
        return {"error":f"{type(ex)}-{ex}"}
@app.delete("/delete_downloadable")
async def delete_downloadable(downloadabletitle : str):
    try:
        downloadable_exists = caesarcrud.check_exists(("*"),"downloadables",f"downloadabletitle = '{downloadabletitle}'")
        if downloadable_exists:
            res = caesarcrud.delete_data("downloadables",f"downloadabletitle = '{downloadabletitle}'")
            return {"message":"downloadable was deleted."}
        else:
            return {"error":"downloadable does not exist."}
    except Exception as ex:
        return {"error":f"{type(ex)}-{ex}"}


@app.get('/')# GET # allow all origins all methods.
async def index():
    return "Welcome to CaesarAIWorld! Hollo"
@app.post('/signupapi') # POST
async def signup(data: JSONStructure = None):
    try:
        signupdata = {}
        data = dict(data)
        hashed = hashlib.sha256(data["password"].encode('utf-8')).hexdigest()
        signupdata["email"] = data["email"]
        signupdata["password"] = hashed
        table = "users"
        condition = f"email = '{signupdata['email']}'"
        email_exists = caesarcrud.check_exists(("*"),"users",condition=condition)
        if email_exists:
            return {"message": "Email already exists"} # , 400
        elif not email_exists:

            res = caesarcrud.post_data(("email","password"),(signupdata["email"],signupdata["password"]),table=table)
            if res:
                access_token = caesarjwt.secure_encode({"email":signupdata["email"]})#create_access_token(identity=signupdata["email"])
                callback = {"status": "success","access_token":access_token}
            else:
                return {"error":"error when posting signup data."}
            return callback
    except Exception as ex:
        error_detected = {"error": "error occured","errortype":type(ex), "error": str(ex)}
        return error_detected
@app.post('/loginapi') # POST
async def login(login_details: JSONStructure = None): # ,authorization: str = Header(None)
    # Login API
    try:



        login_details = dict(login_details)
        #print(login_details)
        condition = f"email = '{login_details['email']}'"
        email_exists = caesarcrud.check_exists(("*"),"users",condition=condition)

        if email_exists:
            access_token = caesarjwt.provide_access_token(login_details,student=0)
            if access_token == "Wrong password":
                return {"message": "The username or password is incorrect."}
            else:
                return {"access_token": access_token}

        return {"message": "The username or password is incorrect."}
    except Exception as ex:
        return {"error": f"{type(ex)} {str(ex)}"}
@app.get('/v1/authenticatebtdtokenkartra') # POST
async def authenticatebtdtokenkartra(kref:str,lid:str): # ,authorization: str = Header(None)
    # Login API

    try:
        if kref == KREF_DAILY_TOKENS or kref == KREF_AUTHENTICATION:
            condition = f"kartraid = {lid}"
            kid_lead_exists = caesarcrud.check_exists(("*"),"userleads",condition=condition)

            if kid_lead_exists:
                kid_lead_email = caesarcrud.get_data(("email",),"userleads",condition=condition)[0]
                access_token = caesarjwt.secure_encode(kid_lead_email)
                return RedirectResponse(f"https://blacktechday.netlify.app/btdtokens?access_token={access_token}&email={kid_lead_email['email']}")

            return {"message": "The username or kid doesn't exist."}
        else:
            return {"error":"Unauthorized."}
    except Exception as ex:
        return {"error": f"{type(ex)} {str(ex)}"}
    
@app.post("/v1/reward")
def reward(api_key :str,api_pass:str,amariverbose: Union[str, None] = None,mulaverbose: Union[str, None] = None,data : JSONStructure = None):
    try:
        if api_key == KARTRA_API_KEY and api_pass == KARTRA_API_PASSWORD:
            email = data["email"]
            first_name = data["first_name"]
            last_name = data["last_name"]
            reward = data["reward"]
            leadaction = data.get("leadaction") if data.get("leadaction") else "assignedbyadmin"
            reward_details = email + leadaction
            rewardlead_b64 = base64.b64encode(reward_details.encode()).decode()
            lead_exists = caesarcrud.check_exists(("*"),"userleads",f"email = '{email}'")
            if not lead_exists:
                res = caesarcrud.post_data(("first_name","last_name","email"),(first_name,last_name,email),"userleads")
            
            rewardlead = caesarcrud.check_exists(("*"),"rewardleads",f"email = '{email}'")
            if not rewardlead:
                res = caesarcrud.post_data(("email","reward"),(email,reward),"rewardleads")
                res = caesarcrud.post_data(("email","reward","action","actiondetailsb64"),(email,reward,leadaction,rewardlead_b64),"rewardactionlogs")
                if amariverbose:
                    CaesarAIEmail.send(**{"email":"revisionbankedu@gmail.com","message":f"{first_name} {last_name} - {email} gained/created {reward} BTD Tokens doing {leadaction} new balance is {reward}","subject":f"{first_name} {last_name} - {email} gained {reward} doing {leadaction}","attachment":None})
            
                if mulaverbose:
                    CaesarAIEmail.send(**{"email":"info@mulacake.com","message":f"{first_name} {last_name} - {email} gained {reward} doing {leadaction} new balance is {reward} BTD Tokens","subject":f"{first_name} {last_name} - {email} gained {reward} doing {leadaction}","attachment":None})
                return {"message":f"lead rewarded and created {reward}. Total: {reward}"}
            
            else:
                old_reward = caesarcrud.get_data(("reward",),"rewardleads",f"email = '{email}'")[0]["reward"]
                new_reward = old_reward + reward
                if new_reward < 0:
                    return {"message":"Insufficient BTD Tokens."}
                else:
                    res = caesarcrud.update_data(("reward",),(new_reward,),"rewardleads",f"email = '{email}'")
                    res = caesarcrud.post_data(("email","reward","action"),(email,reward,leadaction),"rewardactionlogs")
                    if amariverbose:
                        CaesarAIEmail.send(**{"email":"revisionbankedu@gmail.com","message":f"{first_name} {last_name} - {email} gained {reward} BTD Tokens doing {leadaction} new balance is {new_reward}","subject":f"{first_name} {last_name} - {email} gained {reward} doing {leadaction}","attachment":None})
                
                    if mulaverbose:
                        CaesarAIEmail.send(**{"email":"info@mulacake.com","message":f"{first_name} {last_name} - {email} gained {reward} BTD Tokens doing {leadaction} new balance is {new_reward}","subject":f"{first_name} {last_name} - {email} gained {reward} doing {leadaction}","attachment":None})

                
                    return {"message":f"lead rewarded {reward} for {leadaction}. Total: {new_reward}"}
        else:
            return {"message":"Unauthorized"}
    except Exception as ex:
            if amariverbose:
                CaesarAIEmail.send(**{"email":"revisionbankedu@gmail.com","message":f"Error: {first_name} {last_name} - {email} gained {reward} BTD Tokens doing {leadaction} new balance is {new_reward}","subject":f"Error {first_name} {last_name} - {email} gained {reward} doing {leadaction}","attachment":None})
            return {"error":f"{type(ex)}-{ex}"}
@app.post("/v1/contentdownloaded")
def contentdownloaded(api_key :str,api_pass:str,amariverbose: Union[str, None] = None,mulaverbose: Union[str, None] = None,data : JSONStructure = None,authorization: str = Header(None)):
    try:
        email = caesarjwt.secure_decode(authorization.replace("Bearer ",""))["email"]
        if email:
            if api_key == KARTRA_API_KEY and api_pass == KARTRA_API_PASSWORD:
                data = dict(data)
                downloadabletitle = data["downloadabletitle"]
                reward = data["tokens"]
                leadaction = "downloadedcontent"
                downloadabletitle_hash = base64.b64encode(downloadabletitle.encode()).decode()
                
                contenthasbeendownloaded = caesarcrud.check_exists(("*"),"contentdownloaded",f"email = '{email}' AND downloadabletitle = '{downloadabletitle}'")
                if contenthasbeendownloaded:
                    return {"exists":"downloadable has already been downloaded."}
                else:
                    rewardlead = caesarcrud.check_exists(("*"),"rewardleads",f"email = '{email}'")
                    if not rewardlead:
                        res = caesarcrud.post_data(("email","reward"),(email,reward),"rewardleads")
                        res = caesarcrud.post_data(("email","reward","action","actiondetailsb64"),(email,reward,leadaction,downloadabletitle_hash),"rewardactionlogs")
                        if amariverbose:
                            CaesarAIEmail.send(**{"email":"revisionbankedu@gmail.com","message":f"{email} gained/created {reward} BTD Tokens doing {leadaction} new balance is {reward}","subject":f"{email} gained {reward} doing {leadaction}","attachment":None})
                    
                        if mulaverbose:
                            CaesarAIEmail.send(**{"email":"info@mulacake.com","message":f"{email} gained {reward} doing {leadaction} new balance is {reward} BTD Tokens","subject":f"{email} gained {reward} doing {leadaction}","attachment":None})
                        res = caesarcrud.post_data(("email","downloadabletitle","tokens"),(email,downloadabletitle,reward),"contentdownloaded")
                        return {"message":f"lead rewarded and created {reward}. Total: {reward}","reward":reward}
                    
                    else:
                        old_reward = caesarcrud.get_data(("reward",),"rewardleads",f"email = '{email}'")[0]["reward"]
                        new_reward = old_reward + reward
                        if new_reward < 0:
                            return {"message":"Insufficient BTD Tokens."}
                        else:
                            res = caesarcrud.update_data(("reward",),(new_reward,),"rewardleads",f"email = '{email}'")
                            res = caesarcrud.post_data(("email","reward","action","actiondetailsb64"),(email,reward,leadaction,downloadabletitle_hash),"rewardactionlogs")
                            if amariverbose:
                                CaesarAIEmail.send(**{"email":"revisionbankedu@gmail.com","message":f"{email} gained {reward} BTD Tokens doing {leadaction} new balance is {new_reward}","subject":f"{email} gained {reward} doing {leadaction}","attachment":None})
                        
                            if mulaverbose:
                                CaesarAIEmail.send(**{"email":"info@mulacake.com","message":f"{email} gained {reward} BTD Tokens doing {leadaction} new balance is {new_reward}","subject":f"{email} gained {reward} doing {leadaction}","attachment":None})
                            res = caesarcrud.post_data(("email","downloadabletitle","tokens"),(email,downloadabletitle,reward),"contentdownloaded")
                            return {"message":f"lead rewarded {reward} for {leadaction}. Total: {new_reward}","reward":new_reward}
            else:
                return {"message":"Unauthorized"}
    
    except Exception as ex:
        return {"error":f"{type(ex)} = {ex}"}
@app.post("/v1/storedinvitedfriend")
def storedinvitedfriend(data : JSONStructure = None):
    data = dict(data)
    friend_email = data["friend_email"]
    alias = data["alias"]

    alias_exists = caesarcrud.check_exists(("*"),"aliaslinks",f"alias = '{alias}'")
    if alias_exists:
        friend_exists = caesarcrud.check_exists(("*"),"invitedfriends",f"friend_email = '{friend_email}'")
        if not friend_exists:
            alias_friend = caesarcrud.get_data(("email","alias","aliaslink","datewhenaliascreated"),"aliaslinks",condition=f"alias = '{alias}'")[0]
            email = alias_friend["email"]
            res = caesarcrud.post_data(("recommender_email","friend_email"),(email,friend_email),"invitedfriends")
            return {"message":"invite a friend taken note of."}
        else:
            return {"error":"This email has already been recommended."}


@app.get("/v1/getrewardtokens")
def getreward(authorization: str = Header(None)):
    email = caesarjwt.secure_decode(authorization.replace("Bearer ",""))["email"]
    if email:
        rewardlead = caesarcrud.check_exists(("*"),"rewardleads",f"email = '{email}'")
        if rewardlead:
            reward = caesarcrud.get_data(("reward",),"rewardleads",f"email = '{email}'")[0]["reward"]
            return {"email":email,"reward":reward}
        else:
            return {"email":email,"reward":0}
@app.post("/v1/storealiaslink")
def storealiaslink(data : JSONStructure = None,authorization: str = Header(None)):
    try:
        email = caesarjwt.secure_decode(authorization.replace("Bearer ",""))["email"]
        if email:
            data = dict(data)
            aliaslink_exists = caesarcrud.check_exists(("*"),"aliaslinks",f"email = '{email}'")
            if not aliaslink_exists:
                #print((email,data["alias"],data["aliaslink"],data["datewhenaliascreated"]))
                res = caesarcrud.post_data(("email","alias","aliaslink","datewhenaliascreated"),(email,data["alias"],data["aliaslink"],data["datewhenaliascreated"]),"aliaslinks")
                return {"message":"alias was stored.","aliaslink":data["aliaslink"]}
            else:
                return {"error":"alias already exists for this account."}

    except Exception as ex:
        return {"error":f"{type(ex)} = {ex}"}
    
@app.get("/v1/getaliaslink")
def getaliaslink(authorization: str = Header(None)):
    try:
        email = caesarjwt.secure_decode(authorization.replace("Bearer ",""))["email"]
        if email:
            aliaslink = caesarcrud.get_data(("email","alias","aliaslink","datewhenaliascreated"),"aliaslinks",f"email = '{email}'")
            if aliaslink:
                return aliaslink[0]
            else:
                return {"error":"aliaslink doesn't exist."}

    except Exception as ex:
        return {"error":f"{type(ex)} = {ex}"}




@app.get("/v1/getscoreboard")
def getscoreboard():
    rewardlead = caesarcrud.check_exists(("*"),"rewardleads")
    if rewardlead:
        all_rewards= caesarcrud.caesarsql.run_command("SELECT email,reward FROM rewardleads ORDER BY reward DESC",result_function=caesarcrud.caesarsql.fetch)
        if all_rewards:
            all_rewards = caesarcrud.tuple_to_json(("email","reward"),all_rewards)
            return {"scoreboard":all_rewards}
        else:
            return {"error":"no reward data in database"}



            

@app.get("/v1/get_number_of_members")
def get_number_of_members():
    all_leads_exist = caesarcrud.check_exists(("*"),"userleads")
    if all_leads_exist:
        membership_leads = caesarcrud.get_data(("email","membership"),"userleads")
        free_members = len(list(filter(lambda x:x["membership"] == "FREE MEMBERSHIP", membership_leads)))
        standard_membership = len(list(filter(lambda x:x["membership"] == "Membership 2024 Member", membership_leads)))

        return {"standard_membership":standard_membership,"free_members":free_members}
        #print(sum(list(filter(lambda x:x["membership"] == "FREE MEMBERSHIP", membership_leads))))
    else:
        CaesarAIEmail.send(**{"email":"revisionbankedu@gmail.com","message":f"No leads exist in userleads collection","subject":f"Error in get_number_of_members","attachment":None})
            
        return {"error":"no leads in database"}
    
@app.post('/v1/rewardlead')# GET # allow all origins all methods.
async def rewardlead(reward : int,api_key :str,api_pass:str,amariverbose: Union[str, None] = None,mulaverbose: Union[str, None] = None,data : JSONStructure = None):
    def random_with_N_digits(n):
        range_start = 10**(n-1)
        range_end = (10**n)-1
        return random.randint(range_start, range_end)
    try:
        if api_key == KARTRA_API_KEY and api_pass == KARTRA_API_PASSWORD:
            data = dict(data)
            # TODO Store or update storing reward
            leadaction = data["action"]
            lead_user = data["lead"]
            kartraid = lead_user["id"]
            first_name = lead_user["first_name"]
            last_name = lead_user["last_name"]
            email = lead_user["email"]
            action_details = data["action_details"]
            action_details_str = json.dumps(action_details)
            repeatable_action_tags = ["Daily Tokens"]
            # TODO add datetime column to rewardactionlogs
            if action_details.get("tag"):
                if action_details.get("tag").get("tag_name") in repeatable_action_tags:
                    # Vulnerability here, there could be digit clash, so the solution would be to count number of actions in rewardactionlogs, 
                    # To make it sustainable. Create MapReduce/Spark function that specifically counts number of actions done by user then returns it, fetching from large database.
                    action_details_hash = base64.b64encode(action_details_str.encode()).decode() + str(random_with_N_digits(6))
                else:
                    action_details_hash = base64.b64encode(action_details_str.encode()).decode() 
            else:
                action_details_hash = base64.b64encode(action_details_str.encode()).decode() 

                
            #print(data)
            #print(action_details_hash)

            # TODO Store reward and match it to the user hash.
            lead_exists = caesarcrud.check_exists(("*"),"userleads",f"email = '{email}'")
            if not lead_exists:
                res = caesarcrud.post_data(("kartraid","first_name","last_name","email"),(kartraid,first_name,last_name,email),"userleads")
                if action_details.get("tag"):
                    tag_name = action_details.get("tag").get("tag_name")
                    if "member" in tag_name.lower():
                        res = caesarcrud.update_data(("membership",),(tag_name,),"userleads",f"email = '{email}'")
            else:
                membership_now = caesarcrud.get_data(("membership",),"userleads",f"email = '{email}'")[0]
                if action_details.get("tag"):
                    tag_name = action_details.get("tag").get("tag_name")
                    if "member" in tag_name.lower():
                        if membership_now != tag_name:
                            res = caesarcrud.update_data(("membership",),(tag_name,),"userleads",f"email = '{email}'")

            
            rewardlead = caesarcrud.check_exists(("*"),"rewardleads",f"email = '{email}'")
            if not rewardlead:
                res = caesarcrud.post_data(("email","reward"),(email,reward),"rewardleads")
                res = caesarcrud.post_data(("email","reward","action","actiondetailsb64"),(email,reward,leadaction,action_details_hash),"rewardactionlogs")
                if amariverbose:
                    CaesarAIEmail.send(**{"email":"revisionbankedu@gmail.com","message":f"{first_name} {last_name} - {email} gained/created {reward} BTD Tokens doing {leadaction} new balance is {reward}<br> Action Details:{action_details_str}","subject":f"{first_name} {last_name} - {email} gained {reward} doing {leadaction}","attachment":None})
            
                if mulaverbose:
                    CaesarAIEmail.send(**{"email":"info@mulacake.com","message":f"{first_name} {last_name} - {email} gained {reward} doing {leadaction} new balance is {reward} BTD Tokens<br> Action Details:{action_details_str}","subject":f"{first_name} {last_name} - {email} gained {reward} doing {leadaction}","attachment":None})
                return {"message":f"lead rewarded and created {reward} for {leadaction}. Total: {reward}"}
            
            else:
                action_exists = caesarcrud.check_exists(("*"),"rewardactionlogs",f"email = '{email}' AND action = '{leadaction}' AND actiondetailsb64 = '{action_details_hash}'")
                if action_exists:
                    if action_details.get("tag"):
                        if action_details.get("tag").get("tag_name") in repeatable_action_tags:
                            CaesarAIEmail.send(**{"email":"revisionbankedu@gmail.com","message":f"{first_name} {last_name} - {email}  {leadaction} Action Details:{action_details_str}","subject":f"{first_name} {last_name} - {email}, Repeatable Tag assignment Error {action_details.get('tag').get('tag_name')}","attachment":None})
            
                    print({"error":"you have already done this action can't gain tokens."})
                    return {"error":"you have already done this action can't gain tokens."}
                else:
                    old_reward = caesarcrud.get_data(("reward",),"rewardleads",f"email = '{email}'")[0]["reward"]
                    new_reward = old_reward + reward
                    if new_reward < 0:
                        return {"message":"Insufficient BTD Tokens."}
                    else:
                        res = caesarcrud.update_data(("reward",),(new_reward,),"rewardleads",f"email = '{email}'")
                        res = caesarcrud.post_data(("email","reward","action","actiondetailsb64"),(email,reward,leadaction,action_details_hash),"rewardactionlogs")
                        if amariverbose:
                            CaesarAIEmail.send(**{"email":"revisionbankedu@gmail.com","message":f"{first_name} {last_name} - {email} gained {reward} BTD Tokens doing {leadaction} new balance is {new_reward}<br> Action Details:{action_details_str}","subject":f"{first_name} {last_name} - {email} gained {reward} doing {leadaction}","attachment":None})
                    
                        if mulaverbose:
                            CaesarAIEmail.send(**{"email":"info@mulacake.com","message":f"{first_name} {last_name} - {email} gained {reward} BTD Tokens doing {leadaction} new balance is {new_reward}<br> Action Details:{action_details_str}","subject":f"{first_name} {last_name} - {email} gained {reward} doing {leadaction}","attachment":None})

                    
                        return {"message":f"lead rewarded {reward} for {leadaction}. Total: {new_reward}"}
    

            
        else:
            return {"error":"not authorized api key and api password incorrect."}
    except Exception as ex:
        CaesarAIEmail.send(**{"email":"revisionbankedu@gmail.com","message":f"Error: {type(ex)} - {ex}","subject":f"Lead Error {email} - {leadaction} - {reward}","attachment":None})
        print({"error":f"{type(ex)},{ex}"})
        return {"error":f"{type(ex)},{ex}"}
@app.post('/v1/rewardinviteafriend')# GET # allow all origins all methods.
async def rewardinviteafriend(reward : int,api_key :str,api_pass:str,amariverbose: Union[str, None] = None,mulaverbose: Union[str, None] = None,data : JSONStructure = None):
    try:
        if api_key == KARTRA_API_KEY and api_pass == KARTRA_API_PASSWORD:
            data = dict(data)
            # TODO Store or update storing reward
            leadaction = "invite_a_friend_recommendation"
            lead_user = data["lead"]
            first_name = lead_user["first_name"]
            last_name = lead_user["last_name"]
            friend_email = lead_user["email"]
            invitedetails = lead_user + leadaction + friend_email
            rewardinviteafriend_hash = base64.b64encode(invitedetails.encode()).decode()

            # TODO Store reward and match it to the user hash.
            lead_exists = caesarcrud.check_exists(("*"),"userleads",f"email = '{friend_email}'")
            if not lead_exists:
                res = caesarcrud.post_data(("first_name","last_name","email"),(first_name,last_name,friend_email),"userleads")
            friend_exists = caesarcrud.check_exists(("*"),"invitedfriends",f"friend_email = '{friend_email}'")
            if friend_exists:
                invited_friend_data = caesarcrud.get_data(("recommender_email","friend_email"),"invitedfriends",f"friend_email = '{friend_email}'")[0]
                email = invited_friend_data["recommender_email"]
                rewardlead = caesarcrud.check_exists(("*"),"rewardleads",f"email = '{email}'")
                if not rewardlead:
                    res = caesarcrud.post_data(("email","reward"),(email,reward),"rewardleads")
                    res = caesarcrud.post_data(("email","reward","action","actiondetailsb64"),(email,reward,leadaction,rewardinviteafriend_hash),"rewardactionlogs")
                    if amariverbose:
                        CaesarAIEmail.send(**{"email":"revisionbankedu@gmail.com","message":f"{first_name} {last_name} - {email} gained/created {reward} BTD Tokens doing {leadaction} new balance is {reward}","subject":f"{first_name} {last_name} - {email} gained {reward} doing {leadaction}","attachment":None})
                
                    if mulaverbose:
                        CaesarAIEmail.send(**{"email":"info@mulacake.com","message":f"{first_name} {last_name} - {email} gained {reward} doing {leadaction} new balance is {reward} BTD Tokens","subject":f"{first_name} {last_name} - {email} gained {reward} doing {leadaction}","attachment":None})
                    return {"message":f"lead rewarded and created {reward} for {leadaction}. Total: {reward}"}
                
                else:
                    old_reward = caesarcrud.get_data(("reward",),"rewardleads",f"email = '{email}'")[0]["reward"]
                    new_reward = old_reward + reward
                    if new_reward < 0:
                        return {"message":"Insufficient BTD Tokens."}
                    else:
                        res = caesarcrud.update_data(("reward",),(new_reward,),"rewardleads",f"email = '{email}'")
                        res = caesarcrud.post_data(("email","reward","action","actiondetailsb64"),(email,reward,leadaction,rewardinviteafriend_hash),"rewardactionlogs")
                        if amariverbose:
                            CaesarAIEmail.send(**{"email":"revisionbankedu@gmail.com","message":f"{first_name} {last_name} - {email} gained {reward} BTD Tokens doing {leadaction} new balance is {new_reward}","subject":f"{first_name} {last_name} - {email} gained {reward} doing {leadaction}","attachment":None})
                    
                        if mulaverbose:
                            CaesarAIEmail.send(**{"email":"info@mulacake.com","message":f"{first_name} {last_name} - {email} gained {reward} BTD Tokens doing {leadaction} new balance is {new_reward}","subject":f"{first_name} {last_name} - {email} gained {reward} doing {leadaction}","attachment":None})

                    
                        return {"message":f"lead rewarded {reward} for {leadaction}. Total: {new_reward}"}
            else:
                return {"message":"no invite friend was used with this account."}
    

            
        else:
            return {"error":"not authorized api key and api password incorrect."}
    except Exception as ex:
        CaesarAIEmail.send(**{"email":"revisionbankedu@gmail.com","message":f"Error: {type(ex)} - {ex}","subject":f"Lead Error {email} - {leadaction} - {reward}","attachment":None})
        return {"error":f"{type(ex)},{ex}"}



if __name__ == "__main__":

    uvicorn.run("main:app",port=8080,log_level="info")
    #uvicorn.run()
    #asyncio.run(main())