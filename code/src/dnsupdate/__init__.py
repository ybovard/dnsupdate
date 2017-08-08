import logging.config
from .daemon import Daemon

import sys
import time
import signal
import logging
import argparse
import traceback
if sys.version_info[0] == 2:
  import ConfigParser as CP
else:
  import configparser as CP

from logging.handlers import SysLogHandler
from .factory import Factory
import asyncio

class CurrentIP(object):
  RRTYPE=None
  RRNAME=None
  RRVALUE=None

  def update(self,val):
    rc=True
    if val==self.RRVALUE:
      rc=False
    else:
      self.RRVALUE=val
    return rc


class Controller(object):
    _loop=None
    _registrar=None
    _publisher=None
    _currentIPClass=None
    _currentIP=None

    def __init__(self,config):
        self.config=config
        self.stay_alive=True
        
        
    def reload(self):
        ##TODO: PUT CODE HERE THAT SHOULD BE EXECUTED ON SIGHUP ##
        ## the new config is set already from the start script
        logging.info("Reloading dnsupdate")
        
    
    @asyncio.coroutine
    def pretasks(self):
        pretasks=[]
        self._currentIP=[]
        for ipClass in self._currentIPClass:
          pretasks.append(self._registrar.getIP(ipClass.RRTYPE))
          ip=CurrentIP()
          ip.RRTYPE=ipClass.RRTYPE
          ip.RRNAME=ipClass.RRNAME
          self._currentIP.append(ip)

        completed, pending = yield from asyncio.wait(pretasks)
        for t in pending:
          logging.warning("task {} not completed".format(t))
          
        for t in completed:
          res=t.result()
          for ip in self._currentIP:
            if ip.RRTYPE==res[0]:
              logging.info("initialize current {} to {}".format(res[0], res[1]))
              ip.update(res[1])
          

    @asyncio.coroutine
    def mainloop(self):
        while self.stay_alive:
          tasks=[]
          for ipClass in self._currentIPClass:
            tasks.append(ipClass.get())
          completed, pending = yield from asyncio.wait(tasks)
          for t in pending:
            logging.warning("task {} not completed".format(t))
          for t in completed:
            res=t.result()
            changed=False
            for ip in self._currentIP:
              if ip.RRTYPE==res[0]:
                if ip.update(res[1]):
                  logging.info("{} has been updated to {}".format(res[0], res[1]))
                  changed=True
                else:
                  logging.info("no change found for {}".format(res[0]))
          if changed:
            ipTuple=[]
            for ip in self._currentIP:
              ipTuple.append((ip.RRTYPE,ip.RRVALUE))
            completed, pending = yield from asyncio.wait([self._registrar.update(ipTuple)])
            if len(pending) == 0 :
              logging.info("registrar updated")
              completed, pending = yield from asyncio.wait([self._publisher.publish(ipTuple)])
              if len(pending) == 0 :
                logging.info("news published")
              else:
                logging.warning("news cannot be published")
            else:
              logging.warning("registrar cannot be updated")


          time.sleep(float(CONTROLLER.config['dnsupdate']['refresh_rate']))


    def run(self):
        logging.debug('configuration loaded')
        for sec in CONTROLLER.config.sections():
          logging.debug('{: <2s}{}'.format(' ',sec))
          for opt,val in CONTROLLER.config[sec].items():
            logging.debug('{: <4s}{}: {}'.format(' ',opt,val))

        facto=Factory()
        self._registrar=facto.getRegistrar(CONTROLLER.config)
        self._publisher=facto.getPublisher(CONTROLLER.config)
        self._currentIPClass=facto.getWANIP(CONTROLLER.config)

        logging.debug('registrar controller loaded: {}'.format(self._registrar.__class__.__name__))
        logging.debug('publisher controller loaded: {}'.format(self._publisher.__class__.__name__))
        logging.debug('currentIP datastructure loaded: {}'.format(self._currentIPClass))
    
        ## main looap of the program
        self._loop=asyncio.get_event_loop()
        try:
          self._loop.run_until_complete(self.pretasks())
          self._loop.run_until_complete(self.mainloop())
        except KeyboardInterrupt:
          self.stay_alive=False
        finally:
          self._shutdown()
                
    
    def shutdown(self):
        self._shutdown()
    
    def _shutdown(self):
        logging.info("dnsupdate shutting down")
        self._loop.close()
        
    





CONFIGFILE="/etc/dnsupdate/dnsupdate.conf"
CONTROLLER=None

def init_syslog_logging(level=logging.INFO):
    """initialize logging"""
    #logging.basicConfig(level=loglevel)
    logger = logging.getLogger()
    logger.setLevel(level)
    slh=SysLogHandler(address = '/dev/log')
    slh.setFormatter(logging.Formatter("dnsupdate[%(process)d]: %(message)s"))
    #log debug/error messages to syslog info level
    slh.priority_map["DEBUG"]="info"
    slh.priority_map["ERROR"]="info"

    slh.setLevel(level)
    logger.addHandler(slh)
    return logger

def reload_config():
    """reload configuration"""
    newconfig=CP.ConfigParser()
    newconfig.readfp(open(CONFIGFILE))
    return newconfig


def sighup(signum,frame):
    """handle sighup to reload config"""
    newconfig=reload_config()
    if CONTROLLER!=None:
        CONTROLLER.config=newconfig

    CONTROLLER.reload()

def sigterm(signum,frame):
    CONTROLLER.shutdown()

def main():
    global CONFIGFILE,CONTROLLER

    parser = argparse.ArgumentParser()
    parser.add_argument("-f","--foreground",action="store_true",dest="foreground",default=False,help="do not fork to background")
    parser.add_argument("--pidfile",action="store",dest="pidfile")
    parser.add_argument("-c","--config",action="store",dest="config",help="configfile",default="/etc/dnsupdate/dnsupdate.conf")
    parser.add_argument("--log-config",action="store",dest="logconfig",help="logging configuration file")
    parser.add_argument("--user",action="store",dest="user", help="run as user")
    parser.add_argument("--group",action="store",dest="group", help="run as group")

    opts = parser.parse_args()

    #keep a copy of stderr in case something goes wrong
    stderr=sys.stderr
    try:
        daemon=Daemon(opts.pidfile)
        if not opts.foreground:
            daemon.daemonize()
        CONFIGFILE=opts.config
        config=reload_config()

        #drop privileges
        daemon.drop_privileges(opts.user,opts.group)

        if opts.logconfig:
            logging.config.fileConfig(opts.logconfig)

        if opts.foreground:
            #log to console
            if not opts.logconfig:
                logging.basicConfig(level=logging.DEBUG,format='%(asctime)s %(levelname)s %(message)s')
        else:
            #log to syslog
            if not opts.logconfig:
                init_syslog_logging()
            signal.signal(signal.SIGHUP, sighup)
            signal.signal(signal.SIGTERM, sigterm)

        logging.info("dnsupdate starting up...")

        CONTROLLER=Controller(config)
        CONTROLLER.run()

        logging.info("dnsupdate shut down")
    except Exception:
        exc=traceback.format_exc()
        errtext="Unhandled exception in main thread: \n %s \n"%exc
        stderr.write(errtext)
        logging.error(errtext)



