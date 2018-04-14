import threading, sys, re, json, ast, time, Queue

class ThreadDiffusion(threading.Thread):
    """
    Diffusion des Messages reçus durant la creation à tous les utilisateur probable du map
    """
    def __init__(self, users, userlock, active, broadCastQueue, map, maplock):
        threading.Thread.__init__(self)
        self.active = active
        self.broadCastQueue = broadCastQueue
        self.users = users
        self.userlock = userlock
        self.map = map
        self.maplock = maplock

    def run(self):
        print("Début de diffusion des messages")
        while not self.active.is_set():
            if not self.broadCastQueue.empty():
                msg = self.broadCastQueue.get(False)
                output = self.interprete(msg)
                print("Envoie de la Map ### ")
                with self.userlock:
                    for user, userprops in self.users.items():
                        userprops["mailbox"].put(output)
            time.sleep(0.01)
        print("Diffusion de Thread stoppé !")

    def interprete(self, msg):
        if msg == "update":
            with self.maplock:
                return "100 " + json.dumps(self.map) + "\r\n"