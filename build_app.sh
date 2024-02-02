git add .
git commit -m "$1"
git push origin authidkartra:authidkartra
docker build -t palondomus/blacktechdivisionreward:authidkartra .
docker push palondomus/blacktechdivisionreward:authidkartra
docker run -it -p 8080:8080 palondomus/blacktechdivisionreward:authidkartra