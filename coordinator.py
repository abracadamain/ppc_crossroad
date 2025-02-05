import sysv_ipc
import multiprocessing.shared_memory as sm
import numpy as np
import time
import socket
from multiprocessing import Lock
from traffic_gen import key_north, key_south, key_east, key_west
import signal
import select

#arret clavier
stopped = False

def handler_arret_clavier(sig, frame):
    global stopped
    if sig == signal.SIGINT:
        stopped = True

# Configuration du socket TCP
HOST = "127.0.0.1"
PORT = 65432

def mq_creation(key) :
    try:
        mq = sysv_ipc.MessageQueue(key, 0)
        return mq
    except sysv_ipc.ExistentialError:
        print(f"Message queue with key {key} doesn't exist.")
        return sysv_ipc.MessageQueue(key, sysv_ipc.IPC_CREX) # on recrée la queue
    
mqueues = {
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

def send_voiture_to_display(message, display_socket):
    """Envoie un message au processus display via socket TCP"""
    if message is not None and display_socket:
        try:
            message="C:"+message
            print(f"Sending vehicle info: {message}")
            display_socket.sendall(message.encode())
        except OSError as err:
            print(f"Error sending vehicle information:{err}")

def send_light_to_display(message, display_socket):
    """Envoie un message au processus display via socket TCP"""
    if display_socket:
        try:
            message="L:"+message
            display_socket.sendall(message.astype(np.uint8).tobytes())
        except OSError as err:
             print(f"Error sending light information:{err}")


def format_message(source, destination, prio=False) :
    """définit le format du message(véhicule) à envoyer au display"""
    return str(source) + "," + destination + "," + str(prio)
    
def gestion_priorite(current_light_state):
    """renvoie le prochain véhicule à passer (source, destinations, prio)"""
    global waiting_vehicles
    for key, mqueue in mqueues.items():
        if current_light_state[keys_to_index(key)] : #si cette mqueue a le feu vert(True)
            try:
                message, msg_type = mqueue.receive(block=False)
                destination = message.decode()
                if message != None :
                    if msg_type == 2:  # Prioritaire : Passe immédiatement
                        return format_message(key, destination, True)

                    elif msg_type == 1:  # Normal car
                        if destination != left_turns[key]:  #Va tout droit (Priorité 1)
                            return format_message(key, destination, False)
                        elif destination == left_turns[key]:  # Tourne à gauche (Priorité 3)
                            waiting_vehicles.append((key, destination)) #en attente, on verif d'abord que les véhicules d'en face passent d'abord
                            """
                            blocking_vehicles = [
                                v for v in waiting_vehicles 
                                if v[1] in (right_turns[v[0]], opposite[v[0]])  # Droite ou tout droit
                            ]
                            if blocking_vehicles:
                            # attend priorité
                                waiting_vehicles.append((key, destination, message))
                            else:
                                send_to_display(f"✅ {key} tourne à gauche vers {destination}, passage autorisé.")
                            """

            except sysv_ipc.BusyError:
                pass  

    # Vérifier les véhicules en attente
    for v in waiting_vehicles[:]:  
        key, destination = v
        """
        blocking_vehicles = [
            v for v in waiting_vehicles 
            if v[1] in (right_turns[v[0]], opposite[v[0]])  # Véhicules plus prioritaires
        ]
        if not blocking_vehicles:"""
        waiting_vehicles.remove(v)
        return format_message(key, destination) # passage autorisé.

    time.sleep(1)  

def keys_to_index(key):
    """Associe une clé de file de message à l'index du tableau `light_state`"""
    return {100: 0, 200: 1, 300: 2, 400: 3}.get(key, -1)

def gestion_traffic(display_socket):
    "laisse passer les véhicules tant que l'état des lights est le même"
    current_light_state = light_state
    print(current_light_state)
    try :
        send_light_to_display(current_light_state, display_socket)
    except OSError as err:
        print(f"Erreur lors de l'envoi du véhicule : {err}")
    while current_light_state.all() == light_state.all() :
        next_vehicule = gestion_priorite(current_light_state)
        if next_vehicule != None:
            print('prochain véhicule' + next_vehicule)
            try:
                send_voiture_to_display(next_vehicule, display_socket)
            except OSError as err:
                print(f"Erreur lors de l'envoi du véhicule : {err}")
                break  

if __name__ == "__main__":
    signal.signal(signal.SIGINT, handler_arret_clavier)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as coord_socket:
        coord_socket.setblocking(False)
        coord_socket.bind((HOST, PORT))
        coord_socket.listen(1)
        while not stopped :
            readable, writable, error = select.select([coord_socket], [], [], 1)
            if coord_socket in readable:
                display_socket, address = coord_socket.accept()
                print("🚦 Démarrage du coordinateur...")
                try:
                    gestion_traffic(display_socket)
                except Exception as err:
                    print(f"Erreur dans gestion_traffic : {err}")

        print("⛔ Arrêt du coordinateur.")
        light_state_shm.close()
