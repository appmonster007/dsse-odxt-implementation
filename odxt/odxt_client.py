import sys
from util.ODXClient import ODXTClientV2, ODXTClient

MAXINT = sys.maxsize
HOST = 'localhost'
PORT = 50057


if __name__ == "__main__":
    HOST = sys.argv[1]
    PORT = int(sys.argv[2])
    # HOST = 'localhost'
    # PORT = 50060
    client_obj = ODXTClientV2((HOST, PORT))
    client_obj.Setup(100)
    # print(client_obj.sk,client_obj.st)

    client_obj.Update('add', (2, "apple"))
    client_obj.Update('add', (4, "apple"))
    client_obj.Update('add', (5, "apple"))
    client_obj.Update('add', (6, "apple"))
    client_obj.Update('add', (7, "apple"))
    client_obj.Update('add', (8, "apple"))
    client_obj.Update('del', (7, "apple"))
    # client_obj.Update('add', (7, "apple"))

    client_obj.Update('add', (3, "banana"))
    client_obj.Update('add', (4, "banana"))
    client_obj.Update('add', (5, "banana"))
    client_obj.Update('add', (6, "banana"))
    client_obj.Update('add', (7, "banana"))
    client_obj.Update('del', (4, "banana"))

    client_obj.Update('add', (3, "pincode"))
    client_obj.Update('add', (4, "pincode"))
    client_obj.Update('add', (5, "pincode"))
    client_obj.Update('add', (6, "pincode"))
    client_obj.Update('add', (7, "pincode"))
    client_obj.Update('del', (3, "pincode"))
    print("Search for apple")
    client_obj.Search(["apple"])
    print("Search for banana")
    client_obj.Search(["banana"])
    print("Search for pincode")
    client_obj.Search(["pincode"])
    print("Search for apple and banana")
    client_obj.Search(["apple", "banana"])
    print("Search for apple and pincode")
    client_obj.Search(["apple", "pincode"])
    print("Search for banana and pincode")
    client_obj.Search(["banana", "pincode"])
    print("Search for apple and pincode and banana")
    client_obj.Search(["apple", "pincode", "banana"])
