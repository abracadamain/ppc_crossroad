import random
import time
from traffic_gen import mq_creation, genere_vehicule

key_north = 100
key_south = 200
key_east = 300
key_west = 400

def genere_traffic_prio(routes, densite) :
    while True :
        source = random.choice(routes)
        mq = mq_creation(int(source))
        vehicule_prio = genere_vehicule(source, routes)
        mq.send(vehicule_prio, type=2) #type 2 : traffic prio
        time.sleep(densite)

if __name__ == "__main__" :
    routes = [key_north, key_south, key_east, key_west]
    genere_traffic_prio(routes, 5)
    
    #ajouter envoit signal (pid récuperable ou enfant obligé?)