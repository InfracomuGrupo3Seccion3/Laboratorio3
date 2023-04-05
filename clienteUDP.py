import socket
import os
import time
import threading

# Establecer el tamaño máximo de los paquetes UDP
MAX_BYTES = 65535

# Establecer el puerto y la dirección IP del servidor
#server_address = ('192.168.11.134', 8008)
server_address = ('localhost', 8004)


# Preguntar qué archivo desean descargar todos los clientes
filename = input("Ingrese el nombre del archivo a descargar (100MB o 250MB): ")

# Solicitar el número de clientes que se conectarán al servidor
num_clients = int(input("Ingrese el número de clientes que se conectarán al servidor: "))

# Función que maneja la solicitud de un cliente
def handle_client(client_id):
    # Crear un socket UDP
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    client_socket.bind(('', 0))
    
    # Enviar un mensaje al servidor para solicitar el archivo y esperar la respuesta
    client_socket.sendto(filename.encode('utf-8'), server_address)

    # Recibir el archivo por fragmentos y guardarlos en un archivo en el directorio "ArchivosRecibidos"
    received_bytes = 0

    file_path = f"PruebasUDP/ArchivosRecibidos/Prueba6Cliente{client_id}-{filename}"
    client_socket.settimeout(5)
    start_time = time.time()
    with open(file_path, 'wb') as file:
        while True:
            try:
                client_socket.settimeout(5) 
                data, _ = client_socket.recvfrom(MAX_BYTES)
                if data == b'FIN':
                    print("acabo")
                    client_socket.close()
                    break
                file.write(data)
                received_bytes += len(data)
            except socket.timeout:
                print(f"No se ha recibido ningún mensaje después de 5 segundos. Se cancela la descarga del archivo {filename}.")
                client_socket.close()
                break

    file.close()
    end_time = time.time()
    

    log_path = f"PruebasUDP/LogsCliente/{time.strftime('%Y-%m-%d-%H-%M-%S')}-Cliente{client_id}Prueba6-log.txt"
    with open(log_path, 'w') as log:
        log.write(f"Archivo recibido: {filename}\n")
        log.write(f"Tamaño del archivo: {os.path.getsize(file_path)} bytes\n")
        log.write(f"Tiempo de transferencia: {end_time - start_time:.2f} segundos\n")
        log.write(f"Entrega exitosa: {1048576*int(filename[:2]) == received_bytes}")
    log.close()

    

# Iniciar un hilo para cada cliente
threads = []
for i in range(num_clients):
    thread = threading.Thread(target=handle_client, args=(i+1,))
    threads.append(thread)
    thread.start()
    print(f"Cliente {i+1} iniciado...")

    # Esperar un segundo antes de iniciar el siguiente hilo
    time.sleep(0.5)

# Esperar a que todos los hilos terminen
for i in range(num_clients):
    thread.join()
