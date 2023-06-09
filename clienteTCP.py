import socket
import os
import time
import threading
import hashlib

# Establecer el tamaño máximo de los paquetes UDP
MAX_BYTES = 65535

# Establecer el puerto y la dirección IP del servidor
server_address = ('192.168.68.110', 8000)

# Crear un socket UDP
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Función que maneja la solicitud de un cliente
def handle_client(client_id):
    # Enviar un mensaje al servidor para solicitar el archivo y esperar la respuesta
    filename = input(f"Cliente {client_id}: Ingrese el nombre del archivo a descargar (100MB o 250MB): ")
    client_socket.sendto(filename.encode('utf-8'), server_address)

    # Recibir el archivo por fragmentos y guardarlos en un archivo en el directorio "ArchivosRecibidos"
    received_bytes = 0
    file_path = f"ArchivosRecibidos/Cliente{client_id}-Prueba-610.txt"
    start_time = time.time()
    with open(file_path, 'wb') as file:
        while True:
            data, _ = client_socket.recvfrom(MAX_BYTES)
            if not data:
                break
            file.write(data)
            received_bytes += len(data)
    file.close()
    end_time = time.time()

    # recibir el hash del archivo
    hash_recibida= client_socket.recvfrom(MAX_BYTES)

    # comparar hash recibido con el hash del archivo
    hash_archivo = hashlib.md5(filename.read().encode()).hexdigest()
    verificacion = hash_recibida == hash_archivo
    if verificacion:
        print("El archivo es correcto")
        #enviar mensaje de confirmacion b"OK"
        client_socket.sendto(b"OK", server_address)
    else:
        print("El archivo es incorrecto")
        #enviar mensaje de error b"ERROR"
        client_socket.sendto(b"ERROR", server_address)


    # Registrar los tiempos de transferencia y generar un archivo de log en el directorio "Logs"
    log_path = f"Logs/{time.strftime('%Y-%m-%d-%H-%M-%S')}-Cliente{client_id}-log.txt"
    with open(log_path, 'w') as log:
        log.write(f"Archivo recibido: {filename}\n")
        log.write(f"Tamaño del archivo: {os.path.getsize(file_path)} bytes\n")
        log.write(f"Tiempo de transferencia: {end_time - start_time:.2f} segundos\n")
        if verificacion:
            log.write(f"Entrega exitosa: {os.path.getsize(file_path) == received_bytes}")
        else:
            log.write(f"Entrega fallida: {os.path.getsize(file_path) != received_bytes}")
    log.close()

# Solicitar el número de clientes que se conectarán al servidor
num_clients = int(input("Ingrese el número de clientes que se conectarán al servidor: "))

# Iniciar un hilo para cada cliente
threads = []
for i in range(num_clients):
    thread = threading.Thread(target=handle_client, args=(i+1,))
    threads.append(thread)
    thread.start()

# Esperar a que todos los hilos terminen
for thread in threads:
    thread.join()

# Cerrar el socket
client_socket.close()
