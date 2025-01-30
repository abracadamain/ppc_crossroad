import signal
import os
import time
import multiprocessing

#define the signal
SIGNAL_NORTH = signal.SIGUSR1  #north direction priority car
SIGNAL_SOUTH = signal.SIGUSR2  # south
SIGNAL_WEST = signal.SIGRTMIN  # west
SIGNAL_EAST = signal.SIGRTMIN+1  # east

traffic_state = multiprocessing.Value('i', 0)  # 0: NS green light, 1: WE green light
priority_mode = multiprocessing.Value('i', 0)  # 0: normal state, 1: priority state
priority_direction = multiprocessing.Value('i', -1)  # record the direction of the priority car (-1: no, 0: N, 1: S, 2: W, 3: E)


def display_light():
    with traffic_state.get_lock(), priority_mode.get_lock(), priority_direction.get_lock():
        if priority_mode.value == 1:
            directions = ["north", "south", "west", "east"]
            print(f"[{time.strftime('%H:%M:%S')}] enter priority state：green light on the {directions[priority_direction.value]} ，the other direction is red")
        else:
            if traffic_state.value == 0:
                print(f"[{time.strftime('%H:%M:%S')}] normal state：North-South green light, West-East red light.")
            else:
                print(f"[{time.strftime('%H:%M:%S')}] normal state：North-South red light, West-East green light.")


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
        time.sleep(10) 
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

    
    while True:
        time.sleep(1)

if __name__ == "__main__":
    main()
