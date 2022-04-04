import random
import hashlib
from math import sqrt, gcd
from .constants import KEYSIZE, MAXBITS


def bytes_XOR(b1: bytes, b2: bytes):
    return (int.from_bytes(b1, 'little') ^ int.from_bytes(b2, 'little')).to_bytes(32, 'little')


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


def gen_key_F(λ, bitsize=MAXBITS):
    random.seed(λ)
    return random.getrandbits(bitsize).to_bytes(32, 'little')


def prf_F(Key: bytes, M: bytes):
    random.seed(Key)
    rval = random.getrandbits(MAXBITS)
    Mhash = hashlib.new('sha256')
    Mhash.update(M)
    Mval = int.from_bytes(Mhash.digest(), 'little')
    rstr = (rval ^ Mval)
    return rstr.to_bytes(32, 'little')


def prf_Fp(Key: bytes, M: bytes, p: int, g: int):
    random.seed(Key)
    rval = random.getrandbits(MAXBITS)
    Mhash = hashlib.new('sha256')
    Mhash.update(M)
    Mval = int.from_bytes(Mhash.digest(), 'little')
    rstr = (rval ^ Mval)
    if(rstr % p == 0):
        rstr += 1
    ex = (rstr % p)
    return pow(g, ex, p-1).to_bytes(32, 'little')


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
