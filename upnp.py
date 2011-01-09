#!/usr/bin/env python
# encoding: utf-8
"""
upnp.py

Poor man's UPNP controller

Created by Rui Carmo on 2011-01-09
"""

import httplib, logging, cgi

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
</s:Envelope>""" }}

class UPNPDevice:
  def __init__(self, address):
    self.address = address
    self.connection = httplib.HTTPConnection(self.address)
    self.uri = "/MediaRenderer_AVTransport/control"
    
  def play(self, uri):
    uri = cgi.escape(uri)
    for command in ['SetAVTransportURI', 'Play']:
      self.conn.request("POST", self.uri, commands[command]['body'] % locals(), commands[command]['headers']).close()