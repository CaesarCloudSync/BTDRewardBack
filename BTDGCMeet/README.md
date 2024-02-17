# Google Cloud Meet API setup

## Important API's 
- Google MEET API
- Google Workspace
- Google Pub/Sub
- Google Drive
- Google People API


## Google Meet Tutorial
- https://developers.google.com/meet/api/guides/tutorial-events-python
- **Be Wary of Permissions, gcloud auth login and project and service accounts**

1. To allow you to record meetings get Google Admin Account
2. Get Google Workspace account
3. Pay for Google workspace £5 month
4. Then automatically made meetings can be recordeed by host then sent to google drive 

1. Next add google calendar

Code above can stay the same it will do exactly this but google cloud run will force it to timeout.
TODO in hook specify who is the host to avoid trying to give tokens.
Can Track and assign BTD tokens. Store all the people who leave in that meeting and time left into redis. Then when When confirence end finishes for that meeting reward the people who left 5 minutes before max tokens.
TODO Google Calnedar
TODO Maybe make it use celery, the task will run. 
1. When calendar is created. It uses that time to programmatically cloud schedule a 3 minute cloud run job 
2. That will collect pub/sub for that specific meeting and assign tokens.

# projects/blacktechdivision/topics/workspace-events