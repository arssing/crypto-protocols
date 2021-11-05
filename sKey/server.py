import socket
import hashlib
import string


def hashstep(msg):
    hashed = hashlib.md5(msg).hexdigest()
    part_0 = int(hashed[0:8], 16)
    part_1 = int(hashed[8:16], 16)
    part_2 = int(hashed[16:24], 16)
    part_3 = int(hashed[24:32], 16)
    part_0 ^= part_2
    part_1 ^= part_3
    out = (part_0 << 32) | part_1
    out = out.to_bytes((out.bit_length()+7)//8,'little')
    return out

def hashFunc(msg:str,seqn:int):
	hsh = hashstep(msg.encode())
	for i in range(seqn):
		hsh = hashstep(hsh)
	return hsh

def keyinitValidation(l:list):
	alphanumerics = string.ascii_lowercase + string.digits
	if len(l) == 4:
		if isinstance(l[1].encode('cp437'),bytes) and len(l[1]) == 8:
			if len(l[2]) > 0 and len(l[2]) < 17:
				for i in l[2]:
					if alphanumerics.find(i) == -1:
						return False
				for i in l[3]:
					if string.digits.find(i) == -1:
						return False
				if len(l[3]) > 1 and l[3][0] == '0':
					return False
				return True
	return False

def main():
	d = dict()
	#d["user"]=[b"\x19\x90\x8c\x11r\xf6\xf8]","security",99]#bytes,str,int
	while True:
		cmd = input("Enter command:\n1 - add/update user\n2 - start server\n3 - show database\nexit - quit\nCommand:")
		if cmd == "1":
			key = input("Enter keyinit <user> <password> <seed> <sequence number>:\n")
			splitlist = key.split(" ")
			hsh = hashFunc(splitlist[3]+splitlist[2],int(splitlist[4]))
			d.update({splitlist[1]:[hsh,splitlist[3],int(splitlist[4])-1]})
			continue
		elif cmd == "2":
			listener = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
			listener.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
			IP = "127.0.0.1"
			PORT = 12345
			listener.bind((IP,PORT))
			listener.listen(0)
			
			while True:
				try:
					connection,address = listener.accept()
					data = connection.recv(1024).decode()
					userdata = d.get(data)
					if  userdata == None:
						connection.send("User not recognized".encode())
					else:
						connection.send((userdata[1] + " " + str(userdata[2])).encode())
						password = connection.recv(1024)
						hashres = hashstep(password)
						if hashres == userdata[0]:
							seqn = userdata[2]-1
							if seqn == -1:
								while True:
									connection.send("Sequence number became -1. Use keyinit command!".encode())
									msg = connection.recv(1024).decode()
									if msg.startswith("keyinit "):
										splitlist = msg.split(" ")
										if keyinitValidation(splitlist):
											d.update({data:[splitlist[1].encode('cp437'),splitlist[2],int(splitlist[3])]})
											break
							else:
								d.update({data:[password,userdata[1],seqn]})
							connection.send("Connection established".encode())
							while True:
								msg = connection.recv(1024).decode()
								if msg.startswith("keyinit "):
									splitlist = msg.split(" ")
									if keyinitValidation(splitlist):
										d.update({data:[splitlist[1].encode('cp437'),splitlist[2],int(splitlist[3])]})
										connection.send("Keyinit command used successfully".encode())
									else:
										connection.send("Keyinit command used unsuccessfully".encode())
								elif  msg == "close":
									break
								else:
									connection.send(("Server recieved from user:" + msg).encode())
						else:
							connection.send("Wrong password".encode())
				except Exception:
					continue
		elif cmd == "3":
			print(d)
		elif cmd == "exit":
			return
		else:
			print("Wrong command!")

if __name__ == '__main__':
	main()




		

