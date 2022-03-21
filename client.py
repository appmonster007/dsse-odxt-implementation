import dsse_util
from Crypto.Util import number

class client:
    def __init__(self):
        self.sk = None
        self.st = None
        self.p = None
        self.g = None
        # self.UpdateCnt = None
    
    # ODXT Setup(λ)
    def Setup(self,λ):
        # 0. Set prime p and cyclic group generator g
        p = number.getPrime(256)
        while((g:=dsse_util.findPrimitive(p))==-1):
            p = number.getPrime(256)
        self.p = p
        self.g = g
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
        return EDB #change this to a socket send
    
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
        addr = dsse_util.ENC(self.sk,w)
        # 5. Set val = (id||op) (xor) F(KT,w||UpdateCnt[w]||1)
        val = dsse_util.xor(id,addr)
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