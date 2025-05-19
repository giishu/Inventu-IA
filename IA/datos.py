import pandas as pd
import sqlite3
import os
import tkinter as tk
from tkinter import filedialog
from datetime import datetime

import tkinter as tk
from tkinter import filedialog

def seleccionar_archivo():
    """Permite al usuario seleccionar un archivo CSV mediante diálogo"""
    root = tk.Tk()
    root.withdraw()  # Oculta la ventana principal
    
    archivo = filedialog.askopenfilename(
        title="Seleccione el archivo CSV",
        filetypes=[("Archivos CSV", "*.csv"), ("Todos los archivos", "*.*")]
    )
    
    return archivo if archivo else None

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