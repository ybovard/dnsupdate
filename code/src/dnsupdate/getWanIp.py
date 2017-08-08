import asyncio

class GetIPAbstract:
  RRNAME='toto.ch'
  RRTYPE='A'

  @asyncio.coroutine
  def get(self):
    pass

class GetIPL2IO(GetIPAbstract):
  @asyncio.coroutine
  def get(self):
    if self.RRTYPE=='A':
      return (self.RRTYPE,'127.0.0.2')
    if self.RRTYPE=='AAAA':
      return (self.RRTYPE,'::2')
