import pickle
import socket
import random
import sys
from .ODXTutil import *

MAXINT = sys.maxsize


class ODXTClient:
    def __init__(self, addr):
        self.sk: tuple = ()
        self.st: dict = {}
        self.p: int = -1
        self.g: int = -1
        self.addr = addr
        self.upCnt = 0

    # ODXT Setup(λ)
    def Setup(self, λ):
        # self.p = number.getPrime(16)
        # self.g = findPrimitive(self.p)

        self.p = 69445180235231407255137142482031499329548634082242122837872648805446522657159
        self.g = 65537

        Kt = gen_key_F(λ)
        Kx = gen_key_F(λ)
        Ky = gen_key_F(λ)
        Kz = gen_key_F(λ)
        UpdateCnt, Tset, XSet = dict(), dict(), set()
        self.sk, self.st = (Kt, Kx, Ky, Kz), UpdateCnt
        EDB = (Tset, XSet)
        conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        conn.connect(self.addr)
        conn.send(pickle.dumps((0, (EDB, self.p))))
        data = pickle.loads(conn.recv(4096))
        # if(data == (1,)):
        #     print("Setup completed")
        conn.close()

    def Update(self, op: str, id, w):
        Kt, Kx, Ky, Kz = self.sk
        if(not w in self.st):
            self.st[w] = 0
        self.st[w] += 1
        w_wc = str(w)+str(self.st[w])
        addr = prf_F(Kt, (w_wc+str(0)).encode())
        b1 = (str(op)+str(id)).encode()
        b2 = prf_F(Kt, (w_wc+str(1)).encode())
        val = bytes_XOR(b1, b2)
        A0 = prf_Fp(Ky, b1, self.p, self.g)
        A = int.from_bytes(A0, 'little')
        B0 = prf_Fp(Kz, (w_wc).encode(), self.p, self.g)
        B = int.from_bytes(B0, 'little')
        B_inv = mul_inv(B, self.p-1)
        C0 = prf_Fp(Kx, str(w).encode(), self.p, self.g)
        C = int.from_bytes(C0, 'little')
        alpha = (A*B_inv)
        xtag = pow(self.g, C*A, self.p)
        conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        conn.connect(self.addr)
        conn.send(pickle.dumps((1, (addr, val, alpha, xtag))))
        data = pickle.loads(conn.recv(1024))
        # if(data == (1,)):
        #     print("Update completed")
        conn.close()

    def Search(self, q):
        n = len(q)
        Kt, Kx, Ky, Kz = self.sk
        w1_uc = MAXINT
        w1 = ""
        for x in q:
            if x in self.st and self.st[x] < w1_uc:
                w1 = x
                w1_uc = self.st[x]
        stokenlist = []
        xtokenlists = []
        if(w1 in self.st):
            for j in range(w1_uc):
                saddr_j = prf_F(
                    Kt, (str(w1)+str(j+1)+str(0)).encode())
                stokenlist.append(saddr_j)
                xtl = []
                B0 = prf_Fp(
                    Kz, (str(w1)+str(j+1)).encode(), self.p, self.g)
                B = int.from_bytes(B0, 'little')
                for i in range(n):
                    if(q[i] != w1):
                        A0 = prf_Fp(
                            Kx, (str(q[i])).encode(), self.p, self.g)
                        A = int.from_bytes(A0, 'little')
                        xtoken = pow(self.g, A*B, self.p)
                        xtl.append(xtoken)
                random.shuffle(xtl)
                xtokenlists.append(xtl)
        res = (stokenlist, xtokenlists)
        conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        conn.connect(self.addr)
        conn.send(pickle.dumps((2, res)))

        #
        # SERVER WORK
        #

        resp_tup = pickle.loads(conn.recv(4096))
        sEOpList = resp_tup[0]
        IdList = []
        for l in sEOpList:
            j, sval, cnt = l
            X0 = prf_F(Kt, (str(w1)+str(j+1)+str(1)).encode())
            op_id = bytes_XOR(sval, X0)
            op_id = op_id.decode().rstrip('\x00')
            if(op_id[:3] == 'add' and cnt == n):
                IdList.append(int(op_id[3:]))
            elif(op_id[:3] == 'del' and cnt > 0 and int(op_id[3:]) in IdList):
                IdList.remove(int(op_id[3:]))
        print(list(set(IdList)))
        conn.close()
        return list(set(IdList))

    def close_server(self):
        conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        conn.connect(self.addr)
        conn.send(pickle.dumps(("q",)))
        conn.close()


