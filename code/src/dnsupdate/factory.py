from .exceptions import UNKNOWN_REGISTRAR
from .exceptions import UNKNOWN_PUBLISHER
from .exceptions import UNKNOWN_GETA
from .exceptions import UNKNOWN_GETAAAA

class Factory:
  def getRegistrar(self,config):
    if config['dnsupdate']['registrar_class'] == 'gandi':
      from .registrar import RegGandi
      obj=RegGandi()
      obj.CREDS=config['dnsupdate']['registrar_creds']
      obj.NSLIST=config['dnsupdate']['registrar_ns'].split(',')
      obj.ZONEFILE_NAME=config['dnsupdate']['gandi_zonefile_name']
      obj.DOMAIN=config['dnsupdate']['domain']
    elif config['dnsupdate']['registrar_class'] == 'none':
      from .registrar import RegNone
      obj=RegNone()
    else:
      raise UNKNOWN_REGISTRAR('unknown registrar {}'.format(config['dnsupdate']['registrar_class']))
    return obj

  def getPublisher(self,config):
    if config['dnsupdate']['publisher_class'] == 'gitter':
      from .publisher import PubGitter
      obj=PubGitter()
      obj.CREDS=config['dnsupdate']['publisher_creds']
      obj.HOST=config['dnsupdate']['me']
      obj.DEST=config['dnsupdate']['publisher_dest']
    elif config['dnsupdate']['publisher_class'] == 'none':
      from .publisher import PubNone
      obj=PubNone()
    else:
      raise UNKNOWN_PUBLISHER('unknown publisher {}'.format(config['dnsupdate']['publisher_class']))
    return obj
    
  def getWANIP(self,config):
    obj=[]
    if config['dnsupdate']['geta_class'] == 'l2io':
      from .getWanIp import GetIPL2IO
      tmp=GetIPL2IO()
      tmp.RRNAME=config['dnsupdate']['me']
      tmp.RRTYPE='A'
      obj.append(tmp) 
    elif config['dnsupdate']['geta_class'] == '':
      pass
    else:
      raise UNKNOWN_GETA('unknown getter class for A record {}'.format(config['dnsupdate']['geta_class']))

    if config['dnsupdate']['getaaaa_class'] == 'l2io':
      from .getWanIp import GetIPL2IO
      tmp=GetIPL2IO()
      tmp.RRNAME=config['dnsupdate']['me']
      tmp.RRTYPE='AAAA'
      obj.append(tmp) 
    elif config['dnsupdate']['getaaaa_class'] == '':
      pass
    else:
      raise UNKNOWN_GETA('unknown getter class for AAAA record {}'.format(config['dnsupdate']['getaaaa_class']))

    return obj

