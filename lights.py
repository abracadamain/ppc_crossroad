import signal
import os
import time
import multiprocessing
import multiprocessing.shared_memory as sm
import numpy as np
import logging
logging.basicConfig(level=logging.INFO)
#define the signal
SIGNAL_NORTH = signal.SIGUSR1  #north direction priority car
SIGNAL_SOUTH = signal.SIGUSR2  # south
SIGNAL_WEST = signal.SIGRTMIN  # west
SIGNAL_EAST = signal.SIGRTMIN+1  # east

traffic_state = 0 # 0: NS green light, 1: WE green light
priority_mode = 0  # 0: normal state, 1: priority state
priority_source = -1 # record the direction of the priority car (-1: no, 0: N, 1: S, 2: W, 3: E)
try:
    sm.SharedMemory(name="light_state").unlink()
except FileNotFoundError:
    pass  # If it doesn't exist, proceed normally
light_state=sm.SharedMemory(create=True,size=4,name="light_state")#create a shared_memory to send information to process coordinator
data=np.array([True,True,False,False])#initiate the light state as North:green,South:green,West:red,East:red
shared_array=np.ndarray(data.shape,dtype=np.bool_,buffer=light_state.buf)

def display_light():
    global traffic_state
    global priority_mode
    global priority_source
    if priority_mode== 1:
        shared_array[:]=False
        print(priority_source)
        shared_array[priority_source]=True
        logging.info(shared_array)
    else:
        if traffic_state== 0:
            shared_array[:] = [True, True, False, False] 
            logging.info(shared_array)
        else:
            shared_array[:] = [False, False, True, True]
            logging.info(shared_array)


def handle_priority_vehicle(signum, frame):
    global priority_mode
    global priority_source
    priority_mode= 1
    if signum == SIGNAL_NORTH:
        priority_source= 0
    elif signum == SIGNAL_SOUTH:
        priority_source= 1
    elif signum == SIGNAL_WEST:
        priority_source= 2
    elif signum == SIGNAL_EAST:
        priority_source= 3
    display_light()
    time.sleep(5)      
    priority_mode= 0  #After the priority car cross the road,we switch the priority mode to normal
    display_light()


def setup_signal_handlers():
    signal.signal(SIGNAL_NORTH, handle_priority_vehicle)
    signal.signal(SIGNAL_SOUTH, handle_priority_vehicle)
    signal.signal(SIGNAL_WEST, handle_priority_vehicle)
    signal.signal(SIGNAL_EAST, handle_priority_vehicle)


def normal_light_change():
    global traffic_state
    global priority_mode
    
    while True:         
        if priority_mode== 0:
            time.sleep(10)      
            traffic_state= 1 - traffic_state #change light state every 30 seconds
        display_light()


def main():
    process_id = os.getpid()
    try :
        lights_pid = sm.SharedMemory(create=True, size=4, name="lights_pid")
    except FileExistsError:
        lights_pid = sm.SharedMemory(name="lights_pid")   
    pid_array = np.ndarray((1,), dtype=np.int32, buffer=lights_pid.buf)
    pid_array[0] = process_id #store process pid in shared memory 

    setup_signal_handlers()

    light_process = multiprocessing.Process(target=normal_light_change)
    light_process.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Arrêt du processus des feux.")
    finally:
        light_process.terminate()
        light_process.join()
        for shm in [light_state, lights_pid]:
            try:
                shm.close()
                shm.unlink()
            except FileNotFoundError:
                pass
if __name__ == "__main__":
    main()
