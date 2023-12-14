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


@app.get('/')# GET # allow all origins all methods.
async def index():
    return "Welcome to CaesarAIWorld!"
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
    
@app.post("/v1/reward")
def reward(data : JSONStructure = None, authorization: str = Header(None)):
   
    email = caesarjwt.secure_decode(authorization.replace("Bearer ",""))["email"]
    if email:
            data = dict(data)
            reward = data["reward"]
            rewardlead = caesarcrud.check_exists(("*"),"rewardleads",f"email = '{email}'")
            if not rewardlead:
                res = caesarcrud.post_data(("email","reward"),(email,reward),"rewardleads")
            else:
                old_reward = caesarcrud.get_data(("reward",),"rewardleads",f"email = '{email}'")[0]["reward"]
                new_reward = old_reward + reward
                res = caesarcrud.update_data(("reward",),(new_reward,),"rewardleads",f"email = '{email}'")
            return {"message":f"lead rewarded {new_reward}."}
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




            
    
@app.post('/v1/rewardlead')# GET # allow all origins all methods.
async def rewardlead(reward : int,api_key :str,api_pass:str,amariverbose: Union[str, None] = None,mulaverbose: Union[str, None] = None,data : JSONStructure = None):
    try:
        if api_key == KARTRA_API_KEY and api_pass == KARTRA_API_PASSWORD:
            data = dict(data)
            # TODO Store or update storing reward
            leadaction = data["action"]
            lead_user = data["lead"]
            first_name = lead_user["first_name"]
            last_name = lead_user["last_name"]
            last_name2 = lead_user["last_name2"]
            email = lead_user["email"]
            phone_country_code = lead_user["phone_country_code"]
            phone = lead_user["phone"]
            company = lead_user["company"]
            address = lead_user["address"]
            city = lead_user["city"]
            zip_code = lead_user["zip"]
            state = lead_user["state"]
            country = lead_user["country"]
            date_joined = lead_user["date_joined"]
            # TODO Store reward and match it to the user hash.
            lead_exists = caesarcrud.check_exists(("*"),"userleads",f"email = '{email}'")
            if not lead_exists:
                res = caesarcrud.post_data(("first_name","last_name","last_name2","email","address"),(first_name,last_name,last_name2,email,address),"userleads")
            
            rewardlead = caesarcrud.check_exists(("*"),"rewardleads",f"email = '{email}'")
            if not rewardlead:
                res = caesarcrud.post_data(("email","reward"),(email,reward),"rewardleads")
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
                    res = caesarcrud.post_data(("email","reward","action"),(email,reward,leadaction),"rewardactionlogs")
                    if amariverbose:
                        CaesarAIEmail.send(**{"email":"revisionbankedu@gmail.com","message":f"{first_name} {last_name} - {email} gained {reward} BTD Tokens doing {leadaction} new balance is {new_reward}","subject":f"{first_name} {last_name} - {email} gained {reward} doing {leadaction}","attachment":None})
                
                    if mulaverbose:
                        CaesarAIEmail.send(**{"email":"info@mulacake.com","message":f"{first_name} {last_name} - {email} gained {reward} BTD Tokens doing {leadaction} new balance is {new_reward}","subject":f"{first_name} {last_name} - {email} gained {reward} doing {leadaction}","attachment":None})

                
                    return {"message":f"lead rewarded {reward} for {leadaction}. Total: {new_reward}"}
    

            
        else:
            return {"error":"not authorized api key and api password incorrect."}
    except Exception as ex:
        CaesarAIEmail.send(**{"email":"revisionbankedu@gmail.com","message":f"Error: {type(ex)} - {ex}","subject":f"Lead Error {email} - {leadaction} - {reward}","attachment":None})
        return {"error":f"{type(ex)},{ex}"}



if __name__ == "__main__":

    uvicorn.run("main:app",port=8080,log_level="info")
    #uvicorn.run()
    #asyncio.run(main())