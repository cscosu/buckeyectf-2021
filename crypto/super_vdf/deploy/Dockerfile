FROM python:3-slim

RUN apt-get update && \
apt-get install -y gcc libmpc-dev socat && \
pip3 install --no-cache-dir gmpy2

WORKDIR /opt/app
COPY chall.py ./
CMD socat -d -d -s TCP-LISTEN:1024,reuseaddr,fork EXEC:'timeout 30 python -u /opt/app/chall.py'
