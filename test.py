import sqlite3

# Conexión a la base de datos
conexion = sqlite3.connect('monopoly.db')

# Crear un cursor
cursor = conexion.cursor()

nombre_tabla = 'boards'

# Obtener la estructura de la tabla
cursor.execute(f"PRAGMA table_info({nombre_tabla});")
estructura = cursor.fetchall()

# Mostrar la estructura de la tabla
for columna in estructura:
    print(f"ID: {columna[0]}, Nombre: {columna[1]}, Tipo: {columna[2]}, No Nulo: {columna[3]}, Valor por Defecto: {columna[4]}, Clave Primaria: {columna[5]}")

conexion.close()
