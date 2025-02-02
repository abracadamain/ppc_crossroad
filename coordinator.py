import sysv_ipc
import multiprocessing.shared_memory as sm
import numpy as np
import time
import socket
from multiprocessing import Lock
from traffic_gen import mq_creation, key_north, key_south, key_east, key_west

# Configuration du socket TCP
HOST = "127.0.0.1"
PORT = 65432

queues = {
    key_north: mq_creation(key_north),
    key_south: mq_creation(key_south),
    key_east: mq_creation(key_east),
    key_west: mq_creation(key_west)
}

# Chargement de l'état des feux depuis la mémoire partagée
light_state_shm = sm.SharedMemory(name="light_state")
light_state = np.ndarray((4,), dtype=np.bool_, buffer=light_state_shm.buf)

# Définition des directions
right_turns = {key_north: key_east, key_south: key_west, key_east: key_south, key_west: key_north}
left_turns = {key_north: key_west, key_south: key_east, key_east: key_north, key_west: key_south}
opposite = {key_north: key_south, key_south: key_north, key_east: key_west, key_west: key_east}

waiting_vehicles = []  # Liste des véhicules en attente

def send_to_display(message, display_socket):
    """Envoie un message au processus display via socket TCP"""
    with display_socket :
        display_socket.sendall(message.encode())
    
def gestion_priorite(current_light_state):
    """renvoie le prochain véhicule à passer (source, destinations)"""
    global waiting_vehicles
    for key, queue in queues.items():
        try:
            message, msg_type = queue.receive(block=False)
            destination = int(message.decode())

            if msg_type == 2:  # 🚨 Prioritaire : Passe immédiatement
                send_to_display(f"🚨 Prioritaire {key} -> {destination}, passage immédiat.")
                continue 

            elif msg_type == 1:  # 🚗 Normal
                #Remettre dans la file=retourne à la fin! a changer (parcours uniquement les queues correspondantes au current light state)
                if not light_state[keys_to_index(key)]:  # Feu rouge
                    queue.send(message, type=1)  # Remettre dans la file d'attente
                    continue

                if destination == opposite[key]:  # 🚗⬆️ Va tout droit (Priorité 1)
                    send_to_display(f"✅ {key} va tout droit vers {destination}, passage immédiat.")

                elif destination == right_turns[key]:  # 🚗🔄 Tourne à droite (Priorité 2)
                    blocking_left_turns = [v for v in waiting_vehicles if v[1] == left_turns[v[0]]]
                    if blocking_left_turns:
                        send_to_display(f"⛔ {key} tourne à droite vers {destination}, attend véhicule tournant à gauche.")
                        waiting_vehicles.append((key, destination, message))
                    else:
                        send_to_display(f"✅ {key} tourne à droite vers {destination}, passage autorisé.")

                elif destination == left_turns[key]:  # ⬅️ Tourne à gauche (Priorité 3)
                    blocking_vehicles = [
                        v for v in waiting_vehicles 
                        if v[1] in (right_turns[v[0]], opposite[v[0]])  # Droite ou tout droit
                    ]
                    if blocking_vehicles:
                        send_to_display(f"⛔ {key} tourne à gauche vers {destination}, attend priorité.")
                        waiting_vehicles.append((key, destination, message))
                    else:
                        send_to_display(f"✅ {key} tourne à gauche vers {destination}, passage autorisé.")

        except sysv_ipc.BusyError:
            pass  

    # Vérifier les véhicules en attente
    for v in waiting_vehicles[:]:  
        key, destination, message = v
        blocking_vehicles = [
            v for v in waiting_vehicles 
            if v[1] in (right_turns[v[0]], opposite[v[0]])  # Véhicules plus prioritaires
        ]
        if not blocking_vehicles:
            send_to_display(f"🚦 {key} tourne à gauche vers {destination}, passage autorisé.")
            waiting_vehicles.remove(v)

    time.sleep(1)  

def keys_to_index(key):
    """Associe une clé de file de message à l'index du tableau `light_state`"""
    return {100: 0, 200: 1, 300: 2, 400: 3}.get(key, -1)

def gestion_traffic(display_socket):
    "laisse passer les véhicules tant que l'état des lights est le même"
    while True : #gérer arret clavier ?
        current_light_state = light_state
        send_to_display(current_light_state)
        while current_light_state == light_state :
            next_vehicule = gestion_priorite(current_light_state)
            send_to_display(next_vehicule, display_socket)

if __name__ == "__main__":
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as coord_socket:
        coord_socket.bind((HOST, PORT))
        coord_socket.listen(1)
        display_socket, address = coord_socket.accept()
        try:
            print("🚦 Démarrage du coordinateur...")
            gestion_traffic(display_socket)

        except KeyboardInterrupt:
            print("⛔ Arrêt du coordinateur.")
        finally:
            light_state_shm.close()
