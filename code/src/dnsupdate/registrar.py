import asyncio
import aiodns

class RegAbstract:
  CREDS=None
  NSLIST=[]

  @asyncio.coroutine
  def getIP(self,rrname,rrtype):
    pass
  def update(self,ipTuple):
    pass

class RegGandi(RegAbstract):
  @asyncio.coroutine
  def getIP(self,rrname,rrtype):
    resolvers=aiodns.DNSResolver()
    res=yield from asyncio.wait_for(resolvers.query(rrname,rrtype),timeout=5)
    return (rrtype,res[0].host)

  @asyncio.coroutine
  def update(self,ipTuple):
    pass
