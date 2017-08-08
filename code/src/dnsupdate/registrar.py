import asyncio

class RegAbstract:
  CREDS=None
  NSLIST=[]

  @asyncio.coroutine
  def getIP(self,rrtype):
    pass
  def update(self,ipTuple):
    pass

class RegGandi(RegAbstract):
  @asyncio.coroutine
  def getIP(self,rrtype):
    if rrtype=='A':
      return ('A','127.0.0.1')
    if rrtype=='AAAA':
      return ('AAAA','::1')

  @asyncio.coroutine
  def update(self,ipTuple):
    pass
