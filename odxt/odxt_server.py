import sys, logging
from util.ODXTServer import ODXTServer, flexODXTServer, serverReqHandler, serverReqHandler

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)

HOST = 'localhost'
PORT = 50057

if __name__ == "__main__":
    HOST = sys.argv[1]
    PORT = int(sys.argv[2])
    server = flexODXTServer((HOST, PORT), serverReqHandler)
    server.serve_forever()
