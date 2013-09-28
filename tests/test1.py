# -*- coding: utf-8 -*-

import sys
import os
sys.path.insert(0, os.path.abspath(".."))

from twisted.internet import protocol
from twisted.trial import unittest
from twisted.test import proto_helpers
import base64
import struct
import socket
from twunnel import local

class TestTunnelProtocol(protocol.Protocol):
    def __init__(self):
        pass
        
    def connectionMade(self):
        pass
        
    def connectionLost(self, reason):
        pass
        
    def dataReceived(self, data):
        pass
        
    def tunnelOutputProtocol_connectionMade(self, data):
        pass

class HTTPTunnelTestCase(unittest.TestCase):
    def setUp(self):
        self.configuration = \
        {
            "PROXY_SERVERS": 
            [
                {
                    "TYPE": "HTTP",
                    "ADDRESS": "127.0.0.1",
                    "PORT": 8080,
                    "ACCOUNT": 
                    {
                        "NAME": "",
                        "PASSWORD": ""
                    }
                }
            ]
        }
        self.remoteAddress = "127.0.0.1"
        self.remotePort = 80
        
        self.protocolFactory = local.HTTPTunnelOutputProtocolFactory(0, self.configuration, self.remoteAddress, self.remotePort, TestTunnelProtocol())
        self.protocolFactory.protocol = local.HTTPTunnelOutputProtocol
        self.protocol = self.protocolFactory.buildProtocol((self.remoteAddress, self.remotePort))
        self.transport = proto_helpers.StringTransport()
        self.protocol.makeConnection(self.transport)
        
    def tearDown(self):
        self.transport.loseConnection()
        
    def test(self):
        value = self.transport.value()
        self.transport.clear()
        
        self.assertEqual(value, "CONNECT %s:%d HTTP/1.0\r\n\r\n" % (self.remoteAddress, self.remotePort))
        
        self.protocol.dataReceived("HTTP/1.0 200 OK\r\n\r\n")

class HTTPTunnelBasicAuthenticationTestCase(unittest.TestCase):
    def setUp(self):
        self.configuration = \
        {
            "PROXY_SERVERS": 
            [
                {
                    "TYPE": "HTTP",
                    "ADDRESS": "127.0.0.1",
                    "PORT": 8080,
                    "ACCOUNT": 
                    {
                        "NAME": "1",
                        "PASSWORD": "2"
                    }
                }
            ]
        }
        self.remoteAddress = "127.0.0.1"
        self.remotePort = 80
        
        self.protocolFactory = local.HTTPTunnelOutputProtocolFactory(0, self.configuration, self.remoteAddress, self.remotePort, TestTunnelProtocol())
        self.protocolFactory.protocol = local.HTTPTunnelOutputProtocol
        self.protocol = self.protocolFactory.buildProtocol((self.remoteAddress, self.remotePort))
        self.transport = proto_helpers.StringTransport()
        self.protocol.makeConnection(self.transport)
        
    def tearDown(self):
        self.transport.loseConnection()
        
    def test(self):
        value = self.transport.value()
        self.transport.clear()
        
        self.assertEqual(value, "CONNECT %s:%d HTTP/1.0\r\nProxy-Authorization: Basic %s\r\n\r\n" % (self.remoteAddress, self.remotePort, base64.standard_b64encode("%s:%s" % (self.configuration["PROXY_SERVERS"][0]["ACCOUNT"]["NAME"], self.configuration["PROXY_SERVERS"][0]["ACCOUNT"]["PASSWORD"]))))
        
        self.protocol.dataReceived("HTTP/1.0 200 OK\r\n\r\n")

