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

def cargar_csv(ruta1, ruta2=None):
    try:
        # Prueba leer con coma primero
        try:
            df1 = pd.read_csv(ruta1, dayfirst=True, on_bad_lines='skip', sep=';')
        except:
            # Si falla, lee con punto y coma
            df1 = pd.read_csv(ruta1, sep=';', dayfirst=True, on_bad_lines='skip')
        
        if ruta2:
            try:
                df2 = pd.read_csv(ruta2, dayfirst=True, on_bad_lines='skip')
            except:
                df2 = pd.read_csv(ruta2, sep=';', dayfirst=True, on_bad_lines='skip')
            df = pd.concat([df1, df2], ignore_index=True)
        else:
            df = df1
            
        return df
    except Exception as e:
        print(f"Error al cargar CSV: {e}")
        return pd.DataFrame()



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