import asyncio
import aiohttp
import json
import sys

class PubAbstract:
  CREDS=''
  HOST='test.toto.ch'
  DEST='dest'

  @asyncio.coroutine
  def publish(self,ipTuple):
    pass
   
class ERR_PUBGITTER_BAD_RESPONSE(Exception):
  pass


'''
publish nothing. Use for exemple when syslog message are enough

config parameters:
  publisher_class: none
'''
class PubNone(PubAbstract):
  @asyncio.coroutine
  def publish(self,ipTuple):
    raise NotImplementedError()


'''
Publish news on a gitter accout

config parameters:
  publisher_class: gitter
  publisher_creds: API secret key
  publisher_dest: name of the reciever
'''
class PubGitter(PubAbstract):
  _message=None

  @asyncio.coroutine
  def publish(self,ipTuple):
    if self._message is None:
      self._message={'message': '@{} {} changed public ip'.format(self.DEST,self.HOST)}
    with aiohttp.ClientSession() as session:
      rep=(yield from session.post(self.CREDS, json=self._message))
      try:
        s=(yield from rep.text())
        if s != 'OK':
          raise ERR_PUBGITTER_BAD_RESPONSE('recieved from Gitter response "{}"'.format(s))
      finally:
        if sys.exc_info()[0] is not None:
          # on exceptions, close the connection altogether
          rep.close()
        else:
          yield from rep.release()
      
