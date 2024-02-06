#!/bin/bash
function getVersions() {
    IN=$(cat main.tf | grep palondomus/blacktechdivisionreward)
    arrIN=(${IN//:/ })
    oldv=$((${arrIN[3]::-1}))
    newv=$(($oldv+1))
    echo $oldv $newv
}

git add .
git commit -m "$1"
read -r oldv newv  <<< $(getVersions)
sed -i -e "s/blacktechdivisionreward:$oldv/blacktechdivisionreward:$newv/" main.tf
git push origin -u terraformbtd:terraformbtd
docker build -t palondomus/blacktechdivisionreward:$newv .
docker push palondomus/blacktechdivisionreward:$newv


terraform init
terraform plan 
terraform apply -auto-approve
docker run -it -p 8080:8080 palondomus/blacktechdivisionreward:$newv







