git add .
git commit -m "$1"
git push origin blacktechinviteafriend:blacktechinviteafriend
docker build -t palondomus/blacktechdivisionreward:latest .
docker push palondomus/blacktechdivisionreward:latest
docker run -it -p 8080:8080 palondomus/blacktechdivisionreward:latest