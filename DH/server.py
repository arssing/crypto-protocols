import socket
from hashlib import sha1
from secrets import SystemRandom
HOST = '127.0.0.1'
PORT = 12345 

if __name__ == "__main__":
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((HOST, PORT))
    sock.listen(1)
    print('Сервер запущен')
    while True:
        conn, addr = sock.accept()
        print(f"новое подключение: {addr}")
        data = conn.recv(2048).decode().split("|")

        if len(data) != 2:
            print("Ошибка - формат пакета не: n|e")
            conn.sendall("error".encode())
            continue
        #считаем, что публичный ключ n|e получен из надежного источника т.е.: n|e -> Alice
        try:
            n = int(data[0])
            e = int(data[1])
        except:
            print("Ошибка при преобразовании в тип int: n|e")
            conn.sendall("error".encode())
            continue

        conn.sendall("OK".encode())
        print(f"n = {n}")
        print(f"e = {e}")

        try:
            #проверка цифровой подписи

            msg = conn.recv(2048).decode().split(":")
            signature = int(msg[1])
            hash = int.from_bytes(sha1(msg[0].encode()).digest(), byteorder='big')
            hashFromSignature = pow(int(signature), e, n)
            if hash == hashFromSignature:
                print("Подпись действительна")
        
                msg = msg[0].split("|")
                public_alice = int(msg[0])
                g = int(msg[1])
                p = int(msg[2])

                rand = SystemRandom()
                private = rand.randrange(2, pow(2,127))
                public = pow(g, private, p)

                conn.sendall(str(public).encode())

                key = pow(public_alice, private, p)

                print(f"key={key}")
                

            else:
                print("Подпись неверна")
                continue
        except:
            print("что-то пошло не так")
            continue