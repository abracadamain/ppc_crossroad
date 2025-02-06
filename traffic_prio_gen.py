from traffic_gen import genere_vehicule, routes, key_north, key_south, key_east, key_west
from coordinator import mq_recup
import sysv_ipc
import numpy as np
import multiprocessing.shared_memory as sm
import os
import signal
import time
import random

#arret clavier
stopped = False

def handler_arret_clavier(sig, frame):
    global stopped
    if sig == signal.SIGINT:
        stopped = True

def mqs_recup() :
    """Création de toutes les mq"""
    mqueues = {
        key_north: mq_recup(key_north),
        key_south: mq_recup(key_south),
        key_east: mq_recup(key_east),
        key_west: mq_recup(key_west)
    }
    return mqueues

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

def genere_traffic_prio(routes, densite, mq) :
    source = random.choice(routes)
    vehicule = genere_vehicule(routes)
    try:
        mq[source].send(vehicule, type=2)  # type 2 : traffic prio
    except sysv_ipc.Error as e:
        print(f"Error sending vehicle to message queue: {e}")
    signal_prio(source)
    time.sleep(densite)

if __name__ == "__main__" :
    mq = mqs_recup()
    signal.signal(signal.SIGINT, handler_arret_clavier)
    while not stopped :
        genere_traffic_prio(routes, 40, mq)
    print("arret traffic prio gen")