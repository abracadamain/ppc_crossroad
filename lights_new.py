import signal
import os
import time
import multiprocessing
import multiprocessing.shared_memory as sm
import numpy as np
#define the signal
SIGNAL_NORTH = signal.SIGUSR1  #north direction priority car
SIGNAL_SOUTH = signal.SIGUSR2  # south
SIGNAL_WEST = signal.SIGRTMIN  # west
SIGNAL_EAST = signal.SIGRTMIN+1  # east

traffic_state = multiprocessing.Value('i', 0) # 0: NS green light, 1: WE green light
priority_mode = multiprocessing.Value('i', 0)  # 0: normal state, 1: priority state
priority_source = multiprocessing.Value('i', -1)  # record the direction of the priority car (-1: no, 0: N, 1: S, 2: W, 3: E)
light_state=sm.SharedMemory(create=True,size=4,name=light_state)
data=np.array([True,True,False,False])
shared_array=np.ndarray(data.shape,dtype=np.bool_,buffer=light_state.buf)

def display_light():
    with traffic_state.get_lock(), priority_mode.get_lock(), priority_direction.get_lock():
        if priority_mode.value == 1:
            directions = ["north", "south", "west", "east"]
            data[:]=False
            data[priority_source.value]=True

        else:
            if traffic_state.value == 0:
                shared_array[:] = [True, True, False, False] 
            else:
                shared_array[:] = [False, False, True, True]


def handle_priority_vehicle(signum, frame):
    with priority_mode.get_lock(), priority_direction.get_lock():
        priority_mode.value = 1
        if signum == SIGNAL_NORTH:
            priority_direction.value = 0
        elif signum == SIGNAL_SOUTH:
            priority_direction.value = 1
        elif signum == SIGNAL_WEST:
            priority_direction.value = 2
        elif signum == SIGNAL_EAST:
            priority_direction.value = 3
    display_light()
    time.sleep(5)  
    with priority_mode.get_lock():
        priority_mode.value = 0  
    display_light()


def setup_signal_handlers():
    signal.signal(SIGNAL_NORTH, handle_priority_vehicle)
    signal.signal(SIGNAL_SOUTH, handle_priority_vehicle)
    signal.signal(SIGNAL_WEST, handle_priority_vehicle)
    signal.signal(SIGNAL_EAST, handle_priority_vehicle)


def normal_light_change():
    while True:
        time.sleep(30) 
        with priority_mode.get_lock():
            if priority_mode.value == 0:  
                with traffic_state.get_lock():
                    traffic_state.value = 1 - traffic_state.value  
                display_light()


def main():
    process_id = os.getpid()
    print(f"Lights process started with PID: {process_id}")

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
        light_state.close()
        light_state.unlink()
if __name__ == "__main__":
    main()
