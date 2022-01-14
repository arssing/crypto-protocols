import socket
import hashlib

IP = "127.0.0.1"
PORT = 12345

def md5(msg):
    hash = hashlib.md5(msg).digest()
    return hash

def solve_challenge(secret, resp):

    identifier = resp[1:2]
    len_data = ord(resp[3:4])
    value = resp[4:4+len_data]

    hash = md5(identifier+secret+value)
        
    length = chr(4+len(hash)).encode()
    hash_size = chr(len(hash)).encode()
    
    challenge = b'2'
    challenge = challenge+identifier+length+hash_size+hash
    return challenge

def main():
    secret = b"password"

    client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_sock.connect((IP, PORT))

    client_sock.sendall("hi".encode())
    try:
        while True:
            resp = client_sock.recv(1024)
            print(f"Ответ от сервера: {resp.decode()}")

            if (resp.decode()[0] == '1') and len(resp)>=3:
                print("Решаем challenge")
                solve = solve_challenge(secret, resp)
                client_sock.sendall(solve)

            elif resp.decode()[0] == "3" and len(resp)>=3:
                print("Соединение установлено")
                client_sock.sendall("Hello".encode())

            elif resp.decode()[0] == "4" and len(resp)>=3:
                print("Что-то пошло не так")
                client_sock.close()
                return
    except:
        print("соединение разорвано")
if __name__ == '__main__':
    main()

    