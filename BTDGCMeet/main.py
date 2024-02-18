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

from fastapi.middleware.cors import CORSMiddleware
from CaesarJWT.caesarjwt import CaesarJWT
from CaesarSQLDB.caesar_create_tables import CaesarCreateTables
from CaesarJWT.caesarjwt import CaesarJWT
from CaesarAICronEmail.CaesarAIEmail import CaesarAIEmail
from typing import Annotated
import base64
from fastapi import FastAPI, File, Form, UploadFile
from fastapi.responses import RedirectResponse
from BTDCalendar.BTDCalendar import BTDCalendar
from BTDGCMeet import BTDGCMeet
from BTDCalendar.BTDCalendarModel import CreateEventModel
from CaesarAIRedis.BTDRedis import BTDRedis
import random
from datetime import datetime, timedelta
import isodate
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

JSONObject = Dict[Any, Any]
JSONArray = List[Any]
JSONStructure = Union[JSONArray, JSONObject]

CALENDAR_NAME = 'BTD Calendar'
btdcalendar = BTDCalendar()
btdgcmeet = BTDGCMeet()
btdredis = BTDRedis()
space = btdgcmeet.create_space()
calendar_exists = btdcalendar.check_calendar_exists(CALENDAR_NAME)
if not calendar_exists:
    btdcalendar.create_calendar(CALENDAR_NAME)

@app.get('/')# GET # allow all origins all methods.
async def index():
    return "Welcome to BTDGCMeet!"

@app.post("/v1/create_google_meet_event")
async def create_google_meet_event(event :CreateEventModel):
    event = event.model_dump()
    event_name = event["summary"]
    description = event["description"]

    recurrence = event["recurrence"][0]
    #duration = event_name["start"]["dateTime"]

    duration = str(datetime.fromisoformat(event["end"]["dateTime"])-datetime.fromisoformat(event["start"]["dateTime"]))

    if not btdcalendar.check_event_exists(CALENDAR_NAME,event_name):
        space = btdgcmeet.create_space()
        # maybe store space.name in redis
        #print(space.name)
        spaceredismapping = {"meeting_uri":space.meeting_uri,"duration":duration,"recurrence": recurrence,"notimeshosted":0}
        btdredis.set_space(space.name,spaceredismapping)
        event["description"] = f"Meeting ID:{space.meeting_uri}"+"<br>"+event["description"]
        btdcalendar.create_event(CALENDAR_NAME,event,verbose=0)
        for attendee in event["attendees"]:
            CaesarAIEmail.send(**{"email":attendee["email"],"subject":f"{event_name} Event","message":f"Meeting ID: {space.meeting_uri}<br>{description}"})
        CaesarAIEmail.send(**{"email":event["organizer"]["email"],"subject":f"{event_name} Event","message":f"Meeting ID: {space.meeting_uri}<br>{description}"})
        return {"message":f"{event_name} scheduled."}
    else:
        return {"error":"event already exists."}


if __name__ == "__main__":
    uvicorn.run("main:app",port=8080,log_level="info")
    #uvicorn.run()
    #asyncio.run(main())