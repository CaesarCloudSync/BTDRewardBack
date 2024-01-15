git add .
git commit -m "$1"
git push origin master:master
docker build -t palondomus/blacktechdivisionreward:finest .
docker push palondomus/blacktechdivisionreward:finest
docker run -it -p 8080:8080 palondomus/blacktechdivisionreward:finest