import sysv_ipc
import random

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
    vehicule_prio = (destination).encode()
    return vehicule_prio

def genere_traffic_prio(routes) :
    source = random.choice(routes)
    mq = mq_creation(int(source))
    vehicule_prio = genere_vehicule(source, routes)
    mq.send(vehicule_prio)

routes = [key_north, key_south, key_east, key_west]
routes = [str(r) for r in routes]
genere_traffic_prio(routes)
#ajouter type (prio ou normal) et ajouter envoit signal (pid récuperable ou enfant obligé?)