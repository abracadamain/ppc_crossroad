import sysv_ipc
import multiprocessing.shared_memory as sm
import numpy as np
import time
import socket
from traffic_gen import key_north, key_south, key_east, key_west
import signal
import select

#arret clavier
stopped = False

def handler_arret_clavier(sig, frame):
    global stopped
    if sig == signal.SIGINT:
        stopped = True
    try:
        light_state_shm.close()
        light_state_shm.unlink()
    except FileNotFoundError:
        pass
    if coord_socket:
        coord_socket.close()
    if display_socket:
        display_socket.close()

# Configuration du socket TCP
HOST = "127.0.0.1"
PORT = 65432

def mq_recup(key) :
    try:
        mq = sysv_ipc.MessageQueue(key, 0)
        return mq
    except sysv_ipc.ExistentialError:
        print(f"Message queue with key {key} doesn't exist.")
        return sysv_ipc.MessageQueue(key, sysv_ipc.IPC_CREX) # on recrée la queue
    
mqueues = {
    key_north: mq_recup(key_north),
    key_south: mq_recup(key_south),
    key_east: mq_recup(key_east),
    key_west: mq_recup(key_west)
}

# Chargement de l'état des feux depuis la mémoire partagée
light_state_shm = sm.SharedMemory(name="light_state")
light_state = np.ndarray((4,), dtype=np.bool_, buffer=light_state_shm.buf)

# Définition des directions
left_turns = {key_north: key_east, key_south: key_west, key_east: key_south, key_west: key_north}
right_turns = {key_north: key_west, key_south: key_east, key_east: key_north, key_west: key_south}
waiting_vehicles = []  # Liste des véhicules en attente

def send_voiture_to_display(message, display_socket):
    """Envoie un message au processus display via socket TCP"""
    if message and display_socket:
        message="C:"+message
        print(f"Sending vehicle info: {message}")
        try:
            display_socket.sendall(message.encode())
        except (BrokenPipeError, OSError) as err:
            print(f"Error sending vehicle information: {err}")

def send_light_to_display(message, display_socket):
    """Envoie un message au processus display via socket TCP"""
    if display_socket:
        try:
            display_socket.sendall(b"L:"+message.astype(np.uint8).tobytes())
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
                print(f"Message reçu: {message}, Type: {msg_type}")  # Debug
                destination = message.decode()
                if message != None :
                    if msg_type == 2:  # Prioritaire : Passe immédiatement
                        return format_message(key, destination, True)

                    elif msg_type == 1:  # Normal car
                        if destination != left_turns[key]:  #Va tout droit (Priorité 1)
                            return format_message(key, destination, False)
                        elif destination == left_turns[key]:  # Tourne à gauche (Priorité 3)
                            waiting_vehicles.append((key, destination)) #en attente, on verif d'abord que les véhicules d'en face passent d'abord
            except sysv_ipc.BusyError:
                pass  

    # Vérifier les véhicules en attente
    for v in waiting_vehicles[:]:  
        key, destination = v
        print(f"Véhicules en attente: {waiting_vehicles}")  # Debug
        waiting_vehicles.remove(v)
        return format_message(key, destination,False) # passage autorisé.

    time.sleep(1)  

def keys_to_index(key):
    """Associe une clé de file de message à l'index du tableau `light_state`"""
    return {100: 0, 200: 1, 300: 2, 400: 3}.get(key, -1)

def gestion_traffic(display_socket):
    "laisse passer les véhicules tant que l'état des lights est le même"
    current_light_state = light_state.copy()
    print(current_light_state)
    try :
        send_light_to_display(current_light_state, display_socket)
    except (BrokenPipeError,ConnectionResetError) as err:
        print(f"Failed to send the message of lights: {err}")

    while not stopped:
            if not np.array_equal(current_light_state,light_state):
                print("traffic state changes,stop the passage of normal cars.")
                break
            next_vehicule=gestion_priorite(current_light_state)
            if next_vehicule:
                print(f"prochain véhicule + {next_vehicule}")
                send_voiture_to_display(next_vehicule, display_socket)
            if next_vehicule and "True" in next_vehicule:
                continue
            time.sleep(2)
        


if __name__ == "__main__":
    signal.signal(signal.SIGINT, handler_arret_clavier)
    coord_socket= socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
    coord_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    coord_socket.setblocking(False)
    coord_socket.bind((HOST, PORT))
    coord_socket.listen(1)
    display_socket=None
    while not stopped :
        readable, writable, error = select.select([coord_socket], [], [], 1)
        if coord_socket in readable:
            display_socket, address = coord_socket.accept()
            print("🚦 Démarrage du coordinateur...")
            try:
                gestion_traffic(display_socket)
            except Exception as err:
                print(f"Erreur dans gestion_traffic : {err}")
            
    print("Arrêt du coordinateur.")
    try:
        light_state_shm.close()
        light_state_shm.unlink()
    except FileNotFoundError:
        pass

    if coord_socket:
        coord_socket.close()
    if display_socket:
        display_socket.close()
