#!/bin/bash
function getVersions() {
    IN=$(cat main.tf | grep palondomus/blacktechdivisionreward)
    arrIN=(${IN//:/ })
    oldv=$((${arrIN[3]::-1}))
    newv=$(($oldv+1))
    echo $oldv $newv
}

# Change Docker tag in .tf
read -r oldv newv  <<< $(getVersions)
sed -i -e "s/blacktechdivisionreward:$oldv/blacktechdivisionreward:$newv/" main.tf



# Push Docker
docker build -t palondomus/blacktechdivisionreward:$newv .
docker push palondomus/blacktechdivisionreward:$newv

# Terraform Push Google Cloud
terraform init
terraform plan 
terraform apply -auto-approve

# Push Github
git add .
git commit -m "$1"
git push origin -u terraformbtd:terraformbtd

# Test application
docker run -it -p 8080:8080 palondomus/blacktechdivisionreward:$newv







