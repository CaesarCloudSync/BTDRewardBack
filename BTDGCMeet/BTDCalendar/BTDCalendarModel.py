from pydantic import BaseModel,Field,model_validator
from typing import List,Optional,Any
from datetime import datetime,date
import re
from BTDExceptions import UserMissingPrimaryKey,NotEmailAddress,RecurrenceRRuleFormatIncorrect,NoRecurrenceField,NotIsoFormat
class AttendeeDataModel(BaseModel):
    email: Optional[str] = None
    id: Optional[str] =None
    displayName:Optional[str] =None
    organizer: bool = False
    optional:bool = False
    @model_validator(mode="before")
    @classmethod
    def from_literal(cls, data: Any) -> Any:
        if not data.get("email") and not data.get("id"):
            raise UserMissingPrimaryKey(f"email or id missing key in attendee")
        if data.get("email"):
            if "@" not in data.get("email"):
                raise NotEmailAddress(f"{data.get('email')} is not an email address.")
        return data


class OrganizerModel(BaseModel):
    email: Optional[str] = None
    id: Optional[str] = None
    displayName:Optional[str] = None
    self : bool = True

    @model_validator(mode="before")
    @classmethod
    def from_literal(cls, data: Any) -> Any:
        """Automatically parse 'x|y' literals"""
        if not data.get("email") and not data.get("id"):
            raise UserMissingPrimaryKey(f"email or id missing key in organizer.")
        if data.get("email"):
            if "@" not in data.get("email"):
                raise NotEmailAddress(f"{data.get('email')} is not an email address.")
        return data

class ReminderMethodModel(BaseModel):  
    method :str = Field(min_length=1, pattern=r"email|popup",default='email') # pop up
    minutes: int = 60 #24 * 60



class ReminderModel(BaseModel):
    useDefault: bool = False
    overrides:List[ReminderMethodModel] = Field(min_length=1) 



class EventTimeModel(BaseModel):
    dateTime: str
    timeZone:str = Field(min_length=1, pattern=r"[A-Z][a-z]+\/[A-Z][a-z]+",default='Europe/London')
    @model_validator(mode="before")
    @classmethod
    def from_literal(cls, data: Any) -> Any:
        """Automatically parse 'x|y' literals"""
        try:
            datetime.fromisoformat(data.get("dateTime"))

        except ValueError:
            raise NotIsoFormat("Not in ISO Format.")
        return data
class CreateEventModel(BaseModel):
    summary:str
    location:str
    description:str
    #colorId: Optional[str] = "#46d6db"
    attendees:List[AttendeeDataModel] = Field(min_length=1) 
    start:EventTimeModel
    end:EventTimeModel
    organizer : OrganizerModel
    attachments :Optional[List[str]] = None # https url
    reminders:ReminderModel
    recurrence:List[str] = Field(min_length=1,max_length=1) #RRULE:FREQ=DAILY;COUNT=2
    @model_validator(mode="before")
    @classmethod
    def from_literal(cls, data: Any) -> Any:
        """Automatically parse 'x|y' literals"""
        regex = r"RRULE\:FREQ\=(DAILY|WEEKLY|MONTHLY|YEARLY)\;COUNT=[0-9]+"
        recurrence = data.get("recurrence")
        for rec in recurrence:
            try:
                res = re.compile(regex).match(rec)
                res.group()
            except AttributeError as aex:
                raise RecurrenceRRuleFormatIncorrect(f"{rec} is incorrect format please use RRULE:FREQ=DAILY;COUNT=2 format.")
            


        return data
class SpaceRedisMappingModel(BaseModel):
    meeting_uri:str
    duration:str
    recurrence:str 
    notimeshosted:int
    @model_validator(mode="before")
    @classmethod
    def from_literal(cls, data: Any) -> Any:
        """Automatically parse 'x|y' literals"""
        regex = r"RRULE\:FREQ\=(DAILY|WEEKLY|MONTHLY|YEARLY)\;COUNT=[0-9]+"
        recurrence = data.get("recurrence")

        try:
            res = re.compile(regex).match(recurrence)
            res.group()
        except AttributeError as aex:
            raise RecurrenceRRuleFormatIncorrect(f"{recurrence} is incorrect format please use RRULE:FREQ=DAILY;COUNT=2 format.")
        return data
    
        


class CreateCalendarModel(BaseModel):
    summary:str
    timeZone:str = Field(min_length=1, pattern=r"[A-Z][a-z]+\/[A-Z][a-z]+",default='Europe/London')
