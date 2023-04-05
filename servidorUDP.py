################################################################################
# Servidor UDP
# Autor: Alejandro Salgado, Juan Camilo Falla, Daniel Bernal
# Fecha: 2022-03-16
# Descripción: Servidor UDP que recibe un mensaje y lo envía a un cliente
#              UDP
################################################################################

import socket
import os
import datetime
import threading

# Configuración del servidor
HOST = '0.0.0.0'
PORT = 8001
BUFFER_SIZE = 64000  # Tamaño de cada paquete en bytes
FILES = {"100MB": "100MB.txt", "250MB": "250MB.txt"}
MAX_CONNECTIONS = 25

# Crea el socket UDP
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((HOST, PORT))

# Crea el directorio de registro si no existe
if not os.path.exists("PruebasUDP/LogsServidor"):
    os.makedirs("PruebasUDP/LogsServidor")

# Crea un semáforo para limitar el número de conexiones concurrentes
connection_semaphore = threading.Semaphore(MAX_CONNECTIONS)

class ClientHandler(threading.Thread):
    def __init__(self, addr, data):
        threading.Thread.__init__(self)
        self.addr = addr
        self.data = data

    def run(self):
        now = datetime.datetime.now()

        # Obtiene el nombre del archivo solicitado y su tamaño
        filename = self.data.decode().strip()
        file_size = os.path.getsize(FILES[filename])

        bytes_enviados = 0
        # Abre el archivo y lo envía al cliente en paquetes de BUFFER_SIZE bytes
        with open(FILES[filename], "rb") as f:
            while True:
                bytes_read = f.read(BUFFER_SIZE)
                bytes_enviados += len(bytes_read)
                if not bytes_read:
                    print(bytes_enviados)
                    sock.sendto(b'FIN', self.addr)
                    break
                sock.sendto(bytes_read, self.addr)

        sock.sendto(b'FIN', self.addr)
        sock.sendto(b'FIN', self.addr)
        sock.sendto(b'FIN', self.addr)
        sock.sendto(b'FIN', self.addr)
        sock.sendto(b'FIN', self.addr)
        sock.sendto(b'FIN', self.addr)
        # Escribe los detalles de la transferencia en el archivo de registro
        log_filename = now.strftime(f"%Y-%m-%d-%H-%M-%S-{self.addr[1]}-log.txt")
        with open(os.path.join("PruebasUDP/LogsServidor", log_filename), "a") as log_file:
            log_file.write(f"Archivo enviado: {FILES[filename]}\n")
            log_file.write(f"Tamaño del archivo: {file_size} bytes\n")
            log_file.write(f"Entrega exitosa: sí\n")
            log_file.write(f"Tiempo de transferencia: {datetime.datetime.now() - now}\n")
            log_file.write(f"Dirección IP del cliente: {self.addr[0]}\n")
            log_file.write(f"Puerto del cliente: {self.addr[1]}\n\n")

# Maneja las solicitudes de los clientes concurrentemente
while True:
    # Espera por una solicitud de un cliente
    data, addr = sock.recvfrom(BUFFER_SIZE)
    print(f"Se ha recibido una solicitud de {addr}")

    # Adquiere el semáforo para limitar el número de conexiones concurrentes
    connection_semaphore.acquire()

    # Inicia una nueva tarea para manejar la solicitud del cliente
    client_handler = ClientHandler(addr, data)
    client_handler.start()
