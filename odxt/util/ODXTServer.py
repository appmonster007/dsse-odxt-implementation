import socketserver
import pickle
import logging
from datetime import datetime


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


class ODXTServer(socketserver.TCPServer):
    def __init__(self, addr, handler_class=serverReqHandler) -> None:
        self.EDB = None
        self.p = -1
        super().__init__(addr, handler_class)

    def Setup(self, res):
        self.EDB, self.p = res

    def Update(self, avax_tup):
        TSet, XSet = self.EDB
        addr, val, alpha, xtag = avax_tup
        TSet[addr] = (val, alpha)
        XSet[xtag] = 1
        self.EDB = (TSet, XSet)

    def Search(self, sxTokenList):
        TSet, XSet = self.EDB
        sEOpList = []
        for token in sxTokenList:
            cnt = 1
            sval, alpha = TSet[token[0]]
            for xt in token[1]:
                xtoken_ij = xt
                xtag_ij = pow(xtoken_ij, alpha, self.p)
                if(xtag_ij in XSet):
                    cnt += 1
            sEOpList.append((sval, cnt))
        return (sEOpList,)



class flexODXTServer(socketserver.TCPServer):
    def __init__(self, addr, handler_class=serverReqHandler) -> None:
        self.EDB = None
        self.p = -1
        super().__init__(addr, handler_class)

    def Setup(self, res):
        self.EDB, self.p = res

    def Update(self, avax_tup):
        TSet, XSet = self.EDB
        addr, val, alpha, xtag = avax_tup
        TSet[addr] = (val, alpha)
        XSet[xtag] = datetime.now()
        self.EDB = (TSet, XSet)

    def Search(self, sxTokenList):
        TSet, XSet = self.EDB
        sEOpList = []
        for token in sxTokenList:
            cnt_i = 1
            cnt_j = 0
            sval, alpha = TSet[token[0]]
            a, a_c = alpha
            for xt in token[1]:
                xtag_ij = pow(xt, a, self.p)
                xtag_ij_c = pow(xt, a_c, self.p)
                if(xtag_ij in XSet):
                    cnt_i += 1
                    if(xtag_ij_c in XSet and XSet[xtag_ij] < XSet[xtag_ij_c]):
                        cnt_j += 1
            sEOpList.append((sval, cnt_i, cnt_j))
        return (sEOpList,)
