#!/bin/bash
git add .
git commit -m "$1"
git push origin -u terraformbtd:terraformbtd
docker build -t palondomus/blacktechdivisionreward:bestest .
docker push palondomus/blacktechdivisionreward:bestest
terraform destroy
terraform init
terraform plan # -o
url=$($(terraform apply) | grep blacktechdivisionreward)
echo $url
curl "${url/service_url = /""}"  
#docker run -it -p 8080:8080 palondomus/blacktechdivisionreward:bestest
