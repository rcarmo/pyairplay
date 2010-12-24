#!/usr/bin/env python
# encoding: utf-8
"""
airplayer.py

Created by Pascal Widdershoven on 2010-12-19.
Modified by Rui Carmo on 2010-12-24
Copyright (c) 2010 P. Widdershoven. All rights reserved.
"""

import sys, thread, socket, signal, BaseHTTPServer

class AirPlayHandler(BaseHTTPServer.BaseHTTPRequestHandler):

  def __init__(self):
    pass

class Runner(object):
  
  def __init__(self, port):
    self.port = port
    self ip = socket.gethostbyname(socket.gethostname())
    self.info = new bonjour.dns.ServiceInfo("_airplay._tcp", "Python", socket.inet_aton(self.ip), self.port)
    self.bonjour = new bonjour.mdns.Bonjour()
    self.web = None
    
  def _start_web(self):
    self.web = Webserver(self.port)
    self.web.start()
    
  def run(self):
    self.bonjour.registerService(self.info)
    httpd = BaseHTTPServer(('', self.port), AirPlayHandler)
    while True: # prepare for conditional exiting
      httpd.handle_request()
  
  def receive_signal(self, signum, stack):
    self.web.stop()
    self.xbmc.stop_playing()

def main():  
  runner = Runner(6002)
  signal.signal(signal.SIGTERM, runner.receive_signal)
  
  try:
    runner.run()
  except Exception, e:  
    print 'Unable to connect to XBMC at %s' % runner.xbmc._host_string()
    print e
    sys.exit(1)

if __name__ == '__main__':
  main()
