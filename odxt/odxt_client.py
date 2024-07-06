import sys, logging
from util.ODXClient import ODXTClient, flexODXTClient, suppODXTClient

logging.basicConfig(level=logging.DEBUG)

log = logging.getLogger(__name__)

MAXINT = sys.maxsize
HOST = 'localhost'
PORT = 50057


if __name__ == "__main__":
    HOST = sys.argv[1]
    PORT = int(sys.argv[2])
    # HOST = 'localhost'
    # PORT = 50060
    client_obj = flexODXTClient((HOST, PORT))
    client_obj.Setup(100)

    client_obj.Update('add', 2, "apple")
    client_obj.Update('add', 4, "apple")
    client_obj.Update('add', 5, "apple")
    client_obj.Update('add', 6, "apple")
    client_obj.Update('add', 7, "apple")
    client_obj.Update('add', 8, "apple")
    client_obj.Update('del', 7, "apple")
    # client_obj.Update('add' 7, "apple")
    client_obj.Update('add', 3, "banana")
    client_obj.Update('add', 4, "banana")
    client_obj.Update('add', 5, "banana")
    client_obj.Update('add', 6, "banana")
    client_obj.Update('add', 7, "banana")
    client_obj.Update('del', 4, "banana")
    client_obj.Update('add', 3, "pincode")
    client_obj.Update('add', 4, "pincode")
    client_obj.Update('add', 5, "pincode")
    client_obj.Update('add', 6, "pincode")
    client_obj.Update('add', 7, "pincode")
    client_obj.Update('del', 3, "pincode")

    
    log.info("Search for apple")
    log.info(client_obj.Search(["apple"]))
    log.info("Search for banana")
    log.info(client_obj.Search(["banana"]))
    log.info("Search for pincode")
    log.info(client_obj.Search(["pincode"]))
    log.info("Search for apple and banana")
    log.info(client_obj.Search(["apple", "banana"]))
    log.info("Search for apple and pincode")
    log.info(client_obj.Search(["apple", "pincode"]))
    log.info("Search for banana and pincode")
    log.info(client_obj.Search(["banana", "pincode"]))
    log.info("Search for apple and pincode and banana")
    log.info(client_obj.Search(["apple", "pincode", "banana"]))
