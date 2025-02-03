import socket
import multiprocessing.shared_memory as sm
import numpy as np
import time

# Configuration du socket pour recevoir les infos de `coordinator.py`
HOST = "127.0.0.1"
PORT = 65432



def display():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        client_socket.connect((HOST, PORT))  # Se connecter au serveur
        data = client_socket.recv(1024)  
        light_state = sm.SharedMemory(name="light_state")
        shared_array = np.ndarray((4,), dtype=np.bool_, buffer=light_state.buf)

        while True:
            # a corriger
            for i in range (0,4):
                if shared_array[i]:
                    if i==0:
                        print("Green light on the north")
                    elif  i==1:
                        print("Green light on the south")
                    elif i==2:
                        print("Green light on the west")
                    else:
                        print("Green light on the east")   
                else:
                    if i==0:
                        print("Red light on the north")
                    elif  i==1:
                        print("Red light on the south")
                    elif i==2:
                        print("Red light on the west")
                    else:
                        print("Red light on the east")   
            # Recevoir et afficher les informations envoyées par coordinator
            try:
                client_socket.settimeout(2)  
                data, _ = client_socket.recvfrom(1024)  
                data=data.decode()
                source,destination,prio=data.split(",")
                if source == "north":
                    if destination == "south":
                        print("car {prio} comming from the {source} go straight to {destination}")
                    elif destination =="east":
                        print("car {prio} comming from the {source} turns right to {destination}")
                    else:
                        print("car {prio} comming from the {source} turns left to {destination}")
                elif source == "south":
                    if destination == "north":
                        print("car {prio} comming from the {source} go straight to {destination}")
                    elif destination =="west":
                        print("car {prio} comming from the {source} turns right to {destination}")
                    else:
                        print("car {prio} comming from the {source} turns left to {destination}")
                elif source == "east":
                    if destination == "west":
                        print("car {prio} comming from the {source} go straight to {destination}")
                    elif destination =="south":
                        print("car {prio} comming from the {source} turns right to {destination}")
                    else:
                        print("car {prio} comming from the {source} turns left to {destination}")
                else: 
                    if destination == "east":
                        print("car {prio} comming from the {source} go straight to {destination}")
                    elif destination =="north":
                        print("car {prio} comming from the {source} turns right to {destination}")
                    else:
                        print("car {prio} comming from the {source} turns left to {destination}")
            except socket.timeout:
                pass  

            time.sleep(2)

if __name__ == "__main__":
    try:
        display()
    except KeyboardInterrupt:
        print("Arrêt du processus d'affichage.")