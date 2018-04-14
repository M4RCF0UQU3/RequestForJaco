import threading, sys, re, time, Queue

class EnvoieThread(threading.Thread):
    """
    Permet d'enoyer les réponses propables aux commandes 
    """
    def __init__(self, clientsocket, socketLock, queue, event):
        threading.Thread.__init__(self)
        self.socketLock = socketLock
        self.clientsocket = clientsocket
        self.active = event
        self.mailbox = queue

    def run(self):
        print("Début d'envoie de Thread !")
        while not self.active.is_set():
            if not self.mailbox.empty():
                command = self.mailbox.get(False)
                print("Envoi de la commande, en cours "+command)
                with self.socketLock:
                    self.clientsocket.send(command.encode())
                    self.mailbox.task_done()
            time.sleep(0.01)
        print("Thread d'envoie fermé !")