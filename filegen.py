import random
import string

# Genera una cadena aleatoria de longitud 'length'
def random_string(length):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(length))

# Genera un archivo de letras random de tamaño 'size' en MB
def generate_file(size):
    filename = f"{size}MB.txt"
    file_size = size * 1024 * 1024 # Convierte el tamaño de MB a bytes
    chunk_size = 1024 * 1024 # Tamaño de cada chunk en bytes (1MB)

    with open(filename, "w") as file:
        for i in range(int(file_size / chunk_size)):
            file.write(random_string(chunk_size))
    
    print(f"Archivo {filename} generado exitosamente.")

# Genera archivos de 100MB y 250MB
generate_file(100)
generate_file(250)