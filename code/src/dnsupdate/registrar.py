import asyncio
import aiodns
import xmlrpc.client
import logging

'''
In case of an address change, they could be directly changed on the registrar. This class should be sub-classed for each registrar
'''
class RegAbstract:
  CREDS=None
  NSLIST=[]

  def update(self,ipTuple):
    pass

'''
Used when no registrar update are necessary

config parameters:
  registrar_class: none
'''
class RegNone(RegAbstract):
  @asyncio.coroutine
  def update(self,ipTuple):
    raise NotImplementedError()


'''
Change IPs on Gandi web site

config parameters:
  registrar_class: gandi
  registrar_creds: credentials for the API
  registrar_ns: a.reg.ch,b.reg.ch
  gandi_zonefile_name: zone file to change
'''
class ERR_GANDI_ZONE_NOT_FOUND(Exception):
  pass
class ERR_GANDI_ZONE_LOCKED(Exception):
  pass

class RegGandi(RegAbstract):
  ZONEFILE_NAME=''
  DOMAIN=''
  _api=None
  _url='https://rpc.gandi.net/xmlrpc/'
  _zoneFileId=-1


  def setup(self):
    self._api = xmlrpc.client.ServerProxy(self._url)
    self._zoneFileId=self._getZoneId(self.ZONEFILE_NAME)


  def _getZoneId(self, zoneFileName):
    zones = self._api.domain.zone.list(self.CREDS)
    for z in zones:
      if z['name'] == zoneFileName:
        return z['id']
    raise ERR_GANDI_ZONE_NOT_FOUND()


  def _getNewVersion(self):
    versionList = self._api.domain.zone.version.list(self.CREDS, self._zoneFileId)
    zoneInfo = self._api.domain.zone.info(self.CREDS, self._zoneFileId)
    lastVersionNum=-1
    for zfv in versionList:
      tmp=int(zfv['id'])
      if tmp > lastVersionNum:
        lastVersionNum=tmp

    if lastVersionNum == int(zoneInfo['version']):
      return self._api.domain.zone.version.new(self.CREDS, self._zoneFileId)
    else:
      raise ERR_GANDI_ZONE_LOCKED('zone {} found but {} is active'.format(lastVersionNum,zoneInfo['version']))

  @asyncio.coroutine
  def update(self,ipTuple):
    if self._api is None:
      self.setup()
    
    try:
      zfv=self._getNewVersion()
    except ERR_GANDI_ZONE_LOCKED:
      logging.warning("a newer zone exists but is not active. Waiting 10sec")
      yield from asyncio.sleep(10)
      zfv=self._getNewVersion()
    
    for ip in ipTuple:
      host=ip[0].replace('.{}'.format(self.DOMAIN),'')
      self._api.domain.zone.record.delete(self.CREDS, self._zoneFileId, zfv, { "type" : ip[1], "name" : host })
      self._api.domain.zone.record.add(self.CREDS, self._zoneFileId, zfv, { "type" : ip[1], "name": host, "value": ip[2] })

    self._api.domain.zone.version.set(self.CREDS, self._zoneFileId, zfv)

