import socket
import multiprocessing.shared_memory as sm
import numpy as np
import time

# Configuration du socket pour recevoir les infos de `coordinator.py`
HOST = 'local_host'  
PORT = 6666       



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
                
            except socket.timeout:
                pass  

            time.sleep(1)

if __name__ == "__main__":
    try:
        display()
    except KeyboardInterrupt:
        print("Arrêt du processus d'affichage.")