from traffic_gen import genere_vehicule, mq_creation, handler_arret_clavier, routes, stopped
import numpy as np
import multiprocessing.shared_memory as sm
import os
import signal
import time
import random

def signal_prio(source) :
    lights_pid_shm = sm.SharedMemory(name="lights_pid")
    lights_pid = np.ndarray((1,), dtype=np.int32, buffer=lights_pid_shm.buf)
    if source == 100 :
        sig = signal.SIGUSR1 #north
    elif source == 200 :
        sig = signal.SIGUSR2 #south
    elif source == 300 :
        sig = signal.SIGRTMIN #east
    else :
        sig = signal.SIGRTMIN+1 #west
    os.kill(lights_pid[0], sig)

def genere_traffic_prio(routes, densite) :
    source = random.choice(routes)
    mq = mq_creation(source)
    vehicule = genere_vehicule(source, routes)
    mq.send(vehicule, type=2) #type 2 : traffic prio
    signal_prio(source)
    time.sleep(densite)

if __name__ == "__main__" :
    signal.signal(signal.SIGINT, handler_arret_clavier)
    while not stopped :
        genere_traffic_prio(routes, 5)
    print("arret traffic prio gen")
    for key in routes :
        mq_creation(key).remove()