import random, socket, pickle
import dsse_util
from constants import HOST,PORT

class mitra_client:
    def __init__(self,socket_conn):
        self.sk = None
        self.st = None
        self.UpdateCnt = None
        self.socket_conn = socket_conn
    
    #MITRA conj. Setup(λ)
    def Setup(self,λ):
        # 1. Sample a uniformly random key KT for PRF F
        KT = dsse_util.gen_key_F(λ)
        # 2. Initialize UpdateCnt; TSet to empty maps
        UpdateCnt, Tset = dict(),dict()
        # 3. Set sk = KT and st = UpdateCnt
        self.sk,self.st = KT, UpdateCnt
        # 4. Set EDB = TSet
        EDB = Tset
        # 5. Send EDB to the server
        self.socket_conn.send(pickle.dumps((EDB,)))
    
    def Update(self,op,id_w_tuple):
        id,w = id_w_tuple
        # 1. Parse sk = KT and st = UpdateCnt
        #already saved in object state
        # 2. If UpdateCnt[w] is NULL then set UpdateCnt[w] = 0
        if(self.UpdateCnt[w]==None):
            self.UpdateCnt[w]=0
        # 3. Set UpdateCnt[w] = UpdateCnt[w] + 1
        self.UpdateCnt[w]+=1
        # 4. Set addr = F(KT,w||UpdateCnt[w]||0)
        addr = dsse_util.prf_F(self.sk,(w+str(self.UpdateCnt[w])+str(0)))
        # 5. Set val = (id||op) (xor) F(KT,w||UpdateCnt[w]||1)
        val = dsse_util.bytes_XOR((str(id)+op).encode(),addr)
        # 6. Send (addr, val) to the server
        return (addr,val)
    
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
    HOST = 'localhost'
    PORT = 50007
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((HOST, PORT))
    client_obj = mitra_client(s)
    client_obj.Setup(100)
    print(client_obj.sk,client_obj.st)
    
    