import socket, threading, sys, re, json, random, ast, time, Queue, datetime
class SocketThread(threading.Thread):
   
    def __init__(self,ip, port, clientsocket, map, users, maplock, userlock, broadCastQueue, activated, logQueue):
        threading.Thread.__init__(self)
        self.senderActive = threading.Event()
        self.maplock = maplock
        self.alias = ""
        self.userlock = userlock
        self.map = map
        self.users = users
        self.ip = ip
        self.paused = False
        self.mailbox = Queue.Queue()
        self.socketLock = threading.Lock()
        self.port = port
        self.EnvoieThread = EnvoieThread(clientsocket,self.socketLock, self.mailbox, self.senderActive)
        self.csocket = clientsocket
        self.state = "AUTHORIZATION"
        self.act = activated
        self.commands = {'CONNECT': self.connect, 'QUIT': self.quit, 'ADD': self.add,
                         'ASKTRANSFER': self.asktransfer, 'PAUSE': self.pause, 'PLAY': self.play,
                         'RENAME': self.rename, 'UP': self.up, 'DOWN': self.down, 'LEFT':self.left,
                         'RIGHT': self.right, 'INFO': self.info, 'ACCEPTREQUEST': self.acceptrequest,
                         'REFUSEREQUEST': self.refuserequest}
        self.position = ()
        self.broadcastQueue = broadCastQueue
        self.logQueue = logQueue

    def run(self):
        print("Début de Diffusion Socket")
        self.logQueue.put(str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')) +
                          "[" + self.ip + ", " + str(self.port) + "]: Connected")
        self.EnvoieThread.start()
        while not self.act.is_set():
            with self.socketLock:
                try:
                    data = self.csocket.recv(2048)
                    self.logQueue.put(str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')) +
                                      "["+self.ip+", "+str(self.port)+"]: "+data.decode())
                    self.mailbox.put(self.interprete(data))
                except:
                    pass
            time.sleep(0.1)
        self.senderActive.set()
        print("En attente du diffuseur ...")
        self.EnvoieThread.join()
        self.csocket.close()
        print "Diffusion de Socket fermé !"
        self.logQueue.put(str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')) +
                          "[" + self.ip + ", " + str(self.port) + "]: Disconnected")

    # functions for command evaluation
    def connect(self, alias):
        """
        Vérifie la validité du pseudo et l'ajoute à la liste puis envoir une réponse.
        """
        print ("Commande de connection :    ")
        if self.state == "AUTHORIZATION":
            print (alias)
            validUsername = re.search("^[a-zA-Z0-9]{1,31}$", alias)
            if validUsername:
                #Vérification du pseudo ...
                with self.userlock:
                    if alias in users:
                        return "400 Bad Request : (Pseudo existant !) Essayez-en un nouveau."

                    users[alias] = {"ip":self.ip,"port": self.port, "ressources":[], "requests":[],"mailbox":self.mailbox}
                    print (users)
                self.alias = alias
                self.state = "TRANSACTION"

                return "200 " + json.dumps(self.map)

            else:
                return "440 Pseudo non Valide "
        else:
            return "403 Requete non valide "

    def add(self, coords):
        """
        Ajout d'un robot 
        :param coords: coordonnées du client 
        :return: None
        """
        if self.state == "TRANSACTION":
            pos = ()
            try:
                pos = ast.literal_eval(coords)
                #Vérification de la position avant placement du robot
                with self.maplock:
                    #si les coordonées saisies constitues une place libre :
                    blocking = len(filter(lambda element: element["x"] == pos[0] and element["y"] == pos[1],self.map["blockingElements"]))
                    robots = len(filter(lambda element: element["x"] == pos[0] and element["y"] == pos[1], self.map["robots"]))
                    if (robots+blocking)==0:
                        print ("Placement Ok <<")
                        #Mis en place du robot
                        self.map["robots"].append({"name":self.alias, "x":pos[0],"y":pos[1]})
                        self.position = pos
                        print(self.map)
                        # Mis à jour de la Map
                        self.broadcastQueue.put("update")
                        return "200 Succes de la requete : (Votre robot a été bien ajouté !)"
                    else:
                        return "405 Les Coordonnées sont invalides "


            except:
                return "405 Coordonnées Invalides"
        else:
            return "403 Non authorisé ! ( Veuiller vous connecter)."

    def quit(self):
       
        print ("Déconnection "+str(self.port))
        self.senderActive.set()
        self.act.set()
        if self.alias != "":
            with self.userlock:
                del users[self.alias]
            with self.maplock:
                for robot in self.map["robots"]:
                    if robot["name"] == self.alias:
                        print ("supprimer robot correspondant")
                        self.map["robots"].remove(robot)
                        self.broadcastQueue.put("update")
                        break
        return "200 Déconnexion réussie !"

    def asktransfer(self, username):
      
        if self.state == "TRANSACTION":
            #Vérification client
            with self.userlock:
                if username in users and username != self.alias:
                    users[username]["mailbox"].put("110 Voulez Vous authoriser le transfert ? "+self.alias+"\r\n")
                    #add request to users[username]["requests]
                    users[username]["requests"].append(self.alias)
                    return "202 request submitted, En attente de réponse ? "
                else:
                    return "404 he origin server did not find a current representation (Utilisateur) for the target "
        else:
            return "403 Please connect before trying to pause."

    def pause(self):
        """
        Pauses the robot as specified in RFC Section 4.3
        """
        if self.state == "TRANSACTION":
            with maplock:
                #check if its in maps...
                robot = (filter(lambda element: element["name"] == self.alias, self.map["robots"]))
                print (robot)
                if len(robot) == 1:
                    self.paused = True
                    return "250 ("+ str(robot[0]["x"]) +","+ str(robot[0]["y"]) +")"
                else:
                    return "403 Please add a robot to the map before trying to pause."
        else:
            return "403 Non authorisé ! ( Veuiller vous connecter)."

    def play(self):
       
        if self.state == "TRANSACTION":
            with maplock:
                #check if its in maps...
                robot = (filter(lambda element: element["name"] == self.alias, self.map["robots"]))
                if len(robot) == 1:
                    self.paused = False
                    return "260"
                else:
                    return "403 Veuillez ajouter un robot avant cette Manip ."
        else:
            return "403 Non authorisé ! ( Veuiller vous connecter)."

    def rename(self, alias):
       
        if self.state == "TRANSACTION":
            validUsername = re.search("^[a-zA-Z0-9]{1,31}$", alias)
            if validUsername:
                with self.userlock:
                    if alias in users:
                        return "400 Ce Pseudo est déjà utilisé. Veuillez en choisir à nouveau "
               
                    self.users[alias] = users[self.alias]
                    del users[self.alias]
                   
                with self.maplock:
                    for x in self.map["robots"]:
                        if x["name"]==self.alias:
                            x["name"] = alias
                self.alias = alias
                return "200 "+self.alias
            else:
                return "404 Pseudo invalide ! "
        else:
            return "403 Non authorisé ! ( Veuiller vous connecter)."

    def info(self):
        """
        Renvoie les ressources propre à un utilisateur et la liste des Utilisateurs connectés
        """
        if self.state == "TRANSACTION":
            #get ressources and users
            response = {"Ressources":[], "Users":[]}
            with self.userlock:
                    print (users[self.alias]["ressources"])
                    print (users.keys())
                    response["Ressources"] = users[self.alias]["ressources"]
                    response["Users"] = users.keys()
            return "200 "+json.dumps(response)
        else:
            return "403 Non authorisé ! ( Veuiller vous connecter)."

    def up(self):
        if not self.paused:
            if self.state == "TRANSACTION":
                with maplock:
                    #check if its in maps...
                    robots = (filter(lambda element: element["name"] == self.alias, self.map["robots"]))
                    if len(robots) == 1:
                        #valid movement ( boundaries, obstacles?)
                        if self.validCoords((robots[0]["x"], robots[0]["y"]+1)):
                            robots[0]["y"]=robots[0]["y"]+1
                            # ressources found?
                            self.harvestRessources((robots[0]["x"], robots[0]["y"]))
                        else:
                            return "405 Coordonées Invalides"
                    else:
                        return "403 Non authorisé ! ( Veuiller vous connecter)."
                print self.map
                #update map message
                self.broadcastQueue.put("update")
                return "270 ("+ str(robots[0]["x"]) +","+ str(robots[0]["y"]) +")"
            else:
                return "403 Non authorisé ! ( Veuiller vous connecter)."
        else:
            return "400 << (Robot en Pause)"

    def down(self):
        if not self.paused:
                if self.state == "TRANSACTION":
                    with maplock:
                        # check if its in maps...
                        robots = (filter(lambda element: element["name"] == self.alias, self.map["robots"]))
                        if len(robots) == 1:
                            # valid movement ( boundaries, obstacles?)
                            if self.validCoords((robots[0]["x"], robots[0]["y"] - 1)):
                                robots[0]["y"] = robots[0]["y"] - 1
                                # ressources found?
                                self.harvestRessources((robots[0]["x"], robots[0]["y"]))
                            else:
                                return "405 Coordonnées Invalides "
                        else:
                            return "403 Non authorisé ! ( Veuiller vous connecter)."
                    print self.map
                    # update map message
                    self.broadcastQueue.put("update")
                    return "270 (" + str(robots[0]["x"]) + "," + str(robots[0]["y"]) + ")"
                else:
                    return "403 Non authorisé ! ( Veuiller vous connecter)."
        else:
            return "400 << (Robot en Pause)"

    def right(self):
        if not self.paused:
            if self.state == "TRANSACTION":
                with maplock:
                    
                    robots = (filter(lambda element: element["name"] == self.alias, self.map["robots"]))
                    if len(robots) == 1:
                        
                        if self.validCoords((robots[0]["x"]+1, robots[0]["y"])):
                            robots[0]["x"]=robots[0]["x"]+1
                           
                            self.harvestRessources((robots[0]["x"], robots[0]["y"]))
                        else:
                            return "405 Coordonnéés invalides "
                    else:
                        return ""
                print self.map
                #Mis à jour des Messages sur la map
                self.broadcastQueue.put("update")
                return "270 ("+ str(robots[0]["x"]) +","+ str(robots[0]["y"]) +")"
            else:
                return "403 Non authorisé ! ( Veuiller vous connecter)."
        else:
            return "400 << (Robot en Pause)"

    def left(self):
        if not self.paused:
            if self.state == "TRANSACTION":
                with maplock:
                 
                    robots = (filter(lambda element: element["name"] == self.alias, self.map["robots"]))
                    if len(robots) == 1:
                   
                        if self.validCoords((robots[0]["x"]-1, robots[0]["y"])):
                            robots[0]["x"]=robots[0]["x"]-1
                         
                            self.harvestRessources((robots[0]["x"], robots[0]["y"]))
                        else:
                            return "405 Coordonnées invalides"
                    else:
                        return "403 Non authorisé ! ( Veuiller vous connecter)."
                print (robots)

                self.broadcastQueue.put("update")
                return "270 ("+ str(robots[0]["x"]) +","+ str(robots[0]["y"]) +")"
            else:
                return "403 Non authorisé ! ( Veuiller vous connecter)."
        else:
            return "400 << (Robot en Pause)"

    def interprete(self, cmd):

        cmd_list = cmd.split()
        #print ("interpreting command "+str(cmd_list[0]))
        #try:
        if cmd_list[0] in self.commands and len(cmd_list)==2:
            print ("length =2")
            return self.commands[cmd_list[0]](cmd_list[1])+"\r\n"
        elif cmd_list[0] in self.commands and len(cmd_list)==3:
            print ("length =3")
            return self.commands[cmd_list[0]](cmd_list[1],cmd_list[2])+"\r\n"
        elif cmd_list[0] in self.commands and len(cmd_list)==4:
            print ("length =4")
            return self.commands[cmd_list[0]](cmd_list[1],cmd_list[2], cmd_list[3])+"\r\n"
        elif cmd_list[0] in self.commands and len(cmd_list)==1:
            print("length = 1")
            return self.commands[cmd_list[0]]()+"\r\n"
        else:
            return "403 Commande non valide \r\n"
        #except:
            #return "403 the server understood the request (Command) but refuses to authorize it \r\n"

    def acceptrequest(self, user, port, protocol):
    
        #vérifier sa liste de requetes clients
        with self.userlock:
            if user in users[self.alias]["requests"]:
            # demande de paramètre cible
                users[user]["mailbox"].put("200 "+users[user]["ip"]+" "+port+" "+protocol+"\r\n")
            #supprimer la requete de sa liste
                del users[self.alias]["requests"][user]
                return "200 requete envoyé !"
            else:
                # envoie à aucun cible
                return "400 (Bad Request) Utilisateur absent"
    
    def refuserequest(self, user):
     
        with self.userlock:
            if user in users[self.alias]["requests"]:
            
                users[user]["mailbox"].put("403 Connection refusée par  "+user+"\r\n")
                del users[self.alias]["requests"][user]
                return "200 requete envoyé !"
            else:
               
                return "400 (Bad Request) Utilisateur absent"

    #Fonction Aide 
    def harvestRessources(self, coords):
     
        for element in self.map["ressources"]:
            if element["x"]==coords[0] and element["y"]==coords[1]:
            
                print ("ressource found! harvesting...")
                with userlock:
                    print (self.users)
                    self.users[self.alias]["ressources"].append(element["name"])
            
                self.map["ressources"].remove(element)
                self.broadcastQueue.put("update")

    def validCoords(self, coords):
        
        print ("checking "+str(coords))
        if(coords[0]>=self.map["dimensions"][0] or coords[0]<0 or
                   coords[1]>=self.map["dimensions"][1] or coords[1]<0):
            return False

        for element in self.map["blockingElements"]:
            print ("verifying "+str(element))
            if element["x"]==coords[0] and element["y"]==coords[1]:
                print("Blocking")
                return False
        return True
