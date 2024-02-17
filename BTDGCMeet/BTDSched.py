from google.cloud import scheduler_v1

project_id = "blacktechdivision"
client = scheduler_v1.CloudSchedulerClient.from_service_account_json(
    "./client_secret.json")

parent= client.location_path(project_id,'us-central1')

job={"name":"projects/your-project/locations/app-engine-location/jobs/traing_for_model",
     "description":"this is for testing training model",
     "http_target": {"uri":"https://us-central1-gerald-automl-test.cloudfunctions.net/automl-trainmodel-1-test-for-cron-job"},
     "schedule":"0 10 * * *",
     "time_zone":"Australia/Perth",
     }

training_job= client.create_job(parent,job)