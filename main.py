from IA.datos import cargar_csv, registrar_consulta
from IA.analisis import detectar_cambios_bruscos
import pandas as pd
import sqlite3

df = cargar_csv("data/LOG ENTRADAS Y SALIDAS FISICAS0.csv")
print(df.head(11))
print(df.dtypes)

def mostrar_menu():
    print("\n--- MENÚ DE CONSULTAS ---")
    print("1. Ver primeros N datos")
    print("2. Filtrar por intervalo de tiempo")
    print("3. Detectar variables con cambios bruscos")
    print("4. Ver historial de consultas")
    print("5. Salir")

def ver_primeros_n(df):
    n = int(input("¿Cuántas filas querés ver?: "))
    print(df.head(n))
    registrar_consulta("mostrar_primeros", {"n": n})

def filtrar_por_intervalo(df):
    inicio = input("Ingresá fecha y hora de inicio (ej: 26.11.2024 04:27:47): ")
    fin = input("Ingresá fecha y hora de fin (ej: 26.11.2024 04:30:00): ")
    
    df['timestring'] = pd.to_datetime(df['timestring'], format="%d.%m.%Y %H:%M:%S")
    resultado = df[(df['timestring'] >= inicio) & (df['timestring'] <= fin)]
    print(resultado)
    
    registrar_consulta("intervalo_tiempo", {"inicio": inicio, "fin": fin})

def detectar_cambios(df):
    columna = "varvalue"  # o podés pedir input del usuario
    umbral = int(input("Ingresá el umbral de cambio brusco (ej: 1000): "))
    cambios = detectar_cambios_bruscos(df, columna, umbral)
    
    if cambios.empty:
        print("No se detectaron cambios bruscos.")
    else:
        print(f"Se detectaron {len(cambios)} cambios bruscos en '{columna}':")
        print(cambios)
    
    registrar_consulta("cambios_bruscos", {"columna": columna, "umbral": umbral})

import sqlite3

def ver_historial():
    conn = sqlite3.connect("data/memoria.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, tipo_consulta, parametros, timestamp FROM historial_consultas ORDER BY timestamp DESC LIMIT 10")
    resultados = cursor.fetchall()
    conn.close()
    
    print("\n--- ÚLTIMAS CONSULTAS ---")
    for fila in resultados:
        print(f"ID: {fila[0]} | Tipo: {fila[1]} | Parámetros: {fila[2]} | Fecha: {fila[3]}")


# Loop principal
while True:
    mostrar_menu()
    opcion = input("Elegí una opción: ")
    
    if opcion == "1":
        ver_primeros_n(df)
    elif opcion == "2":
        filtrar_por_intervalo(df)
    elif opcion == "3":
        detectar_cambios(df)
    elif opcion == "4":
        ver_historial()
        break
    elif opcion == "5":
        print("Saliendo del programa.")
        break
    else: 
        print("Opción inválida. Intentá de nuevo.")
