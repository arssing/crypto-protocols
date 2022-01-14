import socket
import hashlib
import string
import random
import time

letters = string.ascii_letters + string.digits

def challenge(mode,pi=0,msg=""):
	identifier = chr(pi)
	if mode == 1:
		r = random.randint(1,16)
		value = "".join(random.choice(letters) for i in range(r))
		length = chr(4 + len(value))
		s = "1" + identifier + length + chr(len(value)) + value
		result = [value,s]
	elif mode == 3:
		length = chr(3+len(msg))
		s = "3" + identifier + length + msg
		result = s
	elif mode == 4:
		length = chr(3+len(msg))
		s = "4" + identifier + length + msg
		result = s
	else:
		print("Неверный код пакета")
		return
	return result

def respCheck(pi,response,hsh):
	resplen = len(response)
	if resplen > 2:
		if chr(response[0]) == '2':
			if response[1] == pi:
				length = response[2]
				if resplen == length:
					valuesize = response[3]
					responsevalue = response[4:(4+valuesize)]
					if hsh == responsevalue:
						return True
	return False
				
def main():
	secret = "password"
	listener = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
	listener.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
	IP = "127.0.0.1"
	PORT = 12345
	listener.bind((IP,PORT))
	listener.listen(0)
	
	while True:
		try:
			connection,address = listener.accept()
			fc = 0
			pi = 0
			data = connection.recv(1024).decode()
			start = time.time()
			while True:
				t = time.time() - start
				if t % 1 == 0:
					print(t)
				if  fc == 0:
					fc = 1
					ch = challenge(1,pi)
					pi +=1
					if pi == 256:
						pi = 0
					hsh = hashlib.md5((chr(pi-1) + secret + ch[0]).encode()).digest()
					connection.send((ch[1]).encode())
					print("Initial challenge sent")
					response = connection.recv(1024)
					if respCheck(pi-1,response,hsh):
						connection.send(challenge(3,pi-1).encode())
						data = connection.recv(1024).decode()
						if data != None:
							print("Client:" + data)
							connection.send("OK".encode())
							continue
					else:
						print("Client sent wrong value")
						connection.send(challenge(4,pi-1).encode())
						connection.close()
						break
				elif t >= 5 :	
					start += t
					ch = challenge(1,pi)
					pi +=1
					if pi == 256:
						pi = 0
					hsh = hashlib.md5((chr(pi-1) + secret + ch[0]).encode()).digest()
					connection.send((ch[1]).encode())
					print("Auxiliary challenge sent")
					response = connection.recv(1024)
					if respCheck(pi-1,response,hsh):
						connection.send(challenge(3,pi-1).encode())
						data = connection.recv(1024).decode()
						if data != None:
							print("Client:" + data)
							connection.send("OK".encode())
							continue	
					else:
						print("Client sent wrong value")
						connection.send(challenge(4,pi-1).encode())
						connection.close()
						break
		except Exception:
			print("Something went wrong(Connection closed)")
			continue

if __name__ == '__main__':
	main()
