#!/bin/bash
git add .
git commit -m "$1"
git push origin terraformbtd:terraformbtd
docker build -t palondomus/blacktechdivisionreward:bestest .
docker push palondomus/blacktechdivisionreward:bestest
terraform init
terraform plan
url=$(terraform apply) | grep blacktechdivisionreward
curl "${url/service_url = /""}"  
#docker run -it -p 8080:8080 palondomus/blacktechdivisionreward:bestest
