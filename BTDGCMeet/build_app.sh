
# Push Docker
docker build -t palondomus/btdgcmeet:latest -f BTDGCMeet.Dockerfile .
docker push palondomus/btdgcmeet:latest
docker run -it palondomus/btdgcmeet:latest

