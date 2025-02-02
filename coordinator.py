import sysv_ipc
import multiprocessing.shared_memory as sm
import numpy as np
import time
import socket

# Configuration du socket TCP
HOST = "127.0.0.1"
PORT = 65432

# Clés des files de messages
key_north = 100
key_south = 200
key_east = 300
key_west = 400

queues = {
    key_north: sysv_ipc.MessageQueue(key_north, sysv_ipc.IPC_CREAT),
    key_south: sysv_ipc.MessageQueue(key_south, sysv_ipc.IPC_CREAT),
    key_east: sysv_ipc.MessageQueue(key_east, sysv_ipc.IPC_CREAT),
    key_west: sysv_ipc.MessageQueue(key_west, sysv_ipc.IPC_CREAT)
}

# Chargement de l'état des feux depuis la mémoire partagée
light_state_shm = sm.SharedMemory(name="light_state")
light_state = np.ndarray((4,), dtype=np.bool_, buffer=light_state_shm.buf)

# Définition des directions
right_turns = {key_north: key_east, key_south: key_west, key_east: key_south, key_west: key_north}
left_turns = {key_north: key_west, key_south: key_east, key_east: key_north, key_west: key_south}
opposite = {key_north: key_south, key_south: key_north, key_east: key_west, key_west: key_east}

waiting_vehicles = []  # Liste des véhicules en attente

def send_to_display(message):
    """Envoie un message au processus display via socket TCP"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((HOST, PORT))
            s.sendall(message.encode())
    except ConnectionRefusedError:
        print("⚠️ Impossible de se connecter au display. Vérifiez qu'il est bien démarré.")

def process_traffic():
    global waiting_vehicles
    while True:
        for key, queue in queues.items():
            try:
                message, msg_type = queue.receive(block=False)
                destination = int(message.decode())

                if msg_type == 2:  # 🚨 Prioritaire : Passe immédiatement
                    send_to_display(f"🚨 Prioritaire {key} -> {destination}, passage immédiat.")
                    continue 

                elif msg_type == 1:  # 🚗 Normal
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

if __name__ == "__main__":
    try:
        print("🚦 Démarrage du coordinateur...")
        process_traffic()
    except KeyboardInterrupt:
        print("⛔ Arrêt du coordinateur.")
    finally:
        light_state_shm.close()
