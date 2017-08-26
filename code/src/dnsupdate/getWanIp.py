import asyncio
import socket
import aiohttp
import async_timeout

from .exceptions import UNKNOWN_RRTYPE

class GetIPAbstract:
  RRNAME='toto.ch'
  RRTYPE='A'

  @asyncio.coroutine
  def get(self):
    pass

class GetIPL2IO(GetIPAbstract):
  URL='https://l2.io/ip'

  @asyncio.coroutine
  def get(self):
    if self.RRTYPE=='A':
      conn=aiohttp.TCPConnector(family=socket.AF_INET, verify_ssl=True)
    elif self.RRTYPE=='AAAA':
      conn=aiohttp.TCPConnector(family=socket.AF_INET6, verify_ssl=True)
    else:
      raise UNKNOWN_RRTYPE('only A and AAAA are allowed here, but {} recieved'.format(self.RRTYPE))
    with aiohttp.ClientSession(connector=conn) as session:
      with async_timeout.timeout(10):
        html=yield from session.get(self.URL)
        return (self.RRTYPE,(yield from html.text()))
