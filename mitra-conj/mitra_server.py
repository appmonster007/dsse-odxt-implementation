import pickle
import sys
import logging
import socketserver


HOST = 'localhost'
PORT = 50007

logging.basicConfig(level=logging.INFO)


class serverReqHandler(socketserver.BaseRequestHandler):
    def __init__(self, request, addr, server):
        super().__init__(request, addr, server)

    def handle(self):
        resp_tup = pickle.loads(self.request.recv(4096))
        if(resp_tup[0] == 0):  # for setup
            self.server.Setup(resp_tup[1])
            data = (1,)
            logging.debug("setup completed")
        elif(resp_tup[0] == 1):
            self.server.Update(resp_tup[1])
            data = (1,)
            logging.debug("update completed")
        elif(resp_tup[0] == 2):
            data = self.server.Search(resp_tup[1])
            logging.debug("search completed")

        self.request.sendall(pickle.dumps(data))
        logging.debug('handled')


class mitra_server(socketserver.TCPServer):
    def __init__(self, addr, handler_class=serverReqHandler) -> None:
        self.EDB = None
        super().__init__(addr, handler_class)

    def Setup(self, EDB):
        self.EDB = EDB

    def Update(self, addr_val_tup):
        addr, val = addr_val_tup
        self.EDB[addr] = val

    def Search(self, Tokenlists):
        EOpLists = []
        for tknl_i in Tokenlists:
            EOPL_i = []
            for tknl_ij in tknl_i:
                val_ij = self.EDB[tknl_ij]
                EOPL_i.append(val_ij)
            EOpLists.append(EOPL_i)
        return (EOpLists,)


if __name__ == "__main__":
    HOST = sys.argv[1]
    PORT = int(sys.argv[2])
    server = mitra_server((HOST, PORT), serverReqHandler)
    server.serve_forever()
