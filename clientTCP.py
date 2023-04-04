import socket
import os
import time
import threading
import hashlib

# Dirección IP del servidor
IP = '192.168.77.130'
#IP = socket.gethostbyname(socket.gethostname())
# Puerto del servidor
PORT = 8001

# Dirección del servidor
ADDR = (IP, PORT)

# Máximo número de conexiones concurrentes
MAX_CONNECTIONS = 25

# Tamaño máximo de los paquetes a enviar
BSIZE = 1024

HASHINCORRECTO = 0

def messageReceiver(clientSocket, fileName, fileSize, idClient, num_clients):
    print(f"[{idClient}] Waiting for message...")
    confirmation = "S"
    clientSocket.sendall(confirmation.encode('utf-8'))
    print(f"[{idClient}] Message sent.")
    print(f"[{idClient}] Waiting for message...")
    HASHINCORRECTO = 0
    # Verificar el directorio de descargas
    if not os.path.exists("ReceivedFiles"):
        os.mkdir("ReceivedFiles")
    print(fileSize)
    start = time.time()
    with open(f"ReceivedFiles/{fileName}", "wb") as file:
        cont = 0
        while cont < int(fileSize):
            #thread.wait()
            data = clientSocket.recv(BSIZE)
            file.write(data)
            cont += len(data)
    end = time.time()
    time_dif = end - start

    clientSocket.sendall("Archivo recibido correctamente.".encode('utf-8'))
    
    print(f"[{idClient}] All bytes received.")
   
    file = open(f"ReceivedFiles/{fileName}", 'r')
    hash = clientSocket.recv(BSIZE).decode('utf-8')
    hashAlgorithm = hashlib.md5(file.read().encode()).hexdigest()
    
    print(f"[{idClient}] Hash received: {hash}")
    print(f"[{idClient}] Hash generated: {hashAlgorithm}")
    
    ADDR = clientSocket.getpeername()
    check = ""
    puerto = clientSocket.getsockname()[1]
    if hash == hashAlgorithm:
        print(f"[{idClient}] Hashes match.")
        clientSocket.sendall("Hashes match.".encode('utf-8'))
        with  open(f"./ClientLogs/Cliente{idClient}-Prueba-{num_clients}.txt", 'w')as f:
            archivo = open(f"ClientLogs/Cliente{idClient}-Prueba-{num_clients}.txt", 'r')
            f.write(f"[CLIENTE][{idClient}][{puerto}] {fileName} recibido correctamente en {time_dif} segundos\n")
            f.write(f"[CLIENTE][{idClient}][{puerto}] {fileName} velocidad de transferencia {int(fileSize)/time_dif} B/segundo\n" )

        check = "OK"
    else:
        print(f"[{idClient}] Hashes don't match.")
        HASHINCORRECTO+=1
        check = "ERROR"
        with  open(f"ClientLogs/Cliente{idClient}-Prueba-{num_clients}.txt", 'w')as f:    
            archivo = open(f"./ClientLogs/Cliente{idClient}-Prueba-{num_clients}.txt", 'r')
            f.write(f"[CLIENTE][{idClient}][{puerto}] {fileName} recibido incorrectamente en {time_dif} segundos\n")
            f.write(f"[CLIENTE][{idClient}][{puerto}] {fileName} velocidad de transferencia {int(fileSize)/time_dif} B/segundo\n")
    
    clientSocket.close()


    
    
def main():
    # Conexión al servidor
    clientSockets = []
    tamClients = int(input("Ingrese el número de clientes: "))
    clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    clientSocket.connect(ADDR)
    print(f"[KING CLIENT] Connected to server at {IP}:{PORT}")
    clientSocket.sendall(str(tamClients).encode('utf-8'))
    fileName = input("Ingrese el nombre del archivo a transmitir: ")
    print(f"[KING CLIENT] se espera el archivo {fileName}")
    transmissionFile = fileName.encode('utf-8')
    clientSocket.sendall(transmissionFile)
    print(f"[KING CLIENT] se envio el nombre del archivo {transmissionFile}")
    
    filesize = clientSocket.recv(BSIZE).decode('utf-8')
    print(f"[KING CLIENT] se recibio el tamaño del archivo {filesize}")

    if not os.path.exists('ClientLogs'):
        os.makedirs('ClientLogs')
    
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
        thread = threading.Thread(target=messageReceiver, args=(clientSockets[i],transmissionFile.decode('utf-8'),filesize,id_cliente,tamClients))
        end_time = time.time()
        threads.append(thread)
        thread.start()
    for thread in threads:
        thread.join()
    clientSocket.sendall("Archivo recibido correctamente.".encode('utf-8'))
    clientSocket.close()
if __name__ == "__main__":
    main()
    print(f"[CLIENT] HASH incorrectos: {HASHINCORRECTO}")