from http import server
import pickle, sys
import random, socket
from constants import HOST,PORT

class mitra_server:
    def __init__(self, socket_tup) -> None:
        self.EDB = None
        self.p = -1
        self.conn,self.sock_addr = socket_tup

    def Run(self):
        resp_tup = pickle.loads(self.conn.recv(4096))
        # print(resp_tup)
        if(resp_tup[0]==0):#for setup
            self.Setup(resp_tup[1])
            self.conn.send(pickle.dumps((1,)))
        elif(resp_tup[0]==1):
            self.Update(resp_tup[1])
            self.conn.send(pickle.dumps((1,)))
        elif(resp_tup[0]==2):
            self.Search(resp_tup[1])
            
    def Setup(self,res):
        self.EDB, self.p = res
        
    def Update(self,avax_tup):
        TSet, XSet = self.EDB
        addr,val,α,xtag = avax_tup
        TSet[addr]=(val,α)
        XSet.add(xtag)
        self.EDB = (TSet, XSet)
        print(len(self.EDB[1]))
    
    def Search(self, tknlists):
        TSet, XSet = self.EDB
        stokenlist = tknlists[0]
        xtokenlists = tknlists[1]
        n = len(stokenlist)
        # print(n,m, len(xtokenlists[0]),'-'*5)
        sEOpList = []
        for j in range(n):
            cnt = 1
            sval, α = TSet[stokenlist[j]]
            for xt in xtokenlists[j]:
                xtoken_ij = xt
                xtag_ij = pow(xtoken_ij, α, self.p)
                print(xtag_ij)
                if(xtag_ij in XSet):
                    cnt+=1
            print("count:", cnt)
            sEOpList.append((j,sval,cnt))
        self.conn.send(pickle.dumps((sEOpList,)))
    


if __name__=="__main__":
    HOST = sys.argv[1]
    PORT = int(sys.argv[2])
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((HOST, PORT))
    s.listen(1)

    conn, addr = s.accept()
    # print('Connected by', addr)
    server_obj = mitra_server((conn,addr))
    server_obj.Run()
    # print("new edb recieved to server: ",server_obj.EDB)
    server_obj.Run()
    # print(server_obj.EDB)
    while(True):
        server_obj.Run()
    # conn.close()