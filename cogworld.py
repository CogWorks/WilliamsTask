import sys
import socket
import json

class CogWorld(object):
    """This is a simple class for connecting with CogWorld"""
    
    def __init__(self, host, port):
        super(CogWorld, self).__init__()
        self.host = host
        self.port = port
            
    def connect(self):
        ret = True
        for res in socket.getaddrinfo(self.host, self.port, socket.AF_UNSPEC, socket.SOCK_STREAM):
            af, socktype, proto, canonname, sa = res
            try:
                self.socket = socket.socket(af, socktype, proto)
            except socket.error, msg:
                ret = False
                continue
            try:
                self.socket.connect(sa)
            except socket.error, msg:
                self.socket.close()
                ret = False
                continue
            break
        return ret