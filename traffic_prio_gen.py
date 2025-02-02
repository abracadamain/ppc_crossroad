from traffic_gen import genere_traffic, routes
import numpy as np
import multiprocessing.shared_memory as sm
import os
import signal

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
    os.kill(lights_pid, sig)

if __name__ == "__main__" :
    genere_traffic(routes, 5, True)