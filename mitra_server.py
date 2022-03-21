from http import server
import pickle
import random, socket
from constants import HOST,PORT

class mitra_server:
    def __init__(self) -> None:
        self.EDB = None
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
        EOpLists = [list() for word in range(n)]
        for i in range(n):
            for j in range(len(Tokenlists[i])):
                # i. Set vali;j = TSet[tokenListi[j]]
                val = self.EDB(Tokenlists[i][j])
                # ii. Set EOpListi = EOpListi [ fvali;jg
                EOpLists[i].append(val) #should be union, but assuming hash are unique, can be appended
        # 5. Send EOpList1; : : : ; EOpListn to the client
        return EOpLists
    


if __name__=="__main__":
    server_obj = mitra_server()
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((HOST, PORT))
    s.listen(1)

    conn, addr = s.accept()
    print('Connected by', addr)
    edb_recv, = pickle.loads(conn.recv(4096))

    server_obj.Setup(edb_recv)
    print("new edb recieved from server: ",server_obj.EDB)
    conn.close()