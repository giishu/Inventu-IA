from IA.datos import cargar_csv, seleccionar_archivo, registrar_consulta
from IA.analisis import detectar_cambios_bruscos
from IA.ia import consultar_bot
import pandas as pd
import sqlite3
import tkinter as tk
from tkinter import filedialog
import time
import os

def seleccionar_archivo_manual():
    """
    Función unificada para seleccionar archivos
    Retorna: (ruta_archivo1, ruta_archivo2)
    """
    root = tk.Tk()
    root.withdraw()
    root.attributes('-topmost', True)
    
    # Configurar directorio inicial si existe
    initial_dir = "data" if os.path.exists("data") else None
    
    try:
        archivos = filedialog.askopenfilenames(
            title="Seleccione 1 o 2 archivos CSV (mantenga CTRL para seleccionar dos)",
            filetypes=[("Archivos CSV", "*.csv")],
            initialdir=initial_dir
        )
        
        if not archivos:
            print("\n⚠️ No se seleccionaron archivos. Usando archivo por defecto.")
            default = "data/LOG ENTRADAS Y SALIDAS FISICAS0.csv" if initial_dir else "LOG ENTRADAS Y SALIDAS FISICAS0.csv"
            return default, None
        
        return (archivos[0], archivos[1] if len(archivos) > 1 else None)
        
    except Exception as e:
        print(f"Error al seleccionar archivos: {str(e)}")
        return None, None
    finally:
        root.destroy()

def menu_carga():
    print("\n--- CARGAR DATOS DE LOCOMOTORAS ---")
    print("Opciones de carga:")
    print("1. Cargar archivo(s) manualmente")
    print("2. Usar archivo por defecto")
    print("3. Salir")
    
    opcion = input("Seleccione (1-3): ").strip()
    
    if opcion == "1":
        ruta1, ruta2 = seleccionar_archivo_manual()
        df = cargar_csv(ruta1, ruta2)  # <-- Llamar directo a cargar_csv con ambas rutas
    elif opcion == "2":
         df = cargar_csv("data/LOG ENTRADAS Y SALIDAS FISICAS0.csv")
    elif opcion == "3":
        exit()
    else:
        print("Opción inválida. Usando archivo por defecto.")
        df = cargar_csv("data/LOG ENTRADAS Y SALIDAS FISICAS0.csv")
    
    return df

def mostrar_menu():
    print("\n--- MENÚ DE CONSULTAS ---")
    print("1. Consultar IA")
    print("2. Ver primeros N datos")
    print("3. Filtrar por intervalo de tiempo")
    print("4. Detectar cambios bruscos")
    print("5. Ver historial")
    print("6. Salir")

def ver_primeros_n(df):
    try:
        n = int(input("¿Cuántas filas querés ver?: "))
        print(df.head(n))
        registrar_consulta("mostrar_primeros", {"n": n})
    except Exception as e:
        print(f"Error: {str(e)}")

def filtrar_por_intervalo(df):
    if df.empty:
        print("No hay datos para filtrar")
        return

    time_col = next((col for col in df.columns if 'timestring' in col.lower()), None)
    if not time_col:
        print("No se encontró columna de tiempo")
        return

    try:
        print("\nPrimeras filas de tiempo para referencia:")
        print(df[time_col].head().tolist())

        inicio = input("\nIngresá fecha de inicio (ej: 04.12.2024 08:56:26): ").strip()
        fin = input("Ingresá fecha de fin (ej: 04.12.2024 08:56:27): ").strip()

        # Convertir la columna de tiempo con formato explícito
        df[time_col] = pd.to_datetime(df[time_col], format="%d.%m.%Y %H:%M:%S", errors='coerce')
        df = df.dropna(subset=[time_col])

        inicio_dt = pd.to_datetime(inicio, format="%d.%m.%Y %H:%M:%S")
        fin_dt = pd.to_datetime(fin, format="%d.%m.%Y %H:%M:%S")

        mask = (df[time_col] >= inicio_dt) & (df[time_col] <= fin_dt)
        resultado = df.loc[mask].copy()

        if resultado.empty:
            print("\nNo se encontraron registros en ese intervalo.")
            print(f"Rango disponible: {df[time_col].min()} a {df[time_col].max()}")
        else:
            print(f"\nRegistros encontrados: {len(resultado)}")
            # Mostrar todas las columnas excepto posiblemente índices
            print(resultado.to_string(index=False))

        registrar_consulta("intervalo_tiempo", {"inicio": inicio, "fin": fin})
    except Exception as e:
        print(f"\nError al filtrar: {str(e)}")

