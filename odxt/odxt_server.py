import sys
from util.ODXTServer import ODXTServer, flexODXTServer, serverReqHandler, serverReqHandler

HOST = 'localhost'
PORT = 50057

if __name__ == "__main__":
    HOST = sys.argv[1]
    PORT = int(sys.argv[2])
    server = ODXTServer((HOST, PORT), serverReqHandler)
    server.serve_forever()
