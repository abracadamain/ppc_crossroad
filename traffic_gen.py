import sysv_ipc
import random
import time
import signal

#arret clavier
stopped = False

def handler_arret_clavier(sig, frame):
    global stopped
    if sig == signal.SIGINT:
        stopped = True

key_north = 100
key_south = 200
key_east = 300
key_west = 400

routes = [key_north, key_south, key_east, key_west]

# ! CREAT crée la queue mais si existe déjà réutilise : attention a supprimer à la fin
def mq_creation(key) :
    try:
        mq = sysv_ipc.MessageQueue(key, sysv_ipc.IPC_CREX)
        return mq
    except sysv_ipc.ExistentialError:
        print(f"Message queue with key {key} already exists.")
        sysv_ipc.MessageQueue(key).remove()
        return sysv_ipc.MessageQueue(key, sysv_ipc.IPC_CREX) # on recrée la queue

def genere_vehicule(source, destinations) :
    print(source)
    destination = random.choice(destinations)
    vehicule = (str(destination)).encode()
    print(vehicule)
    return vehicule

def genere_traffic(routes, densite) :
    source = random.choice(routes)
    mq = mq_creation(source)
    vehicule = genere_vehicule(source, routes)
    try:
        mq.send(vehicule, type=1)  # type 1 : traffic normal
    except sysv_ipc.Error as e:
        print(f"Error sending vehicle to message queue: {e}")
    time.sleep(densite)

if __name__ == "__main__" :
    signal.signal(signal.SIGINT, handler_arret_clavier)
    while not stopped :
        genere_traffic(routes, 20)
    print("arret traffic gen")
    for key in routes :
        try:
            mq_creation(key).remove()
        except sysv_ipc.Error as e:
            print(f"Error removing message queue: {e}")