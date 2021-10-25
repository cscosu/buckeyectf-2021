FROM python:3-slim

RUN apt-get update && \
apt-get install -y xinetd python3 hashcash && \
rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY run.sh chall.py service.conf ./

CMD xinetd -filelog /dev/stderr -dontfork -f /app/service.conf
