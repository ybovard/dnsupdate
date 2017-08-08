import asyncio
class PubAbstract:
  CREDS=''

  @asyncio.coroutine
  def publish(self,ipTuple):
    pass
   

class PubGitter(PubAbstract):
  pass
