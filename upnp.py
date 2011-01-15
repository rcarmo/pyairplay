#!/usr/bin/env python
# encoding: utf-8
"""
upnp.py

Poor man's UPNP controller

Created by Rui Carmo on 2011-01-09
"""

import socket, logging, cgi

log = logging.getLogger('upnp')

commands = {
  'SetAVTransportURI': { 
    'headers': {'SOAPACTION': '"urn:schemas-upnp-org:service:AVTransport:1#SetAVTransportURI"'},
    'body': """<?xml version="1.0" encoding="utf-8"?>
<s:Envelope s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/" xmlns:s="http://schemas.xmlsoap.org/soap/envelope/">
  <s:Body>
    <u:SetAVTransportURI xmlns:u="urn:schemas-upnp-org:service:AVTransport:1">
      <InstanceID>0</InstanceID>
      <CurrentURI>%(uri)s</CurrentURI>
      <CurrentURIMetaData />
    </u:SetAVTransportURI>
  </s:Body>
</s:Envelope>""" },

  'Play': {
    'headers': {'SOAPACTION': '"urn:schemas-upnp-org:service:AVTransport:1#Play"'},
    'body': """<?xml version="1.0" encoding="utf-8"?>
<s:Envelope s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/" xmlns:s="http://schemas.xmlsoap.org/soap/envelope/">
  <s:Body>
    <u:Play xmlns:u="urn:schemas-upnp-org:service:AVTransport:1">
      <InstanceID>0</InstanceID>
      <Speed>1</Speed>
    </u:Play>
  </s:Body>
</s:Envelope>""" } }

def rawPost(address, uri, headers, data):
  (host, port) = address.split(':')
  s =  socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  s.connect((host, int(port)))
  headers['Content-Length'] = len(data)
  headers = ''.join(["%s: %s\r\n" % (h, headers[h]) for h in headers.keys()])
  print headers
  s.send("POST %(uri)s HTTP/1.0\r\n%(headers)s\r\n%(data)s" % locals())
  buffer = s.recv(1024)
  s.close()  
  return buffer

class UPNPDevice:
  def __init__(self, address):
    self.address = address
    #self.connection = httplib.HTTPConnection(self.address)
    self.uri = "/MediaRenderer_AVTransport/control"
    
  def play(self, uri):
    print uri
    for command in ['SetAVTransportURI', 'Play']:
      print rawPost(self.address, self.uri, commands[command]['headers'], commands[command]['body'] % locals())
      #self.conn.request("POST", self.uri, commands[command]['body'] % locals(), commands[command]['headers']).close()