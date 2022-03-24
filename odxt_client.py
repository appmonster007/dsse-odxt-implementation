from pydoc import cli
from xmlrpc.client import MAXINT
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
        self.g = 65537

        # self.p = 69445180235231407255137142482031499329548634082242122837872648805446522657159
        # self.p = 14120496892714447199
        # self.p = 9803877828113247241079792513194491218341545278043756244841606553497839645277744524007466705683349057071449190848792221929552903517949301195746698367877099
        # self.p = 20963
        # self.g = 65537
        
        Kt = dsse_util.gen_key_F(λ)
        Kx = dsse_util.gen_key_F(λ)
        Ky = dsse_util.gen_key_F(λ)
        Kz = dsse_util.gen_key_F(λ)
        UpdateCnt, Tset, XSet = dict(),dict(), set()
        self.sk, self.st = (Kt, Kx, Ky, Kz), UpdateCnt
        EDB = (Tset, XSet)
        self.conn.send(pickle.dumps((0,(EDB, self.p))))
        if(pickle.loads(self.conn.recv(4096))==(1,)):
            print("Setup completed")
    
    def Update(self, op: str, id_w_tuple):
        id,w = id_w_tuple
        Kt, Kx, Ky, Kz = self.sk
        if(not w in self.st):
            self.st[w]=0
        self.st[w]+=1
        w_wc = str(w)+str(self.st[w])
        addr = dsse_util.prf_F(Kt,(w_wc+str(0)).encode())
        b1 = (str(op)+str(id)).encode()
        b2 = dsse_util.prf_F(Kt,(w_wc+str(1)).encode())
        val = dsse_util.bytes_XOR(b1, b2)
        A = int.from_bytes(dsse_util.prf_Fp(Ky, b1, self.p, self.g), 'little')
        B = int.from_bytes(dsse_util.prf_Fp(Kz,(w_wc).encode(), self.p, self.g), 'little')
        B_inv = dsse_util.mul_inv(B, self.p-1)
        C = int.from_bytes(dsse_util.prf_Fp(Kx, str(w).encode(), self.p, self.g), 'little')
        α = (A*B_inv)
        # print(f"B {B}\tBinv {B_inv}\t{w_wc, op, id, pow(self.g, B*B_inv, self.p)}")
        xtag = pow(self.g, C*A, self.p)
        # print(xtag)
        # print(w_wc, op, id)
        self.conn.send(pickle.dumps((1,(addr, val, α, xtag))))
        if(pickle.loads(self.conn.recv(4096))==(1,)):
            print("Update completed")
    
    def Search(self,q):
        n = len(q)
        Kt, Kx, Ky, Kz = self.sk
        # min_uc = np.argmin(np.array(list(self.st.values())))
        # w1_uc = list(self.st.values())[min_uc]
        # w1 = list(self.st.keys())[min_uc]
    
        w1_uc = MAXINT
        w1 = ""
        # print(self.st)
        for x in q:
            if x in self.st and self.st[x] < w1_uc:
                w1 = x
                # print(x)
                w1_uc = self.st[x]
        stokenlist = []
        # xtokenlists = [list()]*w1_uc
        xtokenlists = []
        # print(xtokenlists, w1_uc, n)
        if(w1 in self.st):
            for j in range(w1_uc):
                # print(2)
                saddr_j = dsse_util.prf_F(Kt, (str(w1)+str(j+1)+str(0)).encode())
                stokenlist.append(saddr_j)
                xtl = []
                B = int.from_bytes(dsse_util.prf_Fp(Kz,(str(w1)+str(j+1)).encode(), self.p, self.g), 'little')
                # print(f"B--{B}")
                for i in range(n):
                    # print(1, q[i], w1, q[i] != w1)
                    if(q[i] != w1):
                        A = int.from_bytes(dsse_util.prf_Fp(Kx,(str(q[i])).encode(), self.p, self.g), 'little')
                        # print(A,B)
                        xtoken = pow(self.g, A*B, self.p)
                        xtl.append(xtoken)
                random.shuffle(xtl)
                xtokenlists.append(xtl)
        # print(xtokenlists, w1_uc, n)
        res = (stokenlist, xtokenlists)
        # print(len(stokenlist), len(xtokenlists), len(xtokenlists[0]))
        self.conn.send(pickle.dumps((2,res)))
            
        #
        #SERVER WORK
        #
        resp_tup = pickle.loads(self.conn.recv(4096))
        sEOpList = resp_tup[0]
        IdList = []
        for l in sEOpList:
            # print(l)
            j,sval,cnt = l
            op_id = dsse_util.bytes_XOR(sval, dsse_util.prf_F(Kt, (str(w1)+str(j+1)+str(1)).encode()))
            # print(op_id)
            op_id = op_id.decode().rstrip('\x00')
            # print(op_id, op_id[3:], len(op_id), cnt)
            if(op_id[:3]=='add' and cnt==n):
                IdList.append(int(op_id[3:]))
                # print('+')
            elif(op_id[:3]=='del' and cnt>0 and int(op_id[3:]) in IdList):
                IdList.remove(int(op_id[3:]))
                # print('-')
        # print(self.st)
        print(list(set(IdList)))
        return list(set(IdList))


if __name__ == "__main__":
    HOST = sys.argv[1]
    PORT = int(sys.argv[2])
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((HOST, PORT))
    client_obj = odxt_client(s)
    client_obj.Setup(100)
    # print(client_obj.sk,client_obj.st)

    client_obj.Update('add',(2,"apple"))
    client_obj.Update('add',(4,"apple"))
    client_obj.Update('add',(5,"apple"))
    client_obj.Update('add',(6,"apple"))
    client_obj.Update('add',(7,"apple"))
    client_obj.Update('add',(8,"apple"))
    client_obj.Update('del',(7,"apple"))

    client_obj.Update('add',(3,"banana"))
    client_obj.Update('add',(4,"banana"))
    client_obj.Update('add',(5,"banana"))
    client_obj.Update('add',(6,"banana"))
    client_obj.Update('add',(7,"banana"))
    client_obj.Update('del',(4,"banana"))

    client_obj.Update('add',(3,"pincode"))
    client_obj.Update('add',(4,"pincode"))
    client_obj.Update('add',(5,"pincode"))
    client_obj.Update('add',(6,"pincode"))
    client_obj.Update('add',(7,"pincode"))
    client_obj.Update('del',(3,"pincode"))
    # print("Search for apple")
    # client_obj.Search(["apple"])
    # print("Search for banana")
    # client_obj.Search(["banana"])
    # print("Search for pincode")
    # client_obj.Search(["pincode"])
    print("Search for apple and banana")
    client_obj.Search(["apple", "banana"])
    print("Search for apple and pincode and banana")
    client_obj.Search(["apple", "pincode", "banana"])
    client_obj.conn.send(pickle.dumps(("q",)))
    s.close()
    