class SOCKS5TunnelIPv4TestCase(unittest.TestCase):
    def setUp(self):
        self.configuration = \
        {
            "PROXY_SERVERS": 
            [
                {
                    "TYPE": "SOCKS5",
                    "ADDRESS": "127.0.0.1",
                    "PORT": 1080,
                    "ACCOUNT": 
                    {
                        "NAME": "",
                        "PASSWORD": ""
                    }
                }
            ]
        }
        self.remoteAddress = "127.0.0.1"
        self.remotePort = 80
        
        self.protocolFactory = local.SOCKS5TunnelOutputProtocolFactory(0, self.configuration, self.remoteAddress, self.remotePort, TestTunnelProtocol())
        self.protocolFactory.protocol = local.SOCKS5TunnelOutputProtocol
        self.protocol = self.protocolFactory.buildProtocol((self.remoteAddress, self.remotePort))
        self.transport = proto_helpers.StringTransport()
        self.protocol.makeConnection(self.transport)
        
    def tearDown(self):
        self.transport.loseConnection()
        
    def test(self):
        value = self.transport.value()
        self.transport.clear()
        
        v, c, r = struct.unpack('!BBB', value[:3])
        
        self.assertEqual(v, 0x05)
        self.assertEqual(c, 0x01)
        self.assertEqual(r, 0x00)
        
        value = struct.pack('!BB', 0x05, 0x00)
        
        self.protocol.dataReceived(value)
        
        value = self.transport.value()
        self.transport.clear()
        
        v, c, r, remoteAddressType = struct.unpack('!BBBB', value[:4])
        
        self.assertEqual(v, 0x05)
        self.assertEqual(c, 0x01)
        self.assertEqual(r, 0x00)
        self.assertEqual(remoteAddressType, 0x01)
        
        remoteAddress, remotePort = struct.unpack('!IH', value[4:10])
        remoteAddress = socket.inet_ntoa(struct.pack('!I', remoteAddress))
        
        self.assertEqual(remoteAddress, self.remoteAddress)
        self.assertEqual(remotePort, self.remotePort)
        
        value = struct.pack('!BBBBIH', 0x05, 0x00, 0x00, 0x01, 0, 0)
        
        self.protocol.dataReceived(value)

class SOCKS5TunnelDNTestCase(unittest.TestCase):
    def setUp(self):
        self.configuration = \
        {
            "PROXY_SERVERS": 
            [
                {
                    "TYPE": "SOCKS5",
                    "ADDRESS": "127.0.0.1",
                    "PORT": 1080,
                    "ACCOUNT": 
                    {
                        "NAME": "",
                        "PASSWORD": ""
                    }
                }
            ]
        }
        self.remoteAddress = "localhost"
        self.remotePort = 80
        
        self.protocolFactory = local.SOCKS5TunnelOutputProtocolFactory(0, self.configuration, self.remoteAddress, self.remotePort, TestTunnelProtocol())
        self.protocolFactory.protocol = local.SOCKS5TunnelOutputProtocol
        self.protocol = self.protocolFactory.buildProtocol((self.remoteAddress, self.remotePort))
        self.transport = proto_helpers.StringTransport()
        self.protocol.makeConnection(self.transport)
        
    def tearDown(self):
        self.transport.loseConnection()
        
    def test(self):
        value = self.transport.value()
        self.transport.clear()
        
        v, c, r = struct.unpack('!BBB', value[:3])
        
        self.assertEqual(v, 0x05)
        self.assertEqual(c, 0x01)
        self.assertEqual(r, 0x00)
        
        value = struct.pack('!BB', 0x05, 0x00)
        
        self.protocol.dataReceived(value)
        
        value = self.transport.value()
        self.transport.clear()
        
        v, c, r, remoteAddressType = struct.unpack('!BBBB', value[:4])
        
        self.assertEqual(v, 0x05)
        self.assertEqual(c, 0x01)
        self.assertEqual(r, 0x00)
        self.assertEqual(remoteAddressType, 0x03)
        
        remoteAddressLength = ord(value[4])
        remoteAddress, remotePort = struct.unpack('!%dsH' % remoteAddressLength, value[5:])
        
        self.assertEqual(remoteAddress, self.remoteAddress)
        self.assertEqual(remotePort, self.remotePort)
        
        value = struct.pack('!BBBBIH', 0x05, 0x00, 0x00, 0x01, 0, 0)
        
        self.protocol.dataReceived(value)

if __name__ == "__main__":
    unittest.main()