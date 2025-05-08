import os
import pandas as pd
import mysql.connector

# Configuración de conexión desde variables de entorno o valores por defecto
host = os.getenv('MYSQL_HOST', 'localhost')
user = os.getenv('MYSQL_USER', 'root')
password = os.getenv('MYSQL_PASSWORD', 'sonic2013*0314')
database = 'vinos_db'

# Ruta al CSV
csv_path = os.path.join(os.path.dirname(__file__), 'vinos.csv')

# Lectura del CSV con pandas (sep=';' y decimal=',')
df = pd.read_csv(csv_path, sep=';', decimal=',')
# Normalizar nombres de columnas a minúsculas con guiones bajos
df.columns = [col.strip().lower().replace(' ', '_') for col in df.columns]

# Conexión a MySQL
conn = mysql.connector.connect(host=host, user=user, password=password)
conn.autocommit = True
cursor = conn.cursor()

# Crear base de datos si no existe y usarla
db_create = f"CREATE DATABASE IF NOT EXISTS {database} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
cursor.execute(db_create)
cursor.execute(f"USE {database}")

# Crear tabla vinos si no existe
create_table = '''
CREATE TABLE IF NOT EXISTS vinos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    fixed_acidity FLOAT,
    volatile_acidity FLOAT,
    citric_acid FLOAT,
    residual_sugar FLOAT,
    chlorides FLOAT,
    free_sulfur_dioxide INT,
    total_sulfur_dioxide INT,
    density FLOAT,
    ph FLOAT,
    sulphates FLOAT,
    alcohol FLOAT,
    quality VARCHAR(50)
) ENGINE=InnoDB;
'''
cursor.execute(create_table)

# Preparar inserción
tuples = [(
    row.fixed_acidity,
    row.volatile_acidity,
    row.citric_acid,
    row.residual_sugar,
    row.chlorides,
    int(row.free_sulfur_dioxide),
    int(row.total_sulfur_dioxide),
    row.density,
    row.ph,
    row.sulphates,
    row.alcohol,
    row.quality
) for row in df.itertuples(index=False)]

insert_sql = '''
INSERT INTO vinos (
    fixed_acidity, volatile_acidity, citric_acid, residual_sugar,
    chlorides, free_sulfur_dioxide, total_sulfur_dioxide,
    density, ph, sulphates, alcohol, quality
) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
'''

# Ejecutar batch
author_few = 1000  # tamaño de lote
for i in range(0, len(tuples), author_few):
    cursor.executemany(insert_sql, tuples[i:i+author_few])

print(f"Insertados {len(tuples)} registros en {database}.vinos")

# Cerrar conexión
cursor.close()
conn.close()