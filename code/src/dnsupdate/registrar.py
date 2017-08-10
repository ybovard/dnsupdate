import asyncio
import aiodns
import xmlrpc.client
import logging


class RegAbstract:
  CREDS=None
  NSLIST=[]

  @asyncio.coroutine
  def getIP(self,rrname,rrtype):
    pass
  def update(self,ipTuple):
    pass



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


  @asyncio.coroutine
  def getIP(self,rrname,rrtype):
    try:
      resolvers=aiodns.DNSResolver()
      res=yield from asyncio.wait_for(resolvers.query(rrname,rrtype),timeout=5)
      rrval=res[0].host
    except aiodns.error.DNSError:
      rrval=''
    finally: 
      return (rrtype,rrval)


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
      raise ERR_GANDI_ZONE_LOCKED()
    

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

