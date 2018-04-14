import socket, threading, sys, re, json, random, ast, time, Queue, datetime

def createMap(size, blockingElements, ressources):
    """
    :param size: size of map
    blockingElements: percentage as float between 0 and 1 of blocking elements covering the map
    ressources: percentage as float between 0 and 1 of ressources covering the map.
    blockingElements + ressources must be < 1
    :return: a dictionnary with dimensions, blocking elements, ressources and robots.
    the latter is an initially empty array.
    """
    if blockingElements+ressources>1.0:
        print ("blocking elements and ressources together cant be higher than 1.0")
        exit(1)
    blocktypes = ["rock", "plant", "hole"]
    ressourcetypes = ["Gold", "Diamant"]
    map = {"dimensions": [size, size], "blockingElements":[], "ressources": [], "robots":[]}
    #Create blocking elements on map....
    #make a list of distinct coords
    print ("Populating map with " +str(round(size*size*blockingElements))+ " blocking Elements...")
    coords = set()
    while len(coords) < int(round(size*size*blockingElements)):
        coords.add((random.randint(0, size), random.randint(0, size)))
    for coordinate in coords:
        map["blockingElements"].append({"name": blocktypes[random.randint(0,len(blocktypes)-1)], "x":coordinate[0], "y":coordinate[1]})
    #Create Ressources for map...
    # make a list of distinct coords: copy coords, make it until size + size*ressources and the diff coords
    ress_coords = coords.copy()
    print ("Populating map with " + str(round(size*size*ressources)) + " ressources...")
    while len(ress_coords) < int(round(size*size*blockingElements)+round(size*size*ressources)):
        ress_coords.add((random.randint(0, size), random.randint(0, size)))
    ress_coords = ress_coords.difference(coords)
    for coordinate in ress_coords:
        map["ressources"].append({"name": ressourcetypes[random.randint(0,len(ressourcetypes)-1)], "x":coordinate[0], "y":coordinate[1]})
    print ("Map Creation Finished")
    return map
