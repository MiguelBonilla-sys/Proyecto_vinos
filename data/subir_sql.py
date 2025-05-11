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

# Cargar directamente en Postgres (Neon) si se define la URL de conexión y salir
postgres_url = os.getenv('POSTGRES_URL')
if postgres_url:
    import psycopg2
    import sys
    sql_file = os.path.join(os.path.dirname(__file__), 'data.sql', 'vinos_db_vinos.sql')
    with open(sql_file, 'r', encoding='utf-8') as f:
        sql = f.read()
    conn_pg = psycopg2.connect(postgres_url)
    conn_pg.autocommit = True
    cur_pg = conn_pg.cursor()
    # Crear tabla vinos en Postgres si no existe
    cur_pg.execute("""
    CREATE TABLE IF NOT EXISTS vinos (
        id SERIAL PRIMARY KEY,
        fixed_acidity DOUBLE PRECISION,
        volatile_acidity DOUBLE PRECISION,
        citric_acid DOUBLE PRECISION,
        residual_sugar DOUBLE PRECISION,
        chlorides DOUBLE PRECISION,
        free_sulfur_dioxide INTEGER,
        total_sulfur_dioxide INTEGER,
        density DOUBLE PRECISION,
        ph DOUBLE PRECISION,
        sulphates DOUBLE PRECISION,
        alcohol DOUBLE PRECISION,
        quality VARCHAR(50)
    );
    """)
    # contador de INSERTs
    insert_count = 0
    # Dividir en posibles sentencias y ejecutar solo las reales, ignorando comentarios
    for raw in sql.split(';'):
        stmt = raw.strip()
        # eliminar backticks de MySQL para compatibilidad con Postgres
        stmt = stmt.replace('`', '')
        # eliminar AUTO_INCREMENT para Postgres
        stmt = stmt.replace('AUTO_INCREMENT', '')
        # convertir tipo DOUBLE a DOUBLE PRECISION
        stmt = stmt.replace(' double ', ' double precision ')
        # eliminar collation MySQL y DEFAULT NULL
        stmt = stmt.replace(' COLLATE utf8mb4_spanish_ci', '').replace(' COLLATE utf8mb4_unicode_ci', '')
        stmt = stmt.replace(' DEFAULT NULL', '')
        # omitir DROP TABLE y CREATE TABLE para no duplicar esquema
        if stmt.upper().startswith('DROP TABLE') or stmt.upper().startswith('CREATE TABLE'):
            continue
        # si es CREATE TABLE y contiene ENGINE, recortar desde ') ENGINE' para eliminar opciones MySQL
        if stmt.upper().startswith('CREATE TABLE') and ') ENGINE' in stmt.upper():
            pos = stmt.upper().find(') ENGINE')
            stmt = stmt[:pos+1]
        # Ignorar sentencias de bloqueo MySQL
        if stmt.upper().startswith('LOCK TABLES') or stmt.upper().startswith('UNLOCK TABLES'):
            continue
        # saltar vacío o comentario
        if not stmt or stmt.startswith('--') or stmt.startswith('/*'):
            continue
        # Ignorar cierres de comentarios en bloque
        if stmt.endswith('*/'):
            continue
        # contar INSERTs ejecutados
        if stmt.upper().startswith('INSERT INTO'):
            # contar número de tuplas en el INSERT (multi-fila)
            if 'VALUES' in stmt.upper():
                vals_part = stmt[stmt.upper().find('VALUES') + len('VALUES'):]
                # dividir en tuplas usando '),'
                parts = [p for p in vals_part.split('),') if p.strip()]
                insert_count += len(parts)
        cur_pg.execute(stmt)
    print(f"SQL cargado en Postgres desde {sql_file}. Insertadas {insert_count} filas en Postgres")
    cur_pg.close()
    conn_pg.close()
    sys.exit()

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