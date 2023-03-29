import os 
if not os.path.exists('mensajes'):
    os.makedirs('mensajes')
#1KB para UDP

file = open("mensajes/1KB.txt", "w")
texto = 'a' * (250 * 1024 * 1)
file.write(texto)
file.close()

#1MB para UDP

file = open("mensajes/1MB.txt", "w")
texto = 'a' * (1024 * 1024)
file.write(texto)
file.close()

# 100MB para UDP

file = open("mensajes/100MB.txt", "w")
texto = 'a' * (100 * 1024 * 1024)
file.write(texto)
file.close()

# 250MB para UDP

file = open("mensajes/250MB.txt", "w")
texto = 'a' * (250 * 1024 * 1024)
file.write(texto)
file.close()