import socket
import numpy as np
import time

# Configuration du socket pour recevoir les infos de coordinator.py
HOST = "127.0.0.1"
PORT = 65432
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
                print(f"Received data: {data}")
                source, destination, prio = data.split(",")
                if prio==True:
                    prio_texte="priority"
                else:
                    prio_texte="normal"

                # Traitement des messages pour les directions
                if source == "north":
                    if destination == "south":
                        print(f"{prio_texte} car coming from the {source} goes straight to {destination}")
                    elif destination == "east":
                        print(f"{prio_texte} car coming from the {source} turns right to {destination}")
                    else:
                        print(f"{prio_texte} car coming from the {source} turns left to {destination}")
                elif source == "south":
                    if destination == "north":
                        print(f"{prio_texte} car coming from the {source} goes straight to {destination}")
                    elif destination == "west":
                        print(f"{prio_texte} car coming from the {source} turns right to {destination}")
                    else:
                        print(f"{prio_texte} car coming from the {source} turns left to {destination}")
                elif source == "east":
                    if destination == "west":
                        print(f"{prio_texte} car coming from the {source} goes straight to {destination}")
                    elif destination == "south":
                        print(f"{prio_texte} car coming from the {source} turns right to {destination}")
                    else:
                        print(f"{prio_texte} car coming from the {source} turns left to {destination}")
                else:
                    if destination == "east":
                        print(f"{prio_texte} car coming from the {source} goes straight to {destination}")
                    elif destination == "north":
                        print(f"{prio_texte} car coming from the {source} turnsn3 lights.py right to {destination}")
                    else:
                        print(f"{prio_texte} car coming from the {source} turns left to {destination}")
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