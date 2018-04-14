from socket import *
import sys
import json
import threading
import time

#ip = localhost
#port = 9021

SERVER = "localhost"
PORT = 8081
TAILLE_TAMPON = 10240

class ListenThread(threading.Thread):
    
    """ Creation d'un thread pour l'ecoute du serveur"""
    
    def __init__(self, sock, lock, event):
        threading.Thread.__init__(self)
        self.lock = lock
        self.sock = sock
        self.event = event
        
    def run(self):
        while not self.event.is_set():
            with self.lock: #.acquire()
                try:
                    reponse = self.sock.recv(TAILLE_TAMPON)
                    print("Reponse = " + reponse.decode())
                except:
                    pass
                #finally:
                   # self.lock.release()
            #time.sleep(0.3)
            
        

with socket(AF_INET, SOCK_STREAM) as sock:
    
    sock.connect((SERVER, PORT))
    sock.setblocking(0)
    
    event_stop = threading.Event()
    lock_thread = threading.Lock()
    
    rep = ListenThread(sock, lock_thread, event_stop)
    rep.start()
    
    print(f"Connexion vers {SERVER} : {str(PORT)} reussie.")
    
    print("Entrez les commandes : ")

    while True:

        msg = input()       

        # Envoi de la requête au serveur après encodage de str en bytes
        
        #lock_thread.acquire() 
        
        with lock_thread:
            if msg == "quit" :
                sock.send(msg.upper().encode())
                event_stop.set()
                #rep.join()
                break
                
            else: 
                sock.send(msg.upper().encode())
                time.sleep(0.3)
                
        #lock_thread.release()

        # Réception de la réponse du serveur et décodage de bytes en str
        #reponse = sock.recv(TAILLE_TAMPON)
        #print("Réponse = " + reponse.decode())
    
    print ("Deconnexion.")
    sock.close()

