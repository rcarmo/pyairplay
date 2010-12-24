#!/usr/bin/env python
# encoding: utf-8
"""
airplayer.py

Created by Pascal Widdershoven on 2010-12-19.
Modified by Rui Carmo on 2010-12-24
Copyright (c) 2010 P. Widdershoven. All rights reserved.
"""

import sys, thread, socket, signal, BaseHTTPServer, urlparse, logging
from bonjour import mdns


log = logging.getLogger('bonjour.dns')
h = logging.StreamHandler()
h.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s'))
log.addHandler(h)
log.setLevel(logging.debug)

class AirPlayHandler(BaseHTTPServer.BaseHTTPRequestHandler):
  def do_GET(self):
    path = urlparse.urlparse(self.path)
    log.info("Got %s" % self.path)
    result = {
      "/reverse": self.cmd_reverse,
      "/play": self.cmd_play, 
      "/scrub": self.cmd_scrub,
      "/rate": self.cmd_rate,
      "/photo": self.cmd_photo,
      "/stop": self.cmd_stop
    }[path]
    
class Runner(object):
  
  def __init__(self, port):
    self.port = port
    self.ip = socket.gethostbyname(socket.gethostname())
    self.info = mdns.ServiceInfo("_airplay._tcp.local.", "Python._airplay._tcp.local.", socket.inet_aton(self.ip), self.port, 0, 0, {'path':'/'}, "Here.local")
    self.bonjour = mdns.Bonjour()
    
  def run(self):
    self.bonjour.registerService(self.info)
    httpd = BaseHTTPServer.HTTPServer(('', self.port), AirPlayHandler)
    try:
      httpd.serve_forever()
    except KeyboardInterrupt:
      self.bonjour.close()
  
  def receive_signal(self, signum, stack):
    self.bonjour.close()

def main():  
  runner = Runner(6002)
  signal.signal(signal.SIGTERM, runner.receive_signal)
  try:
    runner.run()
  except Exception, e:  
    print e
    sys.exit(1)

if __name__ == '__main__':
  main()
