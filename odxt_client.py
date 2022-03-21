import dsse_util, pickle, socket
from Crypto.Util import number
from constants import HOST,PORT

class odxt_client:
    def __init__(self, socket_conn):
        self.sk = None
        self.st = None
        self.p = None
        self.g = None
        self.conn = socket_conn
        # self.UpdateCnt = None
    
    # ODXT Setup(λ)
    def Setup(self, λ):
        # 0. Set prime p and cyclic group generator g
        # self.p = number.getPrime(16)
        # self.g = dsse_util.findPrimitive(self.p)
        self.p = 14466107790023157743
        self.g = 2
        # 1. Sample a uniformly random key KT for PRF F
        # Kt = dsse_util.GEN(λ)
        Kt = dsse_util.gen_key_F(λ)
        # 2. Sample uniformly random keys Kx, Ky, Kz for PRF Fp
        Kx = dsse_util.gen_key_F(λ)
        Ky = dsse_util.gen_key_F(λ)
        Kz = dsse_util.gen_key_F(λ)
        # 3. Initialize UpdateCnt; TSet to empty maps
        UpdateCnt, Tset, XSet = dict(),dict(), dict()
        # 4. Set sk = (Kt, Kx, Ky, Kz) and st = UpdateCnt
        self.sk, self.st = (Kt, Kx, Ky, Kz), UpdateCnt
        # 5. Set EDB = TSet
        EDB = (Tset, XSet)
        # 6. Send EDB to the server
        self.conn.send(pickle.dumps((0,EDB)))
    
    def Update(self, op: str, id_w_tuple):
        id,w = id_w_tuple
        Kt, Kx, Ky, Kz = self.sk
        # 1. Parse sk = KT and st = UpdateCnt
        #already saved in object state
        # 2. If UpdateCnt[w] is NULL then set UpdateCnt[w] = 0
        if(not w in self.st):
            self.st[w]=0
        # 3. Set UpdateCnt[w] = UpdateCnt[w] + 1
        self.st[w]+=1
        # 4. Set addr = F(KT,w||UpdateCnt[w]||0)
        addr = dsse_util.prf_F(Kt,(w+str(self.st[w])+str(0)).encode())
        # 5. Set val = (id||op) (xor) F(KT,w||UpdateCnt[w]||1)
        val = dsse_util.bytes_XOR((str(id)+str(op)).encode(), dsse_util.prf_F(Kt,(str(w)+str(self.st[w])+str(1)).encode()))
        # 6. Send (addr, val) to the server
        A = int.from_bytes(dsse_util.prf_Fp(Ky,(str(id)+str(op)).encode(), self.p), 'little')
        B = int.from_bytes(dsse_util.prf_Fp(Kz,(str(w)+str(self.st[w])).encode(), self.p), 'little')
        print(B)
        B_inv = dsse_util.mul_inv(B, self.p-1)
        C = int.from_bytes(dsse_util.prf_Fp(Kx, str(w).encode(), self.p), 'little')

        alpha = A*B_inv
        xtag = pow(self.g, C*A, self.p)
        self.conn.send(pickle.dumps((addr,val, alpha, xtag)))
        print()
    
    def Search(self,q):
        n=len(q)
        # 2. Initialize tokenList1; : : : ; tokenListn to empty lists
        tokenlists=[list() for word in range(n)]
        # 3. For i = 1 to n:
        for i in range(n):
            wi = q[i]
            # (a) For j = 1 to UpdateCnt[wi]:
            for j in range(self.UpdateCnt[wi]):
                # i. Set addri;j = F(KT ;wijjjjj0)
                addr = dsse_util.ENC(self.sk,wi)
                # ii. Set tokenListi = tokenListi [ faddri;jg
                tokenlists[i].append(addr)
        # 5. Send tokenList1; : : : ; tokenListn to the server

        #
        #SERVER WORK
        #

        #recieve from server
        EOpLists=[]
        #Initialize IdList1; : : : ; IdListn to empty lists
        IdLists = [list() for word in range(n)]
        # 2. For i = 1 to n:
        for i in range(n):
            # (a) For j = 1 to UpdateCnt[wi]:
            for j in range(self.UpdateCnt):
                id,op = dsse_util.xor(EOpLists[j],dsse_util.ENC(q[i]))
                # ii. If opi;j is add then set IdListi = IdListi [ fidi;jg
                if(op=='add'):
                    IdLists[i].append(id)
                # iii. Else set IdListi = IdListi n fidi;jg
                elif(op=='update'):
                    IdLists[i] = IdLists[i]/id #unsure if this is correct
        # 4. Output IdList = \n i=1IdListi
        return list(set.intersection(*IdLists))


if __name__ == "__main__":
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((HOST, PORT))
    client_obj = odxt_client(s)
    client_obj.Setup(100)
    print(client_obj.sk,client_obj.st)
    client_obj.Update('update',(1,"apple"))
    s.close()
    