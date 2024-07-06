import functools
import socket
import pickle
import sys
import logging
from util import dsse_util

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)

MAXINT = sys.maxsize
HOST = 'localhost'
PORT = 50007


class mitra_client:
    def __init__(self, addr):
        self.sk: bytes = None
        self.st: dict = None
        self.addr = addr

    def Setup(self, l):
        Kt = dsse_util.gen_key_F(l)
        UpdateCnt, Tset = dict(), dict()
        self.sk, self.st = Kt, UpdateCnt
        EDB = Tset
        conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        conn.connect(self.addr)
        conn.send(pickle.dumps((0, EDB)))
        data = pickle.loads(conn.recv(4096))
        # log.info(f"setup{data}")
        # if(data == (1,)):
        #     log.info("Setup completed")
        conn.close()

    def Update(self, op, id_w_tuple):
        id, w = id_w_tuple
        if(not w in self.st):
            self.st[w] = 0
        self.st[w] += 1
        addr = dsse_util.prf_F(
            self.sk, (str(w)+str(self.st[w])+str(0)).encode())
        val = dsse_util.bytes_XOR((str(op)+str(id)).encode(), dsse_util.prf_F(
            self.sk, (str(w)+str(self.st[w])+str(1)).encode()))
        conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        conn.connect(self.addr)
        conn.send(pickle.dumps((1, (addr, val))))
        data = pickle.loads(conn.recv(1024))
        # log.info(f"setup{data}")
        # if(data == (1,)):
        #     log.info("Update completed")
        conn.close()

    def Search(self, q):
        n = len(q)
        tokenlists = []
        for x in q:
            tknli = []
            for j in range(1,self.st[x]+1):
                addr_ij = dsse_util.prf_F(self.sk, (str(x)+str(j)+str(0)).encode())
                tknli.append(addr_ij)
            tokenlists.append(tknli)
        conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        conn.connect(self.addr)
        conn.send(pickle.dumps((2, tokenlists)))

        #
        # SERVER WORK
        #

        resp_tup = pickle.loads(conn.recv(4096))
        EOpLists = resp_tup[0]
        IdLists = []
        for i in range(n):
            idl = []
            for j in range(self.st[q[i]]):
                op_id = dsse_util.bytes_XOR(EOpLists[i][j], dsse_util.prf_F(
                    self.sk, (str(q[i])+str(j+1)+str(1)).encode()))
                op_id = op_id.decode().rstrip('\x00')
                if(op_id[:3] == 'add'):
                    idl.append(int(op_id[3:]))
                elif(op_id[:3] == 'del'):
                    idl.remove(int(op_id[3:]))
            IdLists.append(idl) 
        IdList = list(set(functools.reduce(lambda x, y: list(set(x).intersection(set(y))), IdLists)))
        log.info(sorted(IdList))
        conn.close()
        return IdLists


if __name__ == "__main__":
    HOST = sys.argv[1]
    PORT = int(sys.argv[2])
    client_obj = mitra_client((HOST, PORT))
    client_obj.Setup(100)
    # log.info(client_obj.sk,client_obj.st)

    client_obj.Update('add', (2, "apple"))
    client_obj.Update('add', (4, "apple"))
    client_obj.Update('add', (5, "apple"))
    client_obj.Update('add', (6, "apple"))
    client_obj.Update('add', (7, "apple"))
    client_obj.Update('add', (8, "apple"))
    client_obj.Update('del', (7, "apple"))
    client_obj.Update('add', (7, "apple"))

    client_obj.Update('add', (3, "banana"))
    client_obj.Update('add', (4, "banana"))
    client_obj.Update('add', (5, "banana"))
    client_obj.Update('add', (6, "banana"))
    client_obj.Update('add', (7, "banana"))
    client_obj.Update('del', (4, "banana"))

    client_obj.Update('add', (3, "pincode"))
    client_obj.Update('add', (4, "pincode"))
    client_obj.Update('add', (5, "pincode"))
    client_obj.Update('add', (6, "pincode"))
    client_obj.Update('add', (7, "pincode"))
    client_obj.Update('del', (3, "pincode"))
    log.info("Search for apple")
    client_obj.Search(["apple"])
    log.info("Search for banana")
    client_obj.Search(["banana"])
    log.info("Search for pincode")
    client_obj.Search(["pincode"])
    log.info("Search for apple and banana")
    client_obj.Search(["apple", "banana"])
    log.info("Search for apple and pincode")
    client_obj.Search(["apple", "pincode"])
    log.info("Search for apple and pincode and banana")
    client_obj.Search(["apple", "pincode", "banana"])