import socket
import threading
import socketserver
from enum import Enum

class ServerException(Exception):
    pass


class ThreadedTCPRequestHandler(socketserver.BaseRequestHandler):
    class RequestType(Enum):
        NO_REQ = 0
        USER_INIT = 1
        SEND_MSG = 2
        GET_FROMTS = 3
        SEND_QUEST = 4

    def Process_USER_INIT(self, bo):
        pass

    def Process_SEND_MSG(self, bo):
        pass

    def Process_GET_FROMTS(self, bo):
        pass

    def Process_SEND_QUEST(self, bo):
        pass        

    def handle(self):
        try:
            self.request.settimeout(5)
            got = self.request.recv(4)
            if len(got) < 4:
                raise ServerException('Not enough bytes got')
            bo = 'big' if int.from_bytes(got, byteorder='big') == 1 else 'little'
            got = self.request.recv(4)
            if len(got) < 4:
                raise ServerException('Not enough bytes got')
            req_type_int = int.from_bytes(got, byteorder=bo)
            try:
                req_type = self.RequestType(req_type_int)
            except ValueError:
                self.request.sendall(b'\x00\x10Bad RequestType\x00')
                raise ServerException('Bad RequestType')
            if req_type is self.RequestType.NO_REQ:
                self.request.sendall(b'\x01\x11Request Accepted\x00')
                return
            if req_type is self.RequestType.USER_INIT:
                self.Process_USER_INIT(bo)

            # data = str(self.request.recv(1024), 'ascii')
            #cur_thread = threading.current_thread()
            #response = bytes("{}: {}".format(cur_thread.name, data), 'ascii')
            #self.request.sendall(response)
        except (ServerException,
                socket.timeout) as e:
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
