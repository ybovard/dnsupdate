# Description
The goal of this project is to provide a daemon to get the public IP (IPv4 and IPv6) of the current host and to update the registrar if it provides an API

# Structure
* code: contains the python application
* docker: contains everything needed to make a docker container with this app

# Configuration
* /etc/dnsupdate/dnsupdate.conf
'''
[dnsupdate]
me: a.toto.ch # record
domain: toto.ch # domain name
refresh_rate: 3600 # number of second between checks

getA_class: l2io # object type for looking after the IPv4 address
getAAAA_class: l2io # object type for looking after the IPv6 address

registrar_class: <registrar> : class for the registrar

publisher_class: <publisher_class> # if publishing a message on a chat is needed, the type should be set here. If not, 'none'
publisher_creds: <my_creds>
publisher_dest: <dest_user>
'''
