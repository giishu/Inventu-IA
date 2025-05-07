import pandas as pd
import sqlite3

def cargar_csv(ruta):
    df = pd.read_csv(ruta, sep=';', decimal=',', quotechar='"', on_bad_lines='skip', engine='python')
    print(f"Filas cargadas: {len(df)}")


    # Limpieza básica
    df.columns = df.columns.str.strip().str.lower()  # Ej: 'Presión' -> 'presion'
    df = df.dropna(how='all')  # Elimina filas vacías

    total_lineas = sum(1 for _ in open(ruta, encoding="utf-8"))
    print(f"Total líneas en archivo: {total_lineas}")
    print(f"Filas cargadas sin errores: {len(df)}")
    print(f"Líneas ignoradas por error: {total_lineas - len(df)}")
    
    return df

def guardar_en_db(df, nombre_tabla):
    """Guarda el DataFrame en SQLite para historial."""
    conn = sqlite3.connect('data/memoria.db')
    df.to_sql(nombre_tabla, conn, if_exists='replace', index=False)
    conn.close()