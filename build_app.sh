git add .
git commit -m "$1"
git push origin master:master
docker build -t palondomus/blacktechdivisionreward:kartra_inbound .
docker push palondomus/blacktechdivisionreward:kartra_inbound
docker run -it -p 8080:8080 palondomus/blacktechdivisionreward:kartra_inbound