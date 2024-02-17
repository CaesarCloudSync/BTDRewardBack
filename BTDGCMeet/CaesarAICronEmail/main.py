import os
import base64
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from typing import Generic, TypeVar,Dict,List,AnyStr,Any,Union
import asyncio 
import uvicorn
import requests
from dotenv import load_dotenv
load_dotenv(".env")
from CaesarAIEmail import CaesarAIEmail

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


JSONObject = Dict[Any, Any]
JSONArray = List[Any]
JSONStructure = Union[JSONArray, JSONObject]
time_hour = (60 * 60) * 3 # 1 hour, * 3 hours

qstash_access_token = base64.b64decode(os.environ.get("QSTASH_ACCESS_TOKEN").encode()).decode()


@app.get('/')# GET # allow all origins all methods.
async def index():
    return "CaesarAI Send Email Hello World."



@app.post("/sendemail") # POST # allow all origins all methods.
async def sendemail(data : JSONStructure = None):  
    try:
        data = dict(data)#request.get_json()
        try:
            attachment = data["attachment"]
        except KeyError as kex:
            attachment = None
        CaesarAIEmail.send(**{"email":data["email"],"message":data["message"],"subject":data["subject"],"attachment":attachment})
        return {"message":"email has been sent."}
    except Exception as ex:
        return {"error":f"{type(ex)}-{ex}"}
    
@app.post("/sendemailkartra") # POST # allow all origins all methods.
async def sendemailkartra(email:str,message:str,subject:str,data : JSONStructure = None):  
    try:
        #data = dict(data)#request.get_json()
        attachment = None
        CaesarAIEmail.send(**{"email":email,"message":message,"subject":subject,"attachment":attachment})
        return {"message":"email has been sent."}
    except Exception as ex:
        return {"error":f"{type(ex)}-{ex}"}
@app.get("/schedule_network_reminder") # POST # allow all origins all methods.
async def schedule_network_reminder():  
    try:
        resplogin = requests.get("https://revisionbankcardlink-aoz2m6et2a-uc.a.run.app/getnotecard?h=edce3fb105538411a273665a8022f47&u=amari.network@gmail.com")
        revisioncard= resplogin.json()

        json_data = {"email":"amari.lawal05@gmail.com","subject":f"{revisioncard['subject']} - {revisioncard['revisioncardtitle']}","message":f"{revisioncard['revisioncard'].replace('.','<br>').replace('1','')}"}
        
        resp = requests.post("https://qstash.upstash.io/v2/schedules/https://caesaraicronemail-qqbn26mgpa-uc.a.run.app/sendemail",json=json_data,headers= {"Authorization": f"Bearer {qstash_access_token}","Upstash-Cron":"0 9 1 * *"})
        print()
        return {"message":"Reminder Scheduled","scheduleId":resp.json()["scheduleId"]}
    except Exception as ex:
        return {"error":f"{type(ex)}-{ex}"}
@app.post("/schedule_cron") # POST # allow all origins all methods.
async def schedule_cron(data : JSONStructure = None):  
    try:
        data = dict(data)
        attachment = data.get("attachment")
        if attachment:
            resp = requests.post("https://qstash.upstash.io/v2/schedules/https://caesaraicronemail-qqbn26mgpa-uc.a.run.app/sendemail",json={"email":data["email"],"message":data["message"],"subject":data["subject"],"attachment":attachment},headers= {"Authorization": f"Bearer {qstash_access_token}","Upstash-Cron":f"{data['cron']}"})
            return {"message":"Cron Scheduled","scheduleId":resp.json()["scheduleId"]}
        else:
            resp = requests.post("https://qstash.upstash.io/v2/schedules/https://caesaraicronemail-qqbn26mgpa-uc.a.run.app/sendemail",json={"email":data["email"],"message":data["message"],"subject":data["subject"]},headers= {"Authorization": f"Bearer {qstash_access_token}","Upstash-Cron":f"{data['cron']}"})
            print(resp.json())
            return {"message":"Cron Scheduled","scheduleId":resp.json()["scheduleId"]}

    except Exception as ex:
        return {"error":f"{type(ex)}-{ex}"}

async def main():
    config = uvicorn.Config("main:app", port=8080, log_level="info",host="0.0.0.0",reload=True)
    server = uvicorn.Server(config)
    await server.serve()

if __name__ == "__main__":
    asyncio.run(main())