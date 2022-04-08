import sys
from util.ODXTServer import ODXTServer, ODXTServerV2, serverReqHandler, serverReqHandlerV2

HOST = 'localhost'
PORT = 50057

if __name__ == "__main__":
    HOST = sys.argv[1]
    PORT = int(sys.argv[2])
    server = ODXTServerV2((HOST, PORT), serverReqHandlerV2)
    server.serve_forever()
