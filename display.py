import socket
import numpy as np
import time

# Configuration du socket pour recevoir les infos de coordinator.py
HOST = "127.0.0.1"
PORT = 65432

def display():
    while True:
        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect((HOST, PORT))  # Se connecter au serveur
            
            data = client_socket.recv(1024)  # Réception des données
            
            try:
                # Essayer de décoder le message comme un tableau d'entiers uint8
                decode_message = np.frombuffer(data, dtype=np.uint8)
                for i in range(4):
                    direction = ["north", "south", "west", "east"]
                    if decode_message[i] == 1:
                        print(f"Green light on the {direction[i]}")
                    else:
                        print(f"Red light on the {direction[i]}")
            except Exception as e:
                # Si le décodage échoue, on tente de traiter le message comme une chaîne de caractères
                try:
                    data = data.decode()
                    source, destination, prio = data.split(",")

                    # Traitement des messages pour les directions
                    if source == "north":
                        if destination == "south":
                            print(f"Car {prio} coming from the {source} goes straight to {destination}")
                        elif destination == "east":
                            print(f"Car {prio} coming from the {source} turns right to {destination}")
                        else:
                            print(f"Car {prio} coming from the {source} turns left to {destination}")
                    elif source == "south":
                        if destination == "north":
                            print(f"Car {prio} coming from the {source} goes straight to {destination}")
                        elif destination == "west":
                            print(f"Car {prio} coming from the {source} turns right to {destination}")
                        else:
                            print(f"Car {prio} coming from the {source} turns left to {destination}")
                    elif source == "east":
                        if destination == "west":
                            print(f"Car {prio} coming from the {source} goes straight to {destination}")
                        elif destination == "south":
                            print(f"Car {prio} coming from the {source} turns right to {destination}")
                        else:
                            print(f"Car {prio} coming from the {source} turns left to {destination}")
                    else:
                        if destination == "east":
                            print(f"Car {prio} coming from the {source} goes straight to {destination}")
                        elif destination == "north":
                            print(f"Car {prio} coming from the {source} turns right to {destination}")
                        else:
                            print(f"Car {prio} coming from the {source} turns left to {destination}")
                except ValueError:
                    print("Erreur : format des données incorrect.")
            time.sleep(2)

        except socket.error as err:
            print(f"Erreur de connexion au serveur : {err}")
            time.sleep(2)  # Réessayer après une courte pause

if __name__ == "__main__":
    try:
        display()
    except KeyboardInterrupt:
        print("Arrêt du processus d'affichage.")