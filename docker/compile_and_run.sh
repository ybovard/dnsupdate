#!/bin/sh

cd /opt/dnsauth/dnsupdate
ssh-agent bash -c 'ssh-add /opt/dnsauth/ansible/auth/gitlab; git pull'
docker build -t dnsupdate -f docker/Dockerfile .

docker run -t --name dnsupdate -v /opt/dnsauth/etc/dnsupdate.conf:/etc/dnsupdate/dnsupdate.conf dnsupdate