class flexODXTClient:
    def __init__(self, addr):
        self.sk: tuple = ()
        self.st: dict = {}
        self.p: int = -1
        self.g: int = -1
        self.addr = addr
        self.upCnt = 0

        self.opConj = {
            "add" : "del",
            "del" : "add"
        }

    def Setup(self, λ):
        # self.p = number.getPrime(16)
        # self.g = findPrimitive(self.p)

        self.p = 69445180235231407255137142482031499329548634082242122837872648805446522657159

        self.g = 65537

        Kt = gen_key_F(λ)
        Kx = gen_key_F(λ)
        Ky = gen_key_F(λ)
        Kz = gen_key_F(λ)
        UpdateCnt, Tset, XSet = dict(), dict(), dict()
        self.sk, self.st = (Kt, Kx, Ky, Kz), UpdateCnt
        EDB = (Tset, XSet)
        conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        conn.connect(self.addr)
        conn.send(pickle.dumps((0, (EDB, self.p))))
        data = pickle.loads(conn.recv(4096))
        # if(data == (1,)):
        #     print("Setup completed")
        conn.close()

    def Update(self, op: str, id, w):
        self.upCnt += 1
        Kt, Kx, Ky, Kz = self.sk
        if(not w in self.st):
            self.st[w] = 0
        self.st[w] += 1
        w_wc = str(w)+str(self.st[w])
        addr = prf_F(Kt, (w_wc+str(0)).encode())
        b1 = (str(op)+str(id)).encode()
        b1_c = (str(self.opConj[op])+str(id)).encode()
        b2 = prf_F(Kt, (w_wc+str(1)).encode())
        val = bytes_XOR(b1, b2)
        val_c = bytes_XOR(b1_c, b2)
        A = int.from_bytes(prf_Fp(Ky, b1, self.p, self.g), 'little')
        A_c = int.from_bytes(prf_Fp(Ky, b1_c, self.p, self.g), 'little')
        B = int.from_bytes(prf_Fp(Kz, (w_wc).encode(), self.p, self.g), 'little')
        B_inv = mul_inv(B, self.p-1)
        C = int.from_bytes(prf_Fp(Kx, str(w).encode(), self.p, self.g), 'little')
        alpha = (A*B_inv)
        alpha_c = (A_c*B_inv)
        xtag = pow(self.g, C*A, self.p)
        xtag_c = pow(self.g, C*A_c, self.p)
        conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        conn.connect(self.addr)
        conn.send(pickle.dumps((1, (addr, val_c, (alpha_c, alpha), xtag_c))))
        data = pickle.loads(conn.recv(1024))
        conn.close()

        conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        conn.connect(self.addr)
        conn.send(pickle.dumps((1, (addr, val, (alpha, alpha_c), xtag))))
        data = pickle.loads(conn.recv(1024))
        # if(data == (1,)):
        #     print("Update completed")
        conn.close()

    def Search(self, q):
        n = len(q)
        Kt, Kx, Ky, Kz = self.sk
        w1_uc = MAXINT
        w1 = ""
        for x in q:
            if x in self.st and self.st[x] < w1_uc:
                w1 = x
                w1_uc = self.st[x]
        sxTokenList = []
        if(w1 in self.st):
            for j in range(w1_uc):
                saddr_j = prf_F(
                    Kt, (str(w1)+str(j+1)+str(0)).encode())
                xtl = []
                B0 = prf_Fp(
                    Kz, (str(w1)+str(j+1)).encode(), self.p, self.g)
                B = int.from_bytes(B0, 'little')
                for i in range(n):
                    if(q[i] != w1):
                        A0 = prf_Fp(
                            Kx, (str(q[i])).encode(), self.p, self.g)
                        A = int.from_bytes(A0, 'little')
                        xtoken = pow(self.g, A*B, self.p)
                        xtl.append(xtoken)
                random.shuffle(xtl)
                sxTokenList.append((saddr_j, xtl))
        res = sxTokenList
        conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        conn.connect(self.addr)
        conn.send(pickle.dumps((2, res)))

        #
        # SERVER WORK
        #

        resp_tup = pickle.loads(conn.recv(4096))
        sEOpList = resp_tup[0]
        IdList = []
        for l in sEOpList:
            j, sval, cnt_i, cnt_j = l
            X0 = prf_F(Kt, (str(w1)+str(j+1)+str(1)).encode())
            op_id = bytes_XOR(sval, X0)
            op_id = op_id.decode().rstrip('\x00')
            if(op_id[:3] == 'add' and cnt_i == n and cnt_j == 0):
                IdList.append(int(op_id[3:]))
            elif(op_id[:3] == 'del' and cnt_i > 0 and int(op_id[3:]) in IdList):
                IdList.remove(int(op_id[3:]))
        print(list(set(IdList)))
        conn.close()
        return list(set(IdList))

    def close_server(self):
        conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        conn.connect(self.addr)
        conn.send(pickle.dumps(("q",)))
        conn.close()
