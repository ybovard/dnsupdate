#!/bin/sh

cd /opt/dnsauth/dnsupdate
ssh-agent bash -c 'ssh-add /opt/dnsauth/ansible/auth/gitlab; git pull'
docker build -t dnsupdate -f docker/Dockerfile .

docker container ls|grep dnsupdate
if [ $? -eq 0 ]; then
  docker stop dnsupdate
  docker rm dnsupdate
fi

docker run -d -t --name dnsupdate -v /opt/dnsauth/etc/dnsupdate.conf:/etc/dnsupdate/dnsupdate.conf dnsupdate
