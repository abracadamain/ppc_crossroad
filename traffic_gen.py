import sysv_ipc
import random
import time

key_north = 100
key_south = 200
key_east = 300
key_west = 400

# ! CREAT crée la queue mais si existe déjà réutilise : attention a supprimer à la fin
def mq_creation(key) :
    mq = sysv_ipc.MessageQueue(key, sysv_ipc.IPC_CREAT)
    return mq

def genere_vehicule(source, destinations) :
    print(source)
    destinations.remove(source) #demi-tour non autorisé
    destination = random.choice(destinations)
    print(vehicule_prio)
    vehicule_prio = (str(destination)).encode()
    return vehicule_prio

def genere_traffic(routes, densite) :
    while True : #ajouter condition d'arret et supprimer mq
        source = random.choice(routes)
        mq = mq_creation(source)
        vehicule_prio = genere_vehicule(source, routes)
        mq.send(vehicule_prio, type=1) #type 1 : traffic normal
        time.sleep(densite)

if __name__ == "__main__" :
    routes = [key_north, key_south, key_east, key_west]
    genere_traffic(routes, 5)