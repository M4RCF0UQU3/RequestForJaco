import socket, threading, sys, re, json, random, ast, time, Queue, datetime
import creation_map, init_config, mon_socket, thread_debut, thread_diffusion, thread_envoye 
if __name__ == '__main__':

    
    config = init_config.loadConfig()

   
    users = {}

   
    mapsize = 10
    rd = 0.1
    bd = 0.2
    try:
        if "size" in config:
            mapsize = int(config["size"])
        if "ressourcedensity" in config:
            rd = float(config["ressourcedensity"])
        if "blockdensity" in config:
            bd = float(config["blockdensity"])
    finally:
        map = createMap(mapsize,bd, rd)
        maplock = threading.Lock()
        userlock = threading.Lock()

        
        broadcastMailbox = Queue.Queue()
        broadcastActive = threading.Event()
        ThreadDiffusion = thread_diffusion.ThreadDiffusion(users, userlock, broadcastActive, broadcastMailbox, map, maplock)

       
        logQueue = Queue.Queue()
        logActive = threading.Event()
        ThreadDebut = thread_debut.ThreadDebut(logActive,logQueue,config["path"])
        ThreadDebut.start()

        host ='localhost'

        logQueue.put("\n"+str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')) +
                     " server started @ "+host+" port "+str(config["port"]))

        threads = []
        events = []
        tcpsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        tcpsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        tcpsock.bind((host,int(config["port"])))
        try:
            ThreadDiffusion.start()
            print ("En attente de Connection  " + str(config["port"]) + "...")

            while True:
                try:
                    tcpsock.listen(4)
                    #pass clientsock to the ClientThread thread object being created
                    (clientsock, (ip, port)) = tcpsock.accept()
                    print ("Client [OK] !.")
                    clientsock.settimeout(60)
                    clientsock.setblocking(0)
                    ev = threading.Event()
                    newthread = mon_socket.SocketThread(ip, port, clientsock, map, users, maplock,
                                             userlock, broadcastMailbox, ev, logQueue)
                    print ("starting thread...")
                    newthread.start()
                    print ("thread started...")
                    threads.append(newthread)
                    events.append(ev)
                except KeyboardInterrupt:
                    break
        finally:

            for ev in events:
                ev.set()
            for t in threads:
                t.join()

            logQueue.put("\n" + str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')) +
                         " server halted @ " + host + " port " + str(config["port"]))

            print("Diffusioin Thread terminée !")
            broadcastActive.set()
            ThreadDiffusion.join()
            print("Connection Thread terminée ! ")
            logActive.set()
            ThreadDebut.join()
            tcpsock.close()
            print ("closed server")