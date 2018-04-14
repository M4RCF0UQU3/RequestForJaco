import sys

def loadConfig():
    """
    loads a config file. Must be of this structure:
    <property1> <value1>
    <property2> <value2>
    :return: a dictionnary of the file's content.
    The following keys are set by default: port, path
    """
    config = {"port": 8532, "path":""}
    with open("spaceX.conf", "r") as r:
        for line in r:
            conf = line.split()
            config[conf[0]] = conf[1]
    if (len(sys.argv) >= 2):
        config["port"] = sys.argv[1]
    return config