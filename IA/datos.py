import pandas as pd
import sqlite3

def guardar_estadisticas(df, nombre_tabla):
    """Guarda estadísticas básicas y valores únicos por columna en memoria.db"""
    conn = sqlite3.connect("data/memoria.db")
    cursor = conn.cursor()

    # Crear tabla para estadísticas si no existe
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS estadisticas (
            tabla TEXT,
            columna TEXT,
            promedio REAL,
            minimo REAL,
            maximo REAL,
            desviacion REAL
        )
    """)

    # Crear tabla para valores únicos
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS valores_unicos (
            tabla TEXT,
            columna TEXT,
            valor TEXT
        )
    """)

    for col in df.columns:
        if pd.api.types.is_numeric_dtype(df[col]):
            promedio = df[col].mean()
            minimo = df[col].min()
            maximo = df[col].max()
            desviacion = df[col].std()

            cursor.execute("""
                INSERT INTO estadisticas (tabla, columna, promedio, minimo, maximo, desviacion)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (nombre_tabla, col, promedio, minimo, maximo, desviacion))

        # Guardar valores únicos (máximo 20 por columna para no saturar)
        valores = df[col].dropna().unique()[:20]
        for v in valores:
            cursor.execute("""
                INSERT INTO valores_unicos (tabla, columna, valor)
                VALUES (?, ?, ?)
            """, (nombre_tabla, col, str(v)))

    conn.commit()
    conn.close()
    print(f"Estadísticas guardadas para tabla '{nombre_tabla}'")


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

def registrar_consulta(tipo, parametros):
    conn = sqlite3.connect("data/memoria.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS historial_consultas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tipo_consulta TEXT,
            parametros TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            categoria TEXT DEFAULT 'general'
        )
    """)
    
    # Convertimos los parámetros a string si son un diccionario
    params_str = str(parametros) if not isinstance(parametros, str) else parametros
    
    cursor.execute("""
        INSERT INTO historial_consultas (tipo_consulta, parametros, categoria)
        VALUES (?, ?, ?)
    """, (tipo, params_str, 'ia' if tipo == 'consulta_ia' else 'general'))
    
    conn.commit()
    conn.close()
