import socket
 
HOST = "127.0.0.1"
PORT = 65432

if __name__ == '__main__' :
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        client_socket.connect((HOST, PORT))
        while True:
            data = client_socket.recv(1024)

            #ici gestion reception des données
            print("echo> ", data.decode())
            
            #arret clean