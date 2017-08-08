# dnsupdate code structure
## configuration file
'''
me: ns1.toto.ch.
refresh_rate: 300

getA_class: None
getAAAA_class: None

reg_class: 'gandi'
reg_creds: {}
reg_ns: []

publishNew_class: None
publishNew_auth: {}
'''

## code
* Techno used: python3 asyncio
* startup:
  [ ] prepare datastructure:
    [X] A if necessary
    [X] AAAA if necessary
    [ ] prepare connection to registrar
    [ ] prepare connection to publisher
    [X] look for current IP in reg_ns
  [X] loop every refresh_rate seconds
  [ ] asynchronously look for:
    [ ] current A rec in getA_class
    [ ] current AAAA rec in getAAAA_class
  [X] update datastructure
  [ ] if new addresses:
    [ ] update registrar
    [ ] publish info
