from socket import *
import sys
import json
import threading
import time

#ip = localhost
#port = 9021

""""if len(sys.argv) != 3:
    print(f"Usage: {sys.argv[0]} <ip> <port>", file=sys.stderr)
    sys.exit(1)

SERVER = sys.argv[1]
PORT = int(sys.argv[2])
TAILLE_TAMPON = 256
"""

SERVER = "localhost"
PORT = 8081
TAILLE_TAMPON = 10240

with socket(AF_INET, SOCK_STREAM) as sock:
    sock.connect((SERVER, PORT))
    
    print(f"Connexion vers {SERVER} : {str(PORT)} reussie.")

    while True:

        msg = input("Entrez une commande : ")       

        # Envoi de la requête au serveur après encodage de str en bytes
        if msg == "quit" :
            sock.send(msg.upper().encode())
            break
        sock.send(msg.upper().encode())

        # Réception de la réponse du serveur et décodage de bytes en str
        reponse = sock.recv(TAILLE_TAMPON)
        print("Réponse = " + reponse.decode())
    
    print ("Deconnexion.")
    sock.close()

