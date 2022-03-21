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
    