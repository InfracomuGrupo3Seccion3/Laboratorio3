import socket
import os
import datetime
import hashlib
import threading
import time

# Dirección IP del servidor
#IP = '192.168.77.130'
IP = socket.gethostbyname(socket.gethostname())

# Puerto del servidor
PORT = 8001

# Dirección del servidor
ADDR = (IP, PORT)

# Máximo número de conexiones concurrentes
MAX_CONNECTIONS = 25

# Tamaño máximo de los paquetes a enviar
BSIZE = 1024

# Hash utilizado para verificar la integridad del archivo
HASH_ALGORITHM = hashlib.sha256()


def ClientHandler(idClient, fileName, conn, addr, logFileName):
    
    # Imprimir el ID del cliente
    print(f"[NEW CONNECTION] Client {idClient} connected.")
    
    # Recibir el nombre del archivo a enviar
    ready = conn.recv(BSIZE).decode('utf-8')
    print(f"[{idClient}] Filename: {ready}")
    
    
    # Abrir el archivo
    file = open(fileName, 'r')
    print(f"[file][{addr}] {fileName} opened.")
    
    # Obtener el tamaño del archivo
    tam = os.path.getsize(fileName)
    
    
    # Enviar el archivo por fragmentos de tamaño BSIZE
    with open(fileName, "rb") as f:
        cont = 0
        while cont < tam:
            data = f.read(BSIZE)
            conn.sendall(data)
            cont += len(data)
    
    
    # Recibir la confirmación de que el archivo fue recibido correctamente
    confirmation = conn.recv(BSIZE).decode('utf-8')
    print(f"[{idClient}] {confirmation}")
    

    # Hash del archivo
    hashFile = hashlib.md5(file.read().encode()).hexdigest()
    print(f"[file][hash][{addr}] {fileName} hash generated.")
    print(hashFile)
    # Enviar el hash del archivo
    conn.sendall(hashFile.encode('utf-8'))
    print(f"[file][hash][{addr}] {fileName} hash sent.")
    
    confirmation = conn.recv(BSIZE).decode('utf-8') #Recibe hashes match o no match
    print(confirmation)
    if confirmation == "Hashes match.":
        logFileName.write(f"El estado de la transferencia al cliente {idClient} es: Exitoso\n")
        print(f"[file][{addr}] {fileName} sent successfully.")
    else:
        logFileName.write(f"El estado de la transferencia al cliente {idClient} es: Fallido\n")
        print(f"[file][{addr}] {fileName} sent unsuccessfully.")
    
    
    # Cerrar la conexión
    conn.close()
    
    
def main():
    
    #now = datetime.datetime.now()
    
    print("[STARTING] server is starting...")
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(ADDR)
    server.listen(MAX_CONNECTIONS)
    print(f"[LISTENING] Server is listening on {IP}:{PORT}")
    
    # Recibir la conexión inicial
    intialConnection, addr = server.accept()
    print(f"[MASTER CONNECTION] {addr} connected.")
    
    # Recibir el número de clientes
    clientCant = int(intialConnection.recv(BSIZE).decode('utf-8'))
    print(f"[MASTER CONNECTION] {clientCant} clients connected.")
    
    # Recibir el nombre del archivo a enviar
    transferFile = intialConnection.recv(BSIZE).decode('utf-8')+ ".txt"
    print(f"[MASTER CONNECTION] {transferFile} file to send.")
    # Extraer el tamaño de un arhivo que entra por parámetro en bytes
    tam = os.path.getsize("Files/" + transferFile)
    # Enviar la confirmación de que el archivo fue recibido correctamente
    #tamaño a str
    tam = str(tam)
    intialConnection.sendall(tam.encode('utf-8'))
    
    # Crea el directorio de registro si no existe
    if not os.path.exists("PruebasTCP/ServerLogs"):
        os.makedirs("PruebasTCP/ServerLogs")
    
    # Abre el archivo de log
    logFileName = open('PruebasTCP/ServerLogs/'+time.strftime("%Y-%m-%d-%H-%M-%S")+'-log.txt', 'w')    
    logFileName.write(f"Cantidad de clientes: {clientCant} \n\n") 

    # Aceptar conexiones de los clientes
    for i in range(clientCant):
        conn, addr = server.accept()
        
        # Escribir el archivo de registro
        logFileName.write(f"\nNombre del archivo: {transferFile}\n")
        logFileName.write(f"Tamano del archivo: {tam} bytes\n")
        logFileName.write(f"Id del cliente: {i}\n")
        logFileName.write(f"IP del cliente: {addr[0]}\n")
        logFileName.write(f"Puerto del cliente: {addr[1]}\n")
        startTime = time.time()
        thread = threading.Thread(target=ClientHandler, args=(i,"Files/" +  transferFile, conn, addr, logFileName))
        endTime = time.time()
        thread.start()
        print(f"[ACTIVE CONNECTIONS] {threading.activeCount() - 1}")
        logFileName.write(f"Tiempo de transferencia: {endTime - startTime} segundos\n")
    logFileName.write(f"\n\n")
    logFileName.write(f"  / \__\n")
    logFileName.write(f" (    @\___\n")
    logFileName.write(f"  /         O\n")
    logFileName.write(f"  /   (_____/\n")
    logFileName.write(f" /_____/   U\n")
    logFileName.write(f"  \n")
    
    # Cerrar el archivo de registro
    if intialConnection.recv(BSIZE).decode('utf-8') == "DISCONNECT":
        server.close()
        print("[SERVER] Server is closed.")
        logFileName.close()
    
if __name__ == "__main__":
    main()