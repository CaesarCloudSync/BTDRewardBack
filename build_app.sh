git add .
git commit -m "$1"
git push origin master:master
docker build -t palondomus/blacktechdivisionreward:bestest .
docker push palondomus/blacktechdivisionreward:bestest
docker run -it -p 8080:8080 palondomus/blacktechdivisionreward:bestest