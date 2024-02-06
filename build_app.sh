#!/bin/bash
function getVersions() {
    IN=$(cat main.tf | grep palondomus/blacktechdivisionreward)
    arrIN=(${IN//:/ })
    oldv=$((${arrIN[3]::-1}))
    oldstr="blacktechdivisionreward:$oldv"
    newstr="blacktechdivisionreward:$(($oldv+1))"
    echo $oldstr $newstr
}

git add .
git commit -m "$1"
read -r oldstr newstr  <<< $(getVersions)
sed -i -e "s/$oldstr/$newstr/" main.tf
git push origin -u terraformbtd:terraformbtd
docker build -t palondomus/blacktechdivisionreward:$newv .
docker push palondomus/blacktechdivisionreward:$newv


terraform init
terraform plan 
terraform apply -auto-approve
docker run -it -p 8080:8080 palondomus/blacktechdivisionreward:$newv







