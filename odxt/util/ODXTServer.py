import socketserver
import pickle
import logging


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
        addr, val, α, xtag = avax_tup
        TSet[addr] = (val, α)
        XSet.add(xtag)
        self.EDB = (TSet, XSet)

    def Search(self, tknlists):
        TSet, XSet = self.EDB
        stokenlist = tknlists[0]
        xtokenlists = tknlists[1]
        n = len(stokenlist)
        sEOpList = []
        for j in range(n):
            cnt = 1
            sval, α = TSet[stokenlist[j]]
            for xt in xtokenlists[j]:
                xtoken_ij = xt
                xtag_ij = pow(xtoken_ij, α, self.p)
                if(xtag_ij in XSet):
                    cnt += 1
            sEOpList.append((j, sval, cnt))
        return (sEOpList,)


class serverReqHandlerV2(socketserver.BaseRequestHandler):
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


class ODXTServerV2(socketserver.TCPServer):
    def __init__(self, addr, handler_class=serverReqHandlerV2) -> None:
        self.EDB = None
        self.p = -1
        super().__init__(addr, handler_class)

    def Setup(self, res):
        self.EDB, self.p = res

    def Update(self, avax_tup):
        TSet, XSet = self.EDB
        addr, val, α, xtag, upCnt = avax_tup
        TSet[addr] = (val, α)
        XSet[xtag] = upCnt
        self.EDB = (TSet, XSet)

    def Search(self, tknlists):
        TSet, XSet = self.EDB
        stokenlist = tknlists[0]
        xtokenlists = tknlists[1]
        n = len(stokenlist)
        sEOpList = []
        for j in range(n):
            cnt_i = 1
            cnt_j = 0
            sval, α_beta = TSet[stokenlist[j]]
            α, beta = α_beta
            for xt in xtokenlists[j]:
                xtoken_ij = xt
                xtag_ij = pow(xtoken_ij, α, self.p)
                xtag_ij_p = pow(xtag_ij, beta, self.p)
                if(xtag_ij in XSet):
                    cnt_i += 1
                    if(xtag_ij_p in XSet and XSet[xtag_ij] < XSet[xtag_ij_p]):
                        cnt_j += 1
            sEOpList.append((j, sval, cnt_i, cnt_j))
        return (sEOpList,)
