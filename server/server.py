import socketserver

class MyTCPHandler(socketserver.BaseRequestHandler):
    """
    The request handler class for our server.

    It is instantiated once per connection to the server, and must
    override the handle() method to implement communication to the
    client.
    """

    def handle(self):
        # self.request is the TCP socket connected to the client
        #bo = 'big' if int.from_bytes(self.request.recv(4), byteorder='big') == 1 else 'little'
        self.data = self.request.recv(1024).strip()
        print("{} wrote:".format(self.client_address[0]))
        print(self.data)
        # just send back the same data, but upper-cased
        #self.request.sendall(self.data.upper())
        
        # just send back the same data, but upper-cased
        self.request.sendall(self.data.upper())

#def 

if __name__ == "__main__":
    HOST, PORT = "176.99.11.61", 13013

    # Create the server, binding to localhost on port 9999
    with socketserver.TCPServer((HOST, PORT), MyTCPHandler) as server:
        # Activate the server; this will keep running until you
        # interrupt the program with Ctrl-C
        server.serve_forever()
