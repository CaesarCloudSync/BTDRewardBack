#!/bin/bash

git add .
git commit -m "$1"
git push origin -u terraformbtd:terraformbtd
docker build -t palondomus/blacktechdivisionreward:$2 .
docker push palondomus/blacktechdivisionreward:$2
terraform init
terraform plan # -o
terraform apply -auto-approve
docker run -it -p 8080:8080 palondomus/blacktechdivisionreward:$2
