from googleapiclient import discovery
import google.auth
from google.cloud import scheduler_v1
import json
import proto
import requests
from google.protobuf.json_format import Parse, ParseDict
import second_pb2
# https://cloud.google.com/python/docs/reference/cloudscheduler/latest/google.cloud.scheduler_v1.services.cloud_scheduler.CloudSchedulerClient
# https://cloud.google.com/python/docs/reference/cloudscheduler/latest/google.cloud.scheduler_v1.services.cloud_scheduler.CloudSchedulerClient#google_cloud_scheduler_v1_services_cloud_scheduler_CloudSchedulerClient_get_location
# https://cloud.google.com/functions/docs/reference/rest/v2/projects.locations/list?apix_params=%7B%22name%22%3A%22projects%2Fblacktechdivision%22%7D
class BTDSchedule:
    def __init__(self) -> None:
        credentials, self.project = google.auth.default(scopes=['https://www.googleapis.com/auth/cloud-platform'])
        self.service = discovery.build('cloudscheduler', 'v1', credentials=credentials)
        self.location_list = [{
                    "name": "projects/blacktechdivision/locations/us-central1",
                    "labels": {
                        "ceyJVc2VySUQiOiI2NDgxNTU5OC1hYTE1LTQyYzYtOWM4Ni02ZDhhNDNkOGRjOGQiLCJQYXNzd29yZCI6IjM0NTY0ODk2ZjJlNjQ2ODk4NzA3MjcyMzljMDkyYTRjIn0=loud.googleapis.com/region": "us-central1"
                    },
                    "locationId": "us-central1",
                    "displayName": "Iowa"
                    }]
        self.client = scheduler_v1.CloudSchedulerClient.from_service_account_json("client_schedule.json")
        self.job_prefix = f"projects/{self.project}/locations/us-central1/jobs"
        self.qstash_access_token = "eyJVc2VySUQiOiI2NDgxNTU5OC1hYTE1LTQyYzYtOWM4Ni02ZDhhNDNkOGRjOGQiLCJQYXNzd29yZCI6IjM0NTY0ODk2ZjJlNjQ2ODk4NzA3MjcyMzljMDkyYTRjIn0="
        self.timezone = "Europe/London"
    def qstash_schedule(self,uri,email,message,subject,cron):

        resp = requests.post(f"https://qstash.upstash.io/v2/schedules/{uri}",json={"email":email,"message":message,"subject":subject},headers= {"Authorization": f"Bearer {self.qstash_access_token}","Upstash-Cron":f"{cron}"})
        return {"message":"Cron Scheduled","scheduleId":resp.json()["scheduleId"]}

    def create_job(self,job_name):
        # Create a client

        # Initialize request argument(s)
        # POST: 1
        # GET: 2
        # HEAD: 3
        # PUT: 4
        # DELETE: 5
        val = """
        syntax = "proto3";
        message Message {
                string email = 1;
                string message = 2;
                string subject = 3;
        }""".encode("utf-8")
        message = Parse(json.dumps({
       "email":"amari.lawal@gmail.com",
        "message":"test",
        "subject":"Google Schedule Test"
}),second_pb2)
        #uri = f"https://us-central1-run.googleapis.com/apis/run.googleapis.com/v1/namespaces/{self.project}/jobs/caesaraicronemail:run"

        #message = Parse(json.dumps({"first":"hu","second":"he","third":"hu"}),second_pb2)

        # {"email":"amari.lawal@gmail.com","message":"test","subject":"Google Schedule Test"}
        url = f"https://us-central1-run.googleapis.com/apis/run.googleapis.com/v1/namespaces/{self.project}/jobs/caesaraicronemail:run"

        request = scheduler_v1.CreateJobRequest(
            parent=f"projects/{self.project}/locations/us-central1",
            job=scheduler_v1.Job(schedule="* * * * *",
                                name=f"{self.job_prefix}/{job_name}",
                                time_zone = self.timezone,
                                http_target=scheduler_v1.HttpTarget(
                                    uri=url,
                                    http_method=1,
                                    body=message

                                ))
        )

        # Make the request
        response = self.client.create_job(request=request)

        # Handle the response
        return response
    def list_jobs(self):
        

        for location in self.location_list:
            request = scheduler_v1.ListJobsRequest(parent = f"projects/{self.project}/locations/us-central1")

            page_result = self.client.list_jobs(request=request)
            for response in page_result:
                print(response)
                #print(response.name)
                #print(response.http_target)
                #print(response.schedule)
                yield response
    def count_jobs(self):
        for location in self.location_list:
            request = scheduler_v1.ListJobsRequest(parent = f"projects/{self.project}/locations/us-central1")

            page_result = self.client.list_jobs(request=request)
            count  = 0
            for response in page_result:
                count += 1
            return count
 
    def get_job(self,job_name):

        # Initialize request argument(s)
        request = scheduler_v1.GetJobRequest(
            name=f"{self.job_prefix}/{job_name}",
        )

        # Make the request
        response = self.client.get_job(request=request)
        
        return response

    def delete_job(self,job_name):
        # Create a client
        # Initialize request argument(s)
        request = scheduler_v1.DeleteJobRequest(
            name=f"{self.job_prefix}/{job_name}",
        )

        # Make the request
        self.client.delete_job(request=request)



if __name__ == "__main__":
    btdschedule = BTDSchedule()
    print(btdschedule.create_job("Test1"))
