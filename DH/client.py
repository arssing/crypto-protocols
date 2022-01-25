
from secrets import randbelow, randbits, SystemRandom
from math import ceil
from hashlib import sha1
from random import randrange
from Crypto.PublicKey import RSA
import socket

HOST = '127.0.0.1'
PORT = 12345 

def set_bit(value, bit):
    return value | (1 << bit)

def get_U(seed: int, seedlen: int, m):
    U = 0
    for i in range(m):
        seed_i = seed + i
        sha1_seed_i = sha1(seed_i.to_bytes(ceil(seed_i.bit_length() / 8), "big")).digest()
        seed_m_i = (seed+m+i) % pow(2, seedlen)
        sha1_seed_m_i = sha1(seed_m_i.to_bytes(ceil(seed_m_i.bit_length() / 8), "big")).digest()
        xor_sha1 = int.from_bytes(sha1_seed_i, "big") ^ int.from_bytes(sha1_seed_m_i, "big")
        U = U + xor_sha1 * pow(2, 160 * i)
    return U
def power_2(num):
    pow_2 = 0
    while True:
        if num & 1 == 0:
            num >>= 1
            pow_2 += 1
        else:
            return pow_2
    
#тест Миллера-Рабина
def is_prime(q):
    i = 1
    n = 50
    w = q
    a = power_2(w-1)
    m = (w-1) // pow(2,a)
    rand = SystemRandom()
    while True:
        b = rand.randrange(1,w)
        j = 0
        z = pow(b, m, w)
        while True:
            if (j == 0 and z == 1) or z == w - 1:
                if i < n:
                    i = i + 1
                    break
                else:
                    return True
            if j > 0 and z == 1:
                return False
            j += 1
            if j < a:
                z = pow(z, 2, w)
                continue
            return False

     
# m1 = m
# l1 = L
# m = m'
def gen_pq(m1, l1):
    m = ceil(m1 / 160)
    L = ceil(l1 / 160)
    N = ceil(L / 1024)
    prime = False

    while not prime:
        seedlen = m + randbelow(128)
        seed = randbits(seedlen)
        U = get_U(seed, seedlen, m)

        q = U % pow(2,m1)
        q = set_bit(q, 0)
        q = set_bit(q, m1 - 1)
        prime = is_prime(q)
        
    counter = 0
    while True:
        R = seed + 2*m + L*counter
        V = 0
        for i in range(L-1):
            R_i = R + i
            sha1_R_i = sha1( R_i.to_bytes(ceil(R_i.bit_length() / 8), "big") ).digest()
            V = V + int.from_bytes(sha1_R_i, "big") * pow(2, 160 * i)
        W = V % pow(2, l1)
        X = W | pow(2, l1 - 1)
        p = X - (X % (2 * q)) + 1

        if p > pow(2, l1 - 1) and is_prime(p):
            return (p, q, seed, counter) 
        counter += 1

        if counter < (4096 * N):
            continue
        return False

def check_public_key(key, p, q):
    if key < 2 or key > p - 1:
        return False
    if pow(key, q, p) != 1:
        return False
    return True

def gen_valid_keys():
    while True:
        p, q, seed, counter = gen_pq(128, 1024)
        g = gen_g(p, q)
        rand = SystemRandom()
        x = rand.randrange(2, q - 2)
        y = pow(g, x, p)
        if check_public_key(y, p, q):
            break
    return (x, y, g, p)

def gen_g(p, q):
    j = (p-1) // q
    prev_h = []
    while True:
        h = randrange(2, p - 1)
        if h in prev_h:
            continue
        prev_h.append(h)
        g = pow(h, j, p)
        if g != 1:
            return g
    
if __name__ == "__main__":

    client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_sock.connect((HOST, PORT))

    keyPair = RSA.generate(bits=1024)
    print(f"Public key:  (n={keyPair.n}, e={keyPair.e})")
    print(f"Private key: (n={keyPair.n}, d={keyPair.d})")

    to_send = f"{keyPair.n}|{keyPair.e}"
    client_sock.sendall(to_send.encode())

    resp = client_sock.recv(2048).decode()
    if resp == "OK":
        secret, public, g, p = gen_valid_keys()

        print(f"secret = {secret}")
        print(f"public = {public}")
        print(f"g = {g}")
        print(f"p = {p}")

        msg = f"{public}|{g}|{p}"

        hash = int.from_bytes(sha1(msg.encode()).digest(), byteorder='big')
        signature = pow(hash, keyPair.d, keyPair.n)
        
        to_send = f"{msg}:{signature}"

        client_sock.sendall(str(to_send).encode())

        resp = client_sock.recv(2048).decode()
        try:
            public_bob = int(resp)
            key = pow(public_bob, secret, p)
            print(f"key={key}")
        except:
            print("Приватный ключ сервера не удалось преобразовать в int")