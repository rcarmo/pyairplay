#!/usr/bin/env python
# encoding: utf-8
"""
airplayer.py

Original concept by Pascal Widdershoven on 2010-12-19.
Wantonly modified by Rui Carmo on 2010-12-24 until it bore no resemblance whatsoever
to the original source code.
"""

import sys, thread, socket, signal, BaseHTTPServer, urlparse, logging, httplib, urllib
from bonjour import mdns
import upnp

log = logging.getLogger('bonjour.dns')
log.setLevel(logging.DEBUG)
h = logging.StreamHandler()
h.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s'))
log.addHandler(h)

def AirPlayCommand(command):
  def wrapper(r):
    log.debug(r.request_version)
    log.debug(r.command)
    log.debug(r.headers)
    if 'Content-Length' in r.headers:
      bytes = r.headers['Content-Length']
      if bytes:
        r.body = r.rfile.read(int(bytes))
    command(r)
  return wrapper

class AirPlayHandler(BaseHTTPServer.BaseHTTPRequestHandler):
  def do_GET(self):
    path = urlparse.urlparse(self.path)
    getattr(self,self.path[1:])()    
  
  def do_PUT(self):
    self.body = ''
    self.info = {}
    path = urlparse.urlparse(self.path)
    getattr(self,self.path[1:])()
  
  def do_POST(self):
    self.body = ''
    self.info = {}
    path = urlparse.urlparse(self.path)
    getattr(self,self.path[1:])()

  @AirPlayCommand
  def reverse(self):
    self.send_response(101)
    self.send_header('Upgrade', 'PTTH/1.0')
    self.send_header('Connection', 'Upgrade')
    self.end_headers()

  @AirPlayCommand
  def play(self):
    log.info(self.info)
    self.upnpdevice.play(self.info['Content-Location'])
    self.send_response(200)
    self.end_headers()

  @AirPlayCommand
  def stop(self):
    pass

  @AirPlayCommand
  def photo(self):
    self.send_response(200)
    self.end_headers()
    self.buffer = self.body
    self.upnpdevice.play('http://%s:%d/upnpviewimage' % (self.server.server_address[0],self.server.server_address[1]))

  @AirPlayCommand
  def scrub(self):
    pass

  @AirPlayCommand
  def rate(self):
    pass

  @AirPlayCommand
  def authorize(self):
    pass

  def upnpviewimage(self):
    self.send_response(200)
    self.send_header('Content-Type', 'image/jpeg')
    self.end_headers()
    self.wfile.write(self.buffer)
    
class Runner(object):
  
  def __init__(self, upnpdevice, port):
    self.port = port
    self.upnpdevice = upnpdevice
    self.ip = socket.gethostbyname(socket.gethostname())
    self.info = mdns.ServiceInfo("_airplay._tcp.local.", "Python._airplay._tcp.local.", socket.inet_aton(self.ip), self.port, 0, 0, {'path':'/'}, "Here.local")
    self.bonjour = mdns.Bonjour()
    
  def run(self, address):
    self.bonjour.registerService(self.info)
    httpd = BaseHTTPServer.HTTPServer((address, self.port), AirPlayHandler)
    AirPlayHandler.upnpdevice = self.upnpdevice
    try:
      httpd.serve_forever()
    except KeyboardInterrupt:
      self.bonjour.close()
  
  def receive_signal(self, signum, stack):
    self.bonjour.close()

def main(upnpdevice):  
  port = 6002 # TODO: remove these
  runner = Runner(upnpdevice, port)
  signal.signal(signal.SIGTERM, runner.receive_signal)
  try:
    runner.run('192.168.1.90') # TODO: remove these
  except Exception, e:  
    print e
    sys.exit(1)

if __name__ == '__main__':
  main(upnp.UPNPDevice("192.168.1.76:52932")) # TODO: UPNP autodetection
