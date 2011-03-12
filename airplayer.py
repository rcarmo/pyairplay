#!/usr/bin/env python
# encoding: utf-8
"""
airplayer.py

Original concept by Pascal Widdershoven on 2010-12-19.
Wantonly modified by Rui Carmo on 2010-12-24 until it bore no resemblance whatsoever
to the original source code.
"""

import os, sys, thread, socket, signal, BaseHTTPServer, urlparse, logging, httplib, urllib
from bonjour import mdns
import upnp

log = logging.getLogger('bonjour.dns')
log.setLevel(logging.DEBUG)
h = logging.StreamHandler()
h.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s'))
log.addHandler(h)

photobuffer = ''

def AirPlayCommand(command):
  def wrapper(r):
    log.debug(r.request_version)
    log.debug(r.command)
    log.debug(r.headers)
    if 'Content-Length' in r.headers:
      bytes = r.headers['Content-Length']
      if bytes:
        r.body = r.rfile.read(int(bytes))
      try:
        lines = r.body.split('\n')
        for l in lines:
          (header, value) = l.split(': ',2)
          r.info[header] = value
        log.debug(r.info)
      except:
        pass
    command(r)
  return wrapper

def HTTPCommand(command):
  def wrapper(r):
    (r.schema,r.netloc,r.path,r.parameters,r.query,r.fragment) = urlparse.urlparse(urllib.unquote(r.path))
    command(r)
  return wrapper

class AirPlayHandler(BaseHTTPServer.BaseHTTPRequestHandler):

  @HTTPCommand
  def do_GET(self):
    getattr(self,(self.path[1:].split('/')[0]))()    
  """
  --- TV’s request
  HEAD /get/0$1$0$12/video.mpg HTTP/1.1
  getcontentFeatures.dlna.org: 1
  Pragma: getIfoFileURI.dlna.org
  transferMode.dlna.org: Streaming
  Host: 192.168.1.102:5001

  --- PMS response
  HTTP/1.1 200 OK
  Content-Type: video/mpeg
  Accept-Ranges: bytes
  Connection: keep-alive
  ContentFeatures.DLNA.ORG: DLNA.ORG_PN=MPEG_PS_PAL;DLNA.ORG_OP=01;DLNA.ORG_CI=0;DLNA.ORG_FLAGS=01700000000000000000000000000000
  TransferMode.DLNA.ORG: Streaming
  Server: Windows_XP-x86-5.1, UPnP/1.0, PMS/1.20
  Content-Length: 225261572
  """
  @HTTPCommand
  def do_HEAD(self):
    if 'getcontentFeatures.dlna.org' in self.headers:
      log.info("Replying to HEAD command")
      self.send_header('TransferMode.DLNA.ORG', 'Streaming')
      self.send_header('ContentFeatures.DLNA.ORG', 'DLNA.ORG_OP=01;DLNA.ORG_CI=0;DLNA.ORG_FLAGS=01700000000000000000000000000000')
      self.send_header('Last-Modified', self.date_time_string())
      self.send_header('Content-Length', str(len(photobuffer)))
      self.send_header('Content-Type', 'image/jpeg')
      self.send_response(200)
      self.end_headers()
  
  @HTTPCommand
  def do_PUT(self):
    self.body = ''
    self.info = {}
    getattr(self,(self.path[1:].split('/')[0]))()    
  
  @HTTPCommand
  def do_POST(self):
    self.body = ''
    self.info = {}
    getattr(self,(self.path[1:].split('/')[0]))()    

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
    photobuffer = self.body
    print len(photobuffer)
    self.upnpdevice.play('http://%s:%d/upnpviewimage/photobuffer.jpg' % (self.server.server_address[0],self.server.server_address[1]))

  @AirPlayCommand
  def scrub(self):
    pass

  @AirPlayCommand
  def rate(self):
    pass

  @AirPlayCommand
  def authorize(self):
    pass

  @AirPlayCommand
  def upnpviewimage(self):
    print len(buffer)
    self.send_response(200)
    self.send_header('Content-Type', 'image/jpeg')
    self.send_header('getcontentFeatures.dlna.org', '1')
    self.send_header('Content-Length', str(len(photobuffer)))
    self.end_headers()
    self.wfile.write(photobuffer)
    
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
