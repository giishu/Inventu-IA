import pandas as pd
import sqlite3

def cargar_csv(ruta):
    """Carga el CSV y normaliza formatos (filas/columnas o línea única)."""
    try:
        df = pd.read_csv(ruta, sep=',')
    except:
        df = pd.read_csv(ruta, sep=';')
    
    # Limpieza básica
    df.columns = df.columns.str.strip().str.lower()  # Ej: 'Presión' -> 'presion'
    df = df.dropna(how='all')  # Elimina filas vacías
    return df

def guardar_en_db(df, nombre_tabla):
    """Guarda el DataFrame en SQLite para historial."""
    conn = sqlite3.connect('data/memoria.db')
    df.to_sql(nombre_tabla, conn, if_exists='replace', index=False)
    conn.close()