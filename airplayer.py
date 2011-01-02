#!/usr/bin/env python
# encoding: utf-8
"""
airplayer.py

Created by Pascal Widdershoven on 2010-12-19.
Modified by Rui Carmo on 2010-12-24
Copyright (c) 2010 P. Widdershoven. All rights reserved.
"""

import sys, thread, socket, signal, BaseHTTPServer, urlparse, logging, httplib, urllib
from bonjour import mdns

log = logging.getLogger('bonjour.dns')
log.setLevel(logging.DEBUG)
h = logging.StreamHandler()
h.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s'))
log.addHandler(h)

def UPNPCommand(url):
  conn = httplib.HTTPConnection("192.168.1.76:52932") # my WDTVLive
  headers = {'SOAPACTION': '"urn:schemas-upnp-org:service:AVTransport:1#SetAVTransportURI"'}
  request = """<?xml version="1.0" encoding="utf-8"?>
  <s:Envelope s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/" xmlns:s="http://schemas.xmlsoap.org/soap/envelope/">
    <s:Body>
      <u:SetAVTransportURI xmlns:u="urn:schemas-upnp-org:service:AVTransport:1">
        <InstanceID>0</InstanceID>
        <CurrentURI>%(url)s</CurrentURI>
        <CurrentURIMetaData />
      </u:SetAVTransportURI>
    </s:Body>
  </s:Envelope>""" % locals()
  conn.request("POST", "/MediaRenderer_AVTransport/control", request, headers)
  response = conn.getresponse()
  log.info(response.status)
  log.info(response.read())
  conn.close()

  conn = httplib.HTTPConnection("192.168.1.76:52932") # my WDTVLive
  headers = {'SOAPACTION': '"urn:schemas-upnp-org:service:AVTransport:1#Play"'}
  request = """<?xml version="1.0" encoding="utf-8"?>
  <s:Envelope s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/" xmlns:s="http://schemas.xmlsoap.org/soap/envelope/">
    <s:Body>
      <u:Play xmlns:u="urn:schemas-upnp-org:service:AVTransport:1">
        <InstanceID>0</InstanceID>
        <Speed>1</Speed>
      </u:Play>
    </s:Body>
  </s:Envelope>""" 
  conn.request("POST", "/MediaRenderer_AVTransport/control", request, headers)
  response = conn.getresponse()
  log.info(response.status)
  log.info(response.read())
  conn.close()
  

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
      except:
        pass
      log.debug(r.body)
    command(r)
  return wrapper

class AirPlayHandler(BaseHTTPServer.BaseHTTPRequestHandler):
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
    UPNPCommand(self.info['Content-Location'])
    self.send_response(200)

  @AirPlayCommand
  def stop(self):
    pass

  @AirPlayCommand
  def photo(self):
    pass

  @AirPlayCommand
  def scrub(self):
    pass

  @AirPlayCommand
  def rate(self):
    pass

  @AirPlayCommand
  def authorize(self):
    pass

    
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
