import functools, socket, pickle, sys
import dsse_util
from constants import HOST,PORT

class mitra_client:
    def __init__(self,socket_conn):
        self.sk = None
        self.st = None
        self.socket_conn = socket_conn
    
    #MITRA conj. Setup(λ)
    def Setup(self,λ):
        # 1. Sample a uniformly random key Kt for PRF F
        Kt = dsse_util.gen_key_F(λ)
        # 2. Initialize UpdateCnt; TSet to empty maps
        UpdateCnt, Tset = dict(),dict()
        # 3. Set sk = Kt and st = UpdateCnt
        self.sk,self.st = Kt, UpdateCnt
        # 4. Set EDB = TSet
        EDB = Tset
        # 5. Send EDB to the server
        self.socket_conn.send(pickle.dumps((0,EDB)))
    
    def Update(self,op,id_w_tuple):
        id,w = id_w_tuple
        # 1. Parse sk = Kt and st = UpdateCnt
        #already saved in object state
        # 2. If UpdateCnt[w] is NULL then set UpdateCnt[w] = 0
        if(not w in self.st):
            self.st[w]=0
        # 3. Set UpdateCnt[w] = UpdateCnt[w] + 1
        self.st[w]+=1
        # 4. Set addr = F(Kt,w||UpdateCnt[w]||0)
        addr = dsse_util.prf_F(self.sk,(str(w)+str(self.st[w])+str(0)).encode())
        # 5. Set val = (id||op) (xor) F(Kt,w||UpdateCnt[w]||1)
        val = dsse_util.bytes_XOR((str(id)+str(op)).encode(), dsse_util.prf_F(self.sk,(str(w)+str(self.st[w])+str(1)).encode()))
        # 6. Send (addr, val) to the server
        self.socket_conn.send(pickle.dumps((1,(addr,val))))
        print(addr,val)
    
    def Search(self,q):
        n=len(q)
        Kt = self.sk
        # 2. Initialize tokenList1; : : : ; tokenListn to empty lists
        tokenlists=[list()]*n
        # 3. For i = 1 to n:
        for i in range(n):
            wi = q[i]
            # (a) For j = 1 to UpdateCnt[wi]:
            for j in range(self.st[wi]):
                # i. Set addri;j = F(Kt ;wijjjjj0)
                addr_ij = dsse_util.prf_F(Kt,(str(wi)+str(j)+str(0)).encode())
                # ii. Set tokenListi = tokenListi [ faddri;jg
                tokenlists[i].append(addr_ij)
        # 5. Send tokenList1; : : : ; tokenListn to the server
        self.socket_conn.send(pickle.dumps((2,tokenlists)))
        #
        #SERVER WORK
        #

        resp_tup = pickle.loads(self.conn.recv(4096))
        #recieve from server
        EOpLists=resp_tup[0]
        #Initialize IdList1; : : : ; IdListn to empty lists
        IdLists = [list()]*n
        # 2. For i = 1 to n:
        for i in range(n):
            # (a) For j = 1 to UpdateCnt[wi]:
            for j in range(self.st[q[i]]):
                id,op = dsse_util.bytes_XOR(EOpLists[i][j], dsse_util.prf_F(Kt,(str(q[i])+str(j)+str(1)).encode()))
                # ii. If opi;j is add then set IdListi = IdListi [ fidi;jg
                if(op=='add'):
                    IdLists[i].append(id)
                # iii. Else set IdListi = IdListi n fidi;jg
                elif(op=='del'):
                    IdLists[i] = IdLists[i].remove(id) #unsure if this is correct
        # 4. Output IdList = \n i=1IdListi
        IdList = list(set(functools.reduce(lambda x,y: x+y, IdLists)))
        return IdList


if __name__ == "__main__":
    HOST = sys.argv[1]
    PORT = int(sys.argv[2])
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((HOST, PORT))
    client_obj = mitra_client(s)
    client_obj.Setup(100)
    print(client_obj.sk,client_obj.st)
    client_obj.Update('del',(1,"apple"))
    s.close()
    