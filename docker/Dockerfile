FROM easypi/alpine-arm:latest
MAINTAINER Yves Bovard <ybovard@gmail.com>

WORKDIR /root
ADD code /root

RUN apk update && apk upgrade \
    && apk add python3 python3-dev gcc musl-dev \
    && pip3 install -r requirements.txt \
    && python3 setup.py install

CMD [ "dnsupdate", "--foreground" ]
