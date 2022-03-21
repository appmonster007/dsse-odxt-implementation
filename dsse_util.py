import random
import string
from constants import KEYSIZE
alphabet = string.ascii_letters + string.digits
#SKE helper functions:
def GEN(λ):
    random.seed(λ)
    return random.randint(KEYSIZE,KEYSIZE*10-1)
#random module's probablistic algorithm is relied on for enc and dec
def ENC(sk,x):
    random.seed(sk)
    hashstring = random.sample(alphabet,len(x))
    return xor(hashstring,x)

def DEC(K,c):
    random.seed(K)
    hashstring = random.sample(alphabet,len(c))
    return xor(hashstring,c)

def tobinary(s):
    return ''.join('0'*(8-len(fm:=format(ord(x), 'b')))+fm for x in s)
def tostr(c):
    return ''.join(chr(int(c[i:i+8],base=2)) for i in range(0,len(c),8))
def xor(s1,s2):
    s1b=tobinary(s1)
    s2b=tobinary(s2)
    return tostr(''.join(str(int(c1)^int(c2)) for c1,c2 in zip(s1b,s2b)))