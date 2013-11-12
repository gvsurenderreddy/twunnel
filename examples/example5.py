import sys
import os
sys.path.insert(0, os.path.abspath(".."))

from twisted.internet import reactor, ssl
import logging
from twunnel import local
from example import example

logging.basicConfig(level=logging.DEBUG)

def install_DNS_RESOLVER():
    configuration = \
    {
        "DNS_RESOLVER":
        {
            "HOSTS":
            {
                "FILE": "example5/H.txt"
            },
            "SERVERS":
            [
                {
                    "ADDRESS": "8.8.8.8",
                    "PORT": 53
                },
                {
                    "ADDRESS": "8.8.4.4",
                    "PORT": 53
                }
            ]
        }
    }
    
    resolver = local.createResolver(configuration)
    
    reactor.installResolver(resolver)

def connect(port):
    factory = example.ProtocolFactory()
    factory.address = "www.google.com"
    factory.port = port
    
    configuration = \
    {
        "PROXY_SERVERS": []
    }
    
    contextFactory = None
    if factory.port == 443:
        contextFactory = ssl.ClientContextFactory()
    
    tunnel = local.createTunnel(configuration)
    tunnel.connect(factory.address, factory.port, factory, contextFactory)

reactor.callLater(0, install_DNS_RESOLVER)
reactor.callLater(5, connect, 80)
reactor.callLater(10, connect, 443)
reactor.callLater(15, reactor.stop)
reactor.run()