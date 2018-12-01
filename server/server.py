import socket
import threading
import socketserver
import ml
from enum import Enum

messages = {}
timestamp = 0

class ServerException(Exception):
    pass

class Message():
    """docstring for Message"""
    def __init__(self, ID_from, ID_to, message, ts):
        self.ID_from = ID_from
        self.ID_to = ID_to
        self.message = message
        self.ts = ts

class MyTCPHandler(socketserver.BaseRequestHandler):

    class RequestType(Enum):
        NO_REQ = 0
        USER_INIT = 1
        SEND_MSG = 2
        GET_FROMTS = 3
        SEND_QUEST = 4

    def Process_USER_INIT(self):
        global messages
        pubksize = 2048
        got = self.request.recv(pubksize)
        if len(got) < pubksize:
            self.request.sendall(b'\x00\x0EBad PubK Size\x00')
            raise ServerException('Not enough bytes got')
        messages[int.from_bytes(got, byteorder='big')] = []
        self.request.sendall(b'\x01\x11Request Accepted\x00')

    def Process_SEND_MSG(self):
        global messages
        global timestamp
        ts = timestamp = timestamp + 1
        pubksize = 256

        got = self.request.recv(pubksize)
        if len(got) < pubksize:
            self.request.sendall(b'\x00\x0EBad PubK1Size\x00')
            raise ServerException('Not enough bytes got')
        ID_from = int.from_bytes(got, byteorder='big')

        got = self.request.recv(pubksize)
        if len(got) < pubksize:
            self.request.sendall(b'\x00\x0EBad PubK2Size\x00')
            raise ServerException('Not enough bytes got')
        ID_to = int.from_bytes(got, byteorder='big')

        got = self.request.recv(4)
        if len(got) < 4:
            self.request.sendall(b'\x00\x0EBad LengtSize\x00')
            raise ServerException('Not enough bytes got')
        msglen = int.from_bytes(got, byteorder='big')

        got = self.request.recv(msglen)
        if len(got) < msglen:
            self.request.sendall(b'\x00\x0EBad MessgSize\x00')
            raise ServerException('Not enough bytes got')
        msg = str(got, "utf-8")

        messages[ID_to].append(Message(ID_from, ID_to, msg, ts))
        self.request.sendall(b'\x01\x11Request Accepted\x00')

    def Process_GET_FROMTS(self):
        global messages
        pubksize = 256

        got = self.request.recv(pubksize)
        if len(got) < pubksize:
            self.request.sendall(b'\x00\x0EBad PubK2Size\x00')
            raise ServerException('Not enough bytes got')
        ID_to = int.from_bytes(got, byteorder='big')

        got = self.request.recv(8)
        if len(got) < 8:
            self.request.sendall(b'\x00\x0EBad TStmpSize\x00')
            raise ServerException('Not enough bytes got')
        ts = int.from_bytes(got, byteorder='big')

        if ID_to in messages:
            sz = len(messages[ID_to])
            needsz = True
            for mes in messages[ID_to]:
                if mes.ts < ts:
                    sz = sz - 1
                else:
                    if needsz:
                        self.request.sendall(sz.to_bytes(4, byteorder='big'))
                        needsz = False
                    self.request.sendall(mes.ID_from.to_bytes(pubksize, byteorder='big'))
                    self.request.sendall(len(mes.message).to_bytes(4, byteorder='big'))
                    self.request.sendall(mes.message.encode('utf-8'))
                    self.request.sendall(ts.to_bytes(4, byteorder='big'))
            if needsz:
                self.request.sendall(sz.to_bytes(4, byteorder='big'))
        else:
            self.request.sendall(b'\x00\x0EBad PubKeyVal\x00')
            raise ServerException('Bad pubk val')

    def Process_SEND_QUEST(self):
        pass        

    def handle(self):
        try:
            self.request.settimeout(5)
            got = self.request.recv(4)
            if len(got) < 4:
                self.request.sendall(b'\x00\x10Bad RequestType\x00')
                raise ServerException('Not enough bytes got')
            req_type_int = int.from_bytes(got, byteorder='big')
            try:
                req_type = self.RequestType(req_type_int)
            except ValueError:
                self.request.sendall(b'\x00\x10Bad RequestType\x00')
                raise ServerException('Bad RequestType')
            if req_type is self.RequestType.NO_REQ:
                self.request.sendall(b'\x01\x11Request Accepted\x00')
                return
            if req_type is self.RequestType.USER_INIT:
                self.Process_USER_INIT()

            if req_type is self.RequestType.SEND_MSG:
                self.Process_USER_INIT()
            
            if req_type is self.RequestType.GET_FROMTS:
                self.Process_USER_INIT()
            

        except (ServerException,
                socket.timeout,
                OSError) as e:
            print(e)

if __name__ == "__main__":
    HOST, PORT = "176.99.11.61", 13013

    # Create the server, binding to localhost on port 9999
    with socketserver.TCPServer((HOST, PORT), MyTCPHandler) as server:
        # Activate the server; this will keep running until you
        # interrupt the program with Ctrl-C
        server.serve_forever()















'''
class ThreadedTCPRequestHandler(socketserver.BaseRequestHandler):
    class RequestType(Enum):
        NO_REQ = 0
        USER_INIT = 1
        SEND_MSG = 2
        GET_FROMTS = 3
        SEND_QUEST = 4

    def Process_USER_INIT(self):
        pass

    def Process_SEND_MSG(self):
        pass

    def Process_GET_FROMTS(self):
        pass

    def Process_SEND_QUEST(self):
        pass        

    def handle(self):
        try:
            self.request.settimeout(5)
            got = self.request.recv(4)
            if len(got) < 4:
                raise ServerException('Not enough bytes got')
            req_type_int = int.from_bytes(got, byteorder='big')
            try:
                req_type = self.RequestType(req_type_int)
            except ValueError:
                self.request.sendall(b'\x00\x10Bad RequestType\x00')
                raise ServerException('Bad RequestType')
            if req_type is self.RequestType.NO_REQ:
                self.request.sendall(b'\x01\x11Request Accepted\x00')
                return
            if req_type is self.RequestType.USER_INIT:
                self.Process_USER_INIT()

            # data = str(self.request.recv(1024), 'ascii')
            #cur_thread = threading.current_thread()
            #response = bytes("{}: {}".format(cur_thread.name, data), 'ascii')
            #self.request.sendall(response)
        except (ServerException,
                socket.timeout,
                OSError) as e:
            print(e)

class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    pass

if __name__ == "__main__":
    # Port 0 means to select an arbitrary unused port
    HOST, PORT = "176.99.11.61", 13013

    server = ThreadedTCPServer((HOST, PORT), ThreadedTCPRequestHandler)
    with server:
        ip, port = server.server_address

        # Start a thread with the server -- that thread will then start one
        # more thread for each request
        server_thread = threading.Thread(target=server.serve_forever)
        # Exit the server thread when the main thread terminates
        server_thread.daemon = True
        server_thread.start()
        print("Server loop running in thread:", server_thread.name)
        
        a = 'str\n'
        input(a)

        server.shutdown()
'''