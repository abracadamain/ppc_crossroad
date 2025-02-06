import sysv_ipc
import random
import time
import signal

key_north = 100
key_south = 200
key_east = 300
key_west = 400

routes = [key_north, key_south, key_east, key_west]

#arret clavier
stopped = False

def handler_arret_clavier(sig, frame):
    global stopped
    if sig == signal.SIGINT:
        stopped = True

def mq_creation(key) :
    try:
        mq = sysv_ipc.MessageQueue(key, sysv_ipc.IPC_CREX)
        return mq
    except sysv_ipc.ExistentialError: 
        print(f"Message queue with key {key} already exists.")
        sysv_ipc.MessageQueue(key).remove()
        return sysv_ipc.MessageQueue(key, sysv_ipc.IPC_CREX) # on recrée la queue
    
def mqs_creation() :
    """Création de toutes les mq"""
    mqueues = {
        key_north: mq_creation(key_north),
        key_south: mq_creation(key_south),
        key_east: mq_creation(key_east),
        key_west: mq_creation(key_west)
    }
    return mqueues

def genere_vehicule(destinations) :
    destination = random.choice(destinations)
    vehicule = (str(destination)).encode()
    print(vehicule)
    return vehicule

def genere_traffic(routes, densite, mq) :
    source = random.choice(routes)
    print(source)
    vehicule = genere_vehicule(routes)
    try:
        mq[source].send(vehicule, type=1)  # type 1 : traffic normal
    except sysv_ipc.Error as e:
        print(f"Error sending vehicle to message queue: {e}")
    time.sleep(densite)

if __name__ == "__main__" :
    mq = mqs_creation()
    signal.signal(signal.SIGINT, handler_arret_clavier)
    while not stopped :
        genere_traffic(routes, 2, mq)
    print("arret traffic gen")
    for key in routes :
        try:
             sysv_ipc.MessageQueue(key).remove()
        except sysv_ipc.Error as e:
            print(f"Error removing message queue: {e}")