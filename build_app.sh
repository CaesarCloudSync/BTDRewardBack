git add .
git commit -m "$1"
git push origin master:master
docker build -t palondomus/blacktechdivisionreward:latest .
docker push palondomus/blacktechdivisionreward:latest
docker run -it -p 8080:8080 palondomus/blacktechdivisionreward:latest