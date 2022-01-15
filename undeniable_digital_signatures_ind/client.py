from utils import generator, get_hash_by_msg
from Crypto.Util import number
from gmpy2 import invert
import secrets
import socket

HOST = '127.0.0.1'
PORT = 12345 
BITS_IN_PRIME = 40

def Alice():
    p = number.getPrime(BITS_IN_PRIME)
    g = generator(p)

    while True:
        try:
            secret_key = secrets.randbits(20)
            t = invert(secret_key, (p-1))
        except:
            continue
        break

    public_key = pow(g, secret_key, p)

    print(f"prime num = {p}")
    print(f"g = {g}")
    print(f"secret key = {secret_key}")
    print(f"public key = {public_key}")

    msg = "hello, Bob!"
    hash = get_hash_by_msg(msg)               
    z = pow(hash, secret_key, p)

    to_send = f"{p}|{g}|{BITS_IN_PRIME}|{public_key}|{msg}|{z}"

    client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_sock.connect((HOST, PORT))
    client_sock.sendall(to_send.encode())

    c = int(client_sock.recv(1024).decode())
    d = str(pow(c, t+1, p))
    client_sock.sendall(d.encode())
    client_sock.close()


if __name__ == "__main__":
    Alice()