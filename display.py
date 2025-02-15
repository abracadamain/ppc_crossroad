import socket
import numpy as np
import time
from coordinator import right_turns, left_turns
# Configuration du socket pour recevoir les infos de coordinator.py
HOST = "127.0.0.1"
PORT = 65432
KEY_TO_NAME = {100: 'north', 200: 'south', 300:'east', 400:'west'}
def connect_to_server():
    """Attempts to connect to the coordinator server with retries."""
    while True:
        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.settimeout(5)  # Set a timeout for connection attempts
            client_socket.connect((HOST, PORT))
            print("Connected to the server")
            return client_socket
        except (socket.error, ConnectionRefusedError) as err:
            print(f"Connection failed: {err}, retrying in 5 seconds...")
            time.sleep(2)  # Wait before retrying
def display():
    client_socket = connect_to_server()
    while True:
        try:
            
            data = client_socket.recv(1024)  # Réception des données
            if not data:
                print("Server closed the connection.")
                break
            if data.startswith(b"L:"):
            # Essayer de décoder le message comme un tableau d'entiers uint8
                decode_message = np.frombuffer(data[2:], dtype=np.uint8)
                for i in range(4):
                    direction = ["north", "south", "west", "east"]
                    if decode_message[i] == 1:
                        print(f"Green light on the {direction[i]}")
                    else:
                        print(f"Red light on the {direction[i]}")
            
            elif data.startswith(b"C:"):    
                data = data[2:].decode().strip()
                #print(f"Received data: {data}") #debug
                source, destination, prio = data.split(",")
                source = int(source)
                destination = int(destination)
                if prio == 'True':
                    prio = 'priority'
                else :
                    prio = 'normal'
                if destination == right_turns[source] :
                    print(f"Car {prio} coming from the {KEY_TO_NAME[source]} turns right to {KEY_TO_NAME[destination]}")
                elif destination == left_turns[source] :
                    print(f"Car {prio} coming from the {KEY_TO_NAME[source]} turns left to {KEY_TO_NAME[destination]}")
                else :
                    print(f"Car {prio} coming from the {KEY_TO_NAME[source]} goes straight to {KEY_TO_NAME[destination]}")
            else:
                print("Erreur: Données reçues non reconnues.")
        except (socket.timeout, ConnectionResetError, BrokenPipeError):
            print("Connection lost, reconnecting...")
            client_socket.close()
            client_socket = connect_to_server()
        except Exception as err:
            print(f"Unexpected error: {err}")
            time.sleep(2)
if __name__ == "__main__":
    try:
        display()
    except KeyboardInterrupt:
        print("Arrêt du processus d'affichage.")