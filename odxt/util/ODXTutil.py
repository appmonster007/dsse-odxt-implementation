import random
import hashlib
from math import sqrt, gcd


KEYSIZE = 10**8
MAXBITS = 256
MAXBYTES = 64


def bytes_XOR(b1: bytes, b2: bytes) -> bytes:
    return bytes(x^y for x,y in zip(b1, b2))
    # return (int.from_bytes(b1) ^ int.from_bytes(b2)).to_bytes(32)

def mul_inv(a, b):
    if(gcd(a, b) > 1):
        a = a % b
    b0 = b
    x0, x1 = 0, 1
    if b == 1:
        return 1
    while a > 1 and b != 0:
        q = a // b
        a, b = b, a % b
        x0, x1 = x1 - q * x0, x0
    if x1 < 0:
        x1 += b0
    return x1


def gen_key_F(l, bitsize=MAXBITS):
    random.seed(l)
    return random.getrandbits(bitsize).to_bytes(32)


def prf_F(Key: bytes, M: bytes) -> bytes:
    random.seed(Key)
    # rval = random.getrandbits(MAXBITS)
    rval = random.randbytes(MAXBYTES)
    Mhash = hashlib.new('sha256')
    Mhash.update(M)
    hs = Mhash.digest()
    res = bytes_XOR(hs, rval)
    return res
    # Mval = int.from_bytes(Mhash.digest())
    # rstr = (rval ^ Mval)
    # return rstr.to_bytes(32)


def prf_Fp(Key: bytes, M: bytes, p: int, g: int) -> bytes:
    random.seed(Key)
    # rval = random.getrandbits(MAXBITS)
    rval = random.randbytes(MAXBYTES)
    Mhash = hashlib.new('sha256')
    Mhash.update(M)
    hs = Mhash.digest()
    res = int.from_bytes(bytes_XOR(hs, rval), byteorder="big")
    # Mval = int.from_bytes(Mhash.digest())
    # rstr = (rval ^ Mval)
    if(res % p == 0):
        res += 1
    ex = (res % p)
    return pow(g, ex, p-1).to_bytes(32)


def findPrimefactors(s, n):
    while (n % 2 == 0):
        s.add(2)
        n = n // 2
    for i in range(3, int(sqrt(n)), 2):
        while (n % i == 0):
            s.add(i)
            n = n // i
    if (n > 2):
        s.add(n)


def findPrimitive(n):
    s = set()
    phi = n - 1
    findPrimefactors(s, phi)
    for r in range(2, phi + 1):
        flag = False
        for it in s:
            if (pow(r, phi // it, n) == 1):
                flag = True
                break
        if (flag == False):
            return r
    return -1


def shuffle_and_index(lst):
    i_lst = list(enumerate(lst))
    random.shuffle(i_lst)
    return ([i[1] for i in i_lst], [i[0] for i in i_lst])

def sort_by_order(lst, index):
    e_lst = list(zip(index, lst))
    return [i[1] for i in sorted(e_lst)]