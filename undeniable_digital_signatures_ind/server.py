import socket
import secrets
from utils import get_parametrs, get_hash_by_msg

HOST = '127.0.0.1'
PORT = 12345 

def Bob():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((HOST, PORT))
    sock.listen(1)
    print('Сервер запущен')
    while True:
        conn, addr = sock.accept()
        data = conn.recv(1024)
        try:
            p,g,pk,msg,z,a,b = get_parametrs(data)
        except:
            print("Неверные параметры")
            continue  
        za = pow(z, a, p)
        pkb = pow(pk, b, p)
        c = (za * pkb) % p
        conn.send(str(c).encode())
        try:
            d = int(conn.recv(1024).decode())
        except:
            print("Неверные параметры")
            continue

        hash = get_hash_by_msg(msg)
        ma = pow(hash, a, p)
        gb = pow(g, b, p)
        d_2 = (ma*gb)%p
        if d==d_2:
            print(f"Алиса написала:{msg}")
        else:
            print(f"Это не Алиса:{msg}")

if __name__ == "__main__":
    Bob()