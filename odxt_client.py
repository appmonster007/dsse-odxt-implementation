import dsse_util, pickle, socket, sys, random
from Crypto.Util import number
import numpy as np
from constants import HOST,PORT

class odxt_client:
    def __init__(self, socket_conn):
        self.sk: tuple = ()
        self.st: dict = None
        self.p: int = -1
        self.g: int = -1
        self.conn = socket_conn
    
    # ODXT Setup(λ)
    def Setup(self, λ):
        # self.p = number.getPrime(16)
        # self.g = dsse_util.findPrimitive(self.p)
        self.p = 14466107790023157743
        self.g = 2
        Kt = dsse_util.gen_key_F(λ)
        Kx = dsse_util.gen_key_F(λ)
        Ky = dsse_util.gen_key_F(λ)
        Kz = dsse_util.gen_key_F(λ)
        UpdateCnt, Tset, XSet = dict(),dict(), set()
        self.sk, self.st = (Kt, Kx, Ky, Kz), UpdateCnt
        EDB = (Tset, XSet)
        self.conn.send(pickle.dumps((0,(EDB, self.p))))
    
    def Update(self, op: str, id_w_tuple):
        id,w = id_w_tuple
        Kt, Kx, Ky, Kz = self.sk
        if(not w in self.st):
            self.st[w]=0
        self.st[w]+=1
        w_wc = str(w)+str(self.st[w])
        addr = dsse_util.prf_F(Kt,(w_wc+str(0)).encode())
        b1 = (str(id)+str(op)).encode()
        b2 = dsse_util.prf_F(Kt,(w_wc+str(1)).encode())
        val = dsse_util.bytes_XOR(b1, b2)
        A = int.from_bytes(dsse_util.prf_Fp(Ky,(str(id)+str(op)).encode(), self.p), 'little')
        B = int.from_bytes(dsse_util.prf_Fp(Kz,(w_wc).encode(), self.p), 'little')
        B_inv = dsse_util.mul_inv(B, self.p-1)
        C = int.from_bytes(dsse_util.prf_Fp(Kx, str(w).encode(), self.p), 'little')
        α = A*B_inv
        xtag = pow(self.g, C*A, self.p)
        self.conn.send(pickle.dumps((1,(addr, val, α, xtag))))
    
    def Search(self,q):
        n=len(q)
        Kt, Kx, Ky, Kz = self.sk
        min_uc = np.argmin(np.array(list(self.st.values())))
        w1_uc = list(self.st.values())[min_uc]
        w1 = list(self.st.keys())[min_uc]
        stokenlist = []
        xtokenlists = [list()]*w1_uc
        for j in range(w1_uc):
            saddr_j = dsse_util.prf_F(Kt, (str(w1)+str(j)+str(0)).encode())
            stokenlist.append(saddr_j)
            for i in range(n):
                if(q[i] != w1):
                    A = int.from_bytes(dsse_util.prf_Fp(Kx,(str(q[i])).encode(), self.p), 'little')
                    B = int.from_bytes(dsse_util.prf_Fp(Kz,(str(w1)+str(j)).encode(), self.p), 'little')
                    xtoken = pow(self.g, A*B, self.p)
                    xtokenlists[j].append(xtoken)
            random.shuffle(xtokenlists[j])
        res = (stokenlist, xtokenlists)
        self.conn.send(pickle.dumps((2,res)))
            
        #
        #SERVER WORK
        #
        resp_tup = pickle.loads(self.conn.recv(4096))
        sEOpList = resp_tup[0]
        IdList = []
        for l in sEOpList:
            j,sval,cnt = sEOpList[l]
            id_op = dsse_util.bytes_XOR(sval, dsse_util.prf_F(Kt, (str(w1)+str(j)+str(1)).encode()))

            if(id_op[-3:]=='add' and cnt==n):
                IdList.append(int(id_op[:-3]))
            elif(id_op[-3:]=='del' and cnt>0):
                IdList.remove(int(id_op[:-3]))

        return list(set(IdList))


if __name__ == "__main__":
    HOST = sys.argv[1]
    PORT = int(sys.argv[2])
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((HOST, PORT))
    client_obj = odxt_client(s)
    client_obj.Setup(100)
    print(client_obj.sk,client_obj.st)
    client_obj.Update('update',(1,"apple"))
    s.close()
    