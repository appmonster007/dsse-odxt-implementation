import pickle, sys
import socket
from util.constants import HOST,PORT

class mitra_server:
    def __init__(self, socket_tup) -> None:
        self.EDB = None
        self.conn,self.sock_addr = socket_tup

    def Run(self):
        # while(True):#not very safe
        resp_tup = pickle.loads(self.conn.recv(4096))
        if(resp_tup[0]==0):#for setup
            self.Setup(resp_tup[1])
        elif(resp_tup[0]==1):
            self.Update(resp_tup[1])
        elif(resp_tup[0]==2):
            self.Search(resp_tup[1])
        # else:
        #     print("invalid input")
    #should recieve by socket, but can be called as direct function in client side, 
    #since server object can exist client side.
    #not ideal, but a workaround to actual implementation     
    def Setup(self,EDB):
        self.EDB = EDB
    #change to a better database in future
    def Update(self,addr_val_tup):
        addr,val=addr_val_tup
        self.EDB[addr]=val
    
    def Search(self,Tokenlists):
        n=len(Tokenlists)
        # 2. Initialize EOpList1; : : : ; EOpListn to empty lists
        EOpLists = [list()]*n
        for i in range(n):
            for j in range(len(Tokenlists[i])):
                # i. Set vali;j = TSet[tokenListi[j]]
                val_ij = self.EDB[Tokenlists[i][j]]
                # ii. Set EOpListi = EOpListi [ fvali;jg
                EOpLists[i].append(val_ij) #should be union, but assuming hash are unique, can be appended
        # 5. Send EOpList1; : : : ; EOpListn to the client
        self.conn.send(pickle.dumps((EOpLists,)))
        return EOpLists
    


if __name__=="__main__":
    HOST = sys.argv[1]
    PORT = int(sys.argv[2])
    
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((HOST, PORT))
    s.listen(1)

    conn, addr = s.accept()
    print('Connected by', addr)
    server_obj = mitra_server((conn,addr))
    server_obj.Run()
    print("new edb recieved to server: ",server_obj.EDB)
    server_obj.Run()
    print(server_obj.EDB)
    server_obj.Run()
    server_obj.Run()
    server_obj.Run()
    conn.close()