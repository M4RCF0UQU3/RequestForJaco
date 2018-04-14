#!/usr/bin/env python

import threading, sys, re, Queue

class ThreadDebut(threading.Thread):
    """
    Utilisation du fichier Log de configuration pour gérer la connection.
    Par la fonction run()
    """
    def __init__(self, active, logQueue, path):
        threading.Thread.__init__(self)
        self.active = active
        self.logQueue = logQueue
        self.logpath = path

    def run(self):
        
        print("Début de Connection du Thread")
        with open(self.logpath + "spaceXlog.txt", "a") as f:
            print ("Ouverture du fichier Log")
            while not self.active.is_set():
                if not self.logQueue.empty():
                    msg = self.logQueue.get(False)
                    f.write(msg)
        print("Thread d'entame fermé !")