from socket import *
import sys
from datetime import datetime
import time
import threading



SERVER = 'localhost'	#a définir
PORT = 8280				#a définir
TAILLE_TAMPON = 256		#256 byte, ça devrait le faire

if len(sys.argv) != 1:
    print(f"Usage: {sys.argv[0]} <username>", file=sys.stderr)
    sys.exit(1)

	
	
def arret():
	
	return
def pause():
	return

def plus_pause():
	return
	
def liste_adversaire():
	return
	
def changer_nom():
	return
	
def echange():
	return
	
def bouger():
	return
	
def aide():
	return

sock = socket(AF_INET, SOCK_DGRAM)
clients = []
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
action=[]

sock.bind((SERVER, PORT)

    
f = open('registreServeur.log', "a")
try:
	f.write("Connexion "+datetime.now().strftime("%d/%m/%Y %H:%M:%S") +"PORT: "+PORT+"\n" )
	while True:
		sock.listen()
		thread_event = threading.Event()
		connection, client_address = sock.accept()
		client = threading.Thread
        client.start()
        clients.append(client)
		try:
			while True:
				(comm, (client_ip,client_port)) = sock.recvfrom(TAILLE_TAMPON)
				commande = comm.decode().upper()
				commandes={
							'QUIT':arret,
							'PAUSE':pause,
							'PLAY':plus_pause,
							'LIST':liste_adversaire,
							'RENAME':changer_nom,
							'EXCHANGE':echange,
							'MOVE':bouger,
							'HELP':aide
							}
				
				if commande in commandes:
					reponse=commandes[commande](arg)
				else:
					reponse='400 Bad Request'
				sock.sendto(reponse.encode(), adr_client)
			except KeyboardInterrupt:
				break
				
				
    finally:
        for j in clients:
            t.join()
        sock.close()
finally:
	f.write("Arret Serveur -"+str(datetime.now().strftime('%Y-%m-%d %H:%M:%S')) + "\n")
	f.close()
	connection.close()

	

print("Systeme stop", file=sys.stderr)
sys.exit(0)