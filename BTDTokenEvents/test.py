import requests
response = requests.post("http://127.0.0.1:8080/v1/api/healthcheck")
print(response.json())