def detectar_cambios(df):
    try:
        print("\nColumnas disponibles:")
        # Mostrar columnas sin modificar
        print(df.columns.tolist())
        
        # Pedir el nombre exacto como aparece
        columna = input('Ingresá el nombre exacto de la columna (copia de la lista arriba): ').strip()
        
        # Verificar que la columna existe
        if columna not in df.columns:
            print(f"\nError: La columna '{columna}' no existe. Columnas disponibles:")
            print(df.columns.tolist())
            return
            
        # Verificar que la columna sea numérica
        if not pd.api.types.is_numeric_dtype(df[columna]):
            print(f"\nError: La columna '{columna}' no es numérica")
            return
            
        umbral = float(input("Umbral de cambio (ej: 1000): "))
        
        # Llamar a la función de análisis (sin agregar comillas)
        cambios = detectar_cambios_bruscos(df, columna=columna, umbral=umbral)
        
        if cambios.empty:
            print("\nNo se detectaron cambios bruscos.")
        else:
            print(f"\nSe detectaron {len(cambios)} cambios bruscos:")
            # Mostrar solo columnas relevantes que existan
            cols_mostrar = [c for c in [columna, 'Valor_anterior', 'Diferencia', 'Tipo_Falla'] if c in cambios.columns]
            print(cambios[cols_mostrar].to_string(index=False))
        
        registrar_consulta("cambios_bruscos", {"columna": columna, "umbral": umbral})
    except Exception as e:
        print(f"\nError en detectar_cambios: {str(e)}")

def ver_historial():
    try:
        conn = sqlite3.connect("data/memoria.db")
        cursor = conn.cursor()
        cursor.execute("SELECT tipo_consulta, parametros, timestamp FROM historial_consultas ORDER BY timestamp DESC LIMIT 10")
        
        print("\n--- ÚLTIMAS 10 CONSULTAS ---")
        for consulta in cursor.fetchall():
            print(f"\n[{consulta[2]}] {consulta[0]}:")
            print(consulta[1][:100] + ("..." if len(consulta[1]) > 100 else ""))
    except Exception as e:
        print(f"Error al leer historial: {str(e)}")
    finally:
        conn.close()

def consultar_ia():
    try:
        pregunta = input("\nIngresa tu pregunta técnica: ")
        respuesta = consultar_bot(pregunta)
        print("\n🔧 Respuesta:")
        print(respuesta)
        registrar_consulta("consulta_ia", {"pregunta": pregunta, "respuesta": respuesta[:500]})
    except Exception as e:
        print(f"Error: {str(e)}")

def main():
    # Paso 1: Cargar datos
    df = menu_carga()  # Esta función ahora retorna el DataFrame
    
    if df.empty:
        print("¡Advertencia! No se cargaron datos correctamente")
        return  # Salir si no hay datos
    
    # Paso 2: Menú principal
    while True:
        try:
            mostrar_menu()
            opcion = input("Opción (1-6): ").strip()
            
            if opcion == "1":
                consultar_ia(df)  # Pasar df como argumento
            elif opcion == "2":
                ver_primeros_n(df)
            elif opcion == "3":
                filtrar_por_intervalo(df)
            elif opcion == "4":
                detectar_cambios(df)
            elif opcion == "5":
                ver_historial()  # Esta no necesita df
            elif opcion == "6":
                print("Saliendo...")
                break
            else:
                print("Opción inválida")
        except Exception as e:
            print(f"\nError inesperado: {str(e)}\n")

if __name__ == "__main__":
    main()