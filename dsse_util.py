import random, hashlib, string
from math import sqrt
from constants import KEYSIZE, MAXBITS

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

def gen_key_F(λ, bitsize=MAXBITS):
    random.seed(λ)
    return random.getrandbits(bitsize).to_bytes(32, 'little')

def prf_F(Key: bytes, M: bytes):
    random.seed(Key)
    rval = random.getrandbits(MAXBITS)
    Mhash = hashlib.new('sha256')
    Mhash.update(M)
    Mval = int.from_bytes(Mhash.digest(), 'little')
    rstr=(rval^Mval)
    return rstr.to_bytes(32, 'little')

def prf_Fp(Key: bytes, M: bytes, p: int):
    random.seed(Key)
    rval = random.getrandbits(MAXBITS)
    Mhash = hashlib.new('sha256')
    Mhash.update(M)
    Mval = int.from_bytes(Mhash.digest(), 'little')
    rstr = (rval^Mval)
    if(rstr%p==0):
        rstr+=1
    return (rstr%p).to_bytes(32, 'little')
    

def findPrimefactors(s, n) :
	while (n % 2 == 0) :
		s.add(2)
		n = n // 2
	for i in range(3, int(sqrt(n)), 2):
		while (n % i == 0) :
			s.add(i)
			n = n // i
	if (n > 2) :
		s.add(n)

def findPrimitive(n) :
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
