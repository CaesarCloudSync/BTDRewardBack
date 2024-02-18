docker build -t palondomus/btdgcmeetsub:latest -f BTDGCMeetSub.Dockerfile .
docker push palondomus/btdgcmeetsub:latest
docker run -it palondomus/btdgcmeetsub:latest