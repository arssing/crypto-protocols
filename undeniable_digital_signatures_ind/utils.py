from gmpy2 import gcd
import secrets
import hashlib
def get_hash_by_msg(msg):
    msg = msg.encode()
    hash = hashlib.sha256(msg).digest()
    hash = int.from_bytes(hash, "big") 
    return hash

def generator(n):
    fi = n-1
    factor = []
    i = 2

    fi_cop = fi
    while i*i <= fi_cop:
        if fi_cop % i == 0:
            factor.append(i)
            while fi_cop % i == 0:
                fi_cop //= i
        i += 1
    if fi_cop > 1:
        factor.append(fi_cop)
    
    
    for g in range(2, n):
        if gcd(g, n) == 1:
            count = 0
            for pi in factor:
                if pow(g ,(fi // pi), n) != 1:
                    count += 1
                if count == len(factor):
                    return g

    return -1

def a_b(max_bits, max):
    a_b = []
    while True:
        n = secrets.randbits(max_bits)
        if n < max:
            a_b.append(n)
        if len(a_b) == 2:
            return a_b

def get_parametrs(resp):
    try:
        list_ = resp.decode().split("|")
        p = int(list_[0])
        g = int(list_[1])
        max_bits = int(list_[2])
        pk = int(list_[3])
        m = list_[4]
        z = int(list_[5])
        ab = a_b(max_bits, p)

        a = ab[0]
        b = ab[1]

        return p, g, pk, m, z, a, b
    except:
        return None