import pandas as pd
import sqlite3
import os
from datetime import datetime

def limpiar_timestamp(serie):
    """Estandariza el formato de tiempo para todos los módulos"""
    return pd.to_datetime(
        serie.astype(str).str.extract(r'(\d{2}\.\d{2}\.\d{4} \d{2}:\d{2}:\d{2})')[0],
        format='%d.%m.%Y %H:%M:%S', 
        errors='coerce'
    )

def inicializar_db():
    """Crea la estructura de la BD si no existe"""
    os.makedirs("data", exist_ok=True)
    conn = sqlite3.connect("data/memoria.db")
    
    conn.execute("""
    CREATE TABLE IF NOT EXISTS estadisticas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tabla TEXT NOT NULL,
        columna TEXT NOT NULL,
        promedio REAL,
        minimo REAL,
        maximo REAL,
        desviacion REAL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    conn.execute("""
    CREATE TABLE IF NOT EXISTS valores_unicos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tabla TEXT NOT NULL,
        columna TEXT NOT NULL,
        valor TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    conn.execute("""
    CREATE TABLE IF NOT EXISTS historial_consultas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tipo_consulta TEXT NOT NULL,
        parametros TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    conn.commit()
    conn.close()

def cargar_csv(ruta):
    try:
        # Cargar el CSV
        df = pd.read_csv(ruta, sep=';', quotechar='"', engine='python', on_bad_lines='skip')
        
        # Normalizar nombres de columnas
        df.columns = df.columns.str.strip().str.lower()
        
        # Renombrar columnas clave para consistencia
        column_mapping = {
            'timestring': 'timestring',
            '"timestring"': 'timestring',
            'time_string': 'timestring',
            # Agrega otros mapeos si es necesario
        }
        
        df = df.rename(columns={k: v for k, v in column_mapping.items() if k in df.columns})
        
        return df
    
    except Exception as e:
        print(f"Error al cargar CSV: {str(e)}")

def guardar_en_db(df, nombre_tabla):
    """Guarda en SQLite con actualización incremental"""
    with sqlite3.connect("data/memoria.db") as conn:
        df.to_sql(
            nombre_tabla, 
            conn, 
            if_exists='append',
            index=False,
            method='multi'
        )

def registrar_consulta(tipo, parametros):
    """Registra consultas en historial"""
    with sqlite3.connect("data/memoria.db") as conn:
        conn.execute("""
            INSERT INTO historial_consultas (tipo_consulta, parametros)
            VALUES (?, ?)
        """, (tipo, str(parametros)))