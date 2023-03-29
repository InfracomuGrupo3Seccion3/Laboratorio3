import socket
import os
import time
import threading
import hashlib

# Dirección IP del servidor
#IP = '192.168.81.1'
IP = socket.gethostbyname(socket.gethostname())
# Puerto del servidor
PORT = 8000

# Dirección del servidor
ADDR = (IP, PORT)

# Máximo número de conexiones concurrentes
MAX_CONNECTIONS = 25

# Tamaño máximo de los paquetes a enviar
BSIZE = 1024

HASHINCORRECTO = 0

def messageReceiver(clientSocket, fileName, fileSize, idClient, f):
    print(f"[{idClient}] Waiting for message...")
    confirmation = "S"
    clientSocket.sendall(confirmation.encode('utf-8'))
    print(f"[{idClient}] Message sent.")
    print(f"[{idClient}] Waiting for message...")
    HASHINCORRECTO = 0
    # Verificar el directorio de descargas
    if not os.path.exists("ReceivedFiles"):
        os.mkdir("ReceivedFiles")

    with open(f"ReceivedFiles/{fileName}", "wb") as f:
        cont = 0
        while cont < int(fileSize):
            data = clientSocket.recv(BSIZE)
            f.write(data)
            cont += BSIZE
    
    clientSocket.sendall("Archivo recibido correctamente.".encode('utf-8'))
    
    print(f"[{idClient}] All bytes received.")
    
    file = open(f"ReceivedFiles/{fileName}", 'r')
    hash = clientSocket.recv(BSIZE).decode('utf-8')
    hashAlgorithm = hashlib.md5(file.read().encode()).hexdigest()
    
    print(f"[{idClient}] Hash received: {hash}")
    print(f"[{idClient}] Hash generated: {hashAlgorithm}")
    
    ADDR = clientSocket.getpeername()
    check = ""
    
    if hash == hashAlgorithm:
        print(f"[{idClient}] Hashes match.")
        clientSocket.sendall("Hashes match.".encode('utf-8'))
        check = "OK"
    else:
        print(f"[{idClient}] Hashes don't match.")
        HASHINCORRECTO+=1
        check = "ERROR"
        f.write(f"[client][{idClient}][{ADDR}] {fileName} Hash received/n")
    
    clientSocket.sendall(check.encode('utf-8'))
    clientSocket.close()


    
    
def main():
    # Conexión al servidor
    clientSockets = []
    tamClients = int(input("Ingrese el número de clientes: "))
    clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    clientSocket.connect(ADDR)
    print(f"[KING CLIENT] Connected to server at {IP}:{PORT}")
    clientSocket.sendall(str(tamClients).encode('utf-8'))
    transmissionFile = input("Ingrese el nombre del archivo a transmitir: ")
    print(f"[KING CLIENT] se espera el archivo {transmissionFile}")
    transmissionFile = transmissionFile.encode('utf-8')
    clientSocket.sendall(transmissionFile)
    print(f"[KING CLIENT] se envio el nombre del archivo {transmissionFile}")
    
    filesize = clientSocket.recv(BSIZE).decode('utf-8')
    print(f"[KING CLIENT] se recibio el tamaño del archivo {filesize}")

    if not os.path.exists('Logs'):
        os.makedirs('Logs')
    f= open('Logs/'+time.strftime("%Y-%m-%d-%H-%M-%S")+'-log.txt', 'w') 
    f.write(f"Archivo: {transmissionFile} Tamaño: {filesize} bytes\n")
    f.write(f"Clientes: {tamClients}\n")
    f.write(f"Tiempo de transferencia: \n")

    for i in range(tamClients):
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect(ADDR)
        clientSockets.append(client_socket)
        print(f"[CLIENT {i}] Connected to server at {IP}:{PORT}")

    # Recepción de mensajes
    threads = []
    for i in range(tamClients):
        id_cliente = i
        start_time = time.time()
        thread = threading.Thread(target=messageReceiver, args=(clientSockets[i],transmissionFile.decode('utf-8'),filesize,id_cliente,f))
        end_time = time.time()
        f.write(f"{end_time - start_time}\n")
        threads.append(thread)
        thread.start()
    for thread in threads:
        thread.join()
    f.close()
    clientSocket.sendall("Archivo recibido correctamente.".encode('utf-8'))
    clientSocket.close()
if __name__ == "__main__":
    main()
    print(f"[CLIENT] HASH incorrectos: {HASHINCORRECTO}")