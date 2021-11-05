import socket
import hashlib

def s_key_secure_hash(msg):
    hash = hashlib.md5(msg).hexdigest()
    part_0 = int(hash[0:8], 16)
    part_1 = int(hash[8:16], 16)
    part_2 = int(hash[16:24], 16)
    part_3 = int(hash[24:32], 16)
    
    part_0 ^= part_2
    part_1 ^= part_3

    out = (part_0 << 32) | part_1
    out = out.to_bytes((out.bit_length() + 7) // 8, byteorder='little')
    
    return out

def change_pass(s, client_sock):
    s = s.split(" ")
    passwd = s[1]
    seed = s[2]
    rounds = int(s[3])
    hsh = seed + passwd
    hsh = s_key_secure_hash(hsh.encode())

    for i in range(rounds):
        hsh = s_key_secure_hash(hsh)
    
    hsh = hsh.decode('cp437')  
    command = f"keyinit {hsh} {seed} {rounds-1}"
    client_sock.sendall(command.encode())

def main():
        
    client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_sock.connect(('127.0.0.1', 12345))

    login = input("Введите логин:")
    client_sock.sendall(login.encode())
    resp = ((client_sock.recv(1024)).decode())


    if resp == "User not recognized":
        print("Пользователь не найден")
        return

    elif resp:
        resp = resp.split(" ")
        seed = resp[0]
        rounds = int(resp[1])
        
        passwd = input("Введите пароль:")

        #вычисляем нужные хэши и сохраняем их
        hsh = seed + passwd
        hsh = s_key_secure_hash(hsh.encode())
        for i in range(rounds):
            hsh = s_key_secure_hash(hsh)
        client_sock.sendall(hsh)

        while True:
            resp = client_sock.recv(1024).decode()
            if resp == "Sequence number became -1. Use keyinit command!":
                keyinit = ""
                while not keyinit.startswith("keyinit ") or len(keyinit.split(" ")) != 4:
                    keyinit = input("Пожалуйста, используйте keyinit <пароль> <семя> <число итераций> , так как ваши одноразовые пароли закончились!\n")

                change_pass(keyinit, client_sock)
                print(client_sock.recv(1024).decode())
                continue    

            elif resp == "Connection established":
                print("Соединение с сервером уставновлено")
                print("Чтобы выйти введите close")

                while True:
                    s = input("Ваше сообщение серверу:")
                    if s.startswith("keyinit "):
                        if len(s.split(" ")) != 4:
                            print("Введите команду корректно: keyinit <пароль> <семя> <число итераций>")
                            continue
                        else:
                            change_pass(s, client_sock)

                    elif s == "close":
                        client_sock.sendall(s.encode())
                        client_sock.close()
                        print("Соединение закрыто")
                        return

                    else:
                        client_sock.sendall(s.encode())

                    resp = client_sock.recv(1024).decode()
                    print(f"Ответ сервера: {resp}")
            elif resp == "Wrong password":
                print("Неправильный пароль")
                return
    else:
        print("Соединение не удалось!")
        return

if __name__ == '__main__':
    main()

    