from traffic_gen import genere_vehicule, routes, key_north, key_south, key_east, key_west
from coordinator import mq_recup
import sysv_ipc
import numpy as np
import multiprocessing.shared_memory as sm
import os
import signal
import time
import random
import sys

#arret clavier
stopped = False

def handler_arret_clavier(sig, frame):
    global stopped
    if sig == signal.SIGINT:
        stopped = True

def mqs_recup() :
    """Récuperation de toutes les mq"""
    mqueues = {
        key_north: mq_recup(key_north),
        key_south: mq_recup(key_south),
        key_east: mq_recup(key_east),
        key_west: mq_recup(key_west)
    }
    return mqueues

def signal_prio(source) :
    global lights_pid_shm
    try:
        lights_pid_shm = sm.SharedMemory(name="lights_pid")
        lights_pid = np.ndarray((1,), dtype=np.int32, buffer=lights_pid_shm.buf)
    except FileNotFoundError:
        print("Shared memory 'lights_pid' not found. Ensure traffic light process is running.")
        sys.exit(1)  # Exit if shared memory is missing
    if source == 100 :
        sig = signal.SIGUSR1 #north
    elif source == 200 :
        sig = signal.SIGUSR2 #south
    elif source == 300 :
        sig = signal.SIGRTMIN #east
    else :
        sig = signal.SIGRTMIN+1 #west
    try:
        os.kill(lights_pid[0], 0)  # Check if process is alive
        os.kill(lights_pid[0], sig)
    except ProcessLookupError:
        print(f"Traffic light process with PID {lights_pid[0]} not found. Is it running?")
        sys.exit(1)

def genere_traffic_prio(routes, densite, mq) :
    source = random.choice(routes)
    vehicule = genere_vehicule(source, routes)
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
    try:
        lights_pid_shm.close()
    except FileNotFoundError:
        pass  # Ignore if already unlinked
