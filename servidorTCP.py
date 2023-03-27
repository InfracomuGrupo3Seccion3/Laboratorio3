# Servidor UDP
# Autor: Alejandro Salgado, Juan Camilo Falla, Daniel Bernal
# Fecha: 2022-03-16
# Descripción: Servidor UDP que recibe un mensaje y lo envía a un cliente
#              UDP
################################################################################

import socket
import os
import datetime
import hashlib

# Configuración del servidor
HOST = '0.0.0.0'
PORT = 12345
BUFFER_SIZE = 65536  # Tamaño de cada paquete en bytes
FILES = {"100MB": "archivo_100MB.bin", "250MB": "archivo_250MB.bin"}

# Crea el socket UDP
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind((HOST, PORT))

# Crea el directorio de registro si no existe
if not os.path.exists("Logs"):
    os.makedirs("Logs")

while True:
    # Espera por una solicitud de un cliente
    data, addr = sock.recvfrom(BUFFER_SIZE)
    print(f"Se ha recibido una solicitud de {addr}")
    now = datetime.datetime.now()

    # Obtiene el nombre del archivo solicitado y su tamaño
    filename = data.decode().strip()
    file_size = os.path.getsize(FILES[filename])

    # Abre el archivo y lo envía al cliente en paquetes de BUFFER_SIZE bytes
    with open(FILES[filename], "rb") as f:
        while True:
            bytes_read = f.read(BUFFER_SIZE)
            if not bytes_read:
                break
            sock.sendto(bytes_read, addr)
    #Encontrar el hash del archivo
    hash_archivo = hashlib.md5(filename.read().encode()).hexdigest()
    # Envia el hash del archivo
    sock.sendto(hash_archivo, addr)


    #recibe mensaje de confirmacion de hash
    data, addr = sock.recvfrom(BUFFER_SIZE)
    verfify = True
    # Si el mensaje es "OK", el archivo se envió correctamente si el mensaje es "ERROR", el archivo no se envió correctamente
    if data.decode().strip() == "OK":
        verfify = True
    elif data.decode().strip() == "ERROR":
        verfify = False


    # Escribe los detalles de la transferencia en el archivo de registro
    log_filename = now.strftime("%Y-%m-%d-%H-%M-%S-log.txt")
    with open(os.path.join("Logs", log_filename), "a") as log_file:
        log_file.write(f"Archivo enviado: {FILES[filename]}\n")
        log_file.write(f"Tamaño del archivo: {file_size} bytes\n")
        if verfify:
            log_file.write(f"Entrega exitosa: sí\n")
        else:
            log_file.write(f"Entrega exitosa: no\n")
        log_file.write(f"Tiempo de transferencia: {datetime.datetime.now() - now}\n")
        log_file.write(f"Dirección IP del cliente: {addr[0]}\n")
        log_file.write(f"Puerto del cliente: {addr[1]}\n\n")
