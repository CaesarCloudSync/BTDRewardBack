docker build -t palondomus/caesaraicronemail:latest .
docker push palondomus/caesaraicronemail:latest
docker run -it -p 8080:8080 palondomus/caesaraicronemail:latest