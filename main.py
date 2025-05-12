from IA.datos import cargar_csv, registrar_consulta
from IA.analisis import detectar_cambios_bruscos
import pandas as pd
import sqlite3
from IA.ia import consultar_bot

df = cargar_csv("data/LOG ENTRADAS Y SALIDAS FISICAS0.csv")
print(df.head(11))
print(df.dtypes)

def mostrar_menu():
    print("\n--- MENÚ DE CONSULTAS ---")
    print("1. Ver primeros N datos")
    print("2. Filtrar por intervalo de tiempo")
    print("3. Detectar variables con cambios bruscos")
    print("4. Ver historial de consultas")
    print("5. Consultar con IA")
    print("6. Salir")

def ver_primeros_n(df):
    n = int(input("¿Cuántas filas querés ver?: "))
    print(df.head(n))
    registrar_consulta("mostrar_primeros", {"n": n})

def filtrar_por_intervalo(df):
    inicio = input("Ingresá fecha y hora de inicio (ej: 04.12.2024 08:56:26): ")
    fin = input("Ingresá fecha y hora de fin (ej: 04.12.2024 08:56:27): ")
    
    try:
        # Convertir ambas columnas a datetime
        df['timestring'] = pd.to_datetime(df['timestring'], format="%d.%m.%Y %H:%M:%S")
        inicio_dt = pd.to_datetime(inicio, format="%d.%m.%Y %H:%M:%S")
        fin_dt = pd.to_datetime(fin, format="%d.%m.%Y %H:%M:%S")
        
        # Filtrar el dataframe
        resultado = df[(df['timestring'] >= inicio_dt) & (df['timestring'] <= fin_dt)]
        
        if resultado.empty:
            print("\nNo se encontraron registros en ese intervalo. Verifica:")
            print(f"- Formato usado: dd.mm.YYYY HH:MM:SS")
            print(f"- Rango disponible: {df['timestring'].min()} a {df['timestring'].max()}")
        else:
            print(f"\nRegistros encontrados: {len(resultado)}")
            print(resultado)
        
        registrar_consulta("intervalo_tiempo", {"inicio": inicio, "fin": fin})
    
    except ValueError as e:
        print(f"\nError en formato de fecha: {e}")
        print("Usa el formato: dd.mm.YYYY HH:MM:SS (ej: 04.12.2024 08:56:26)")

def detectar_cambios(df):
    columna = "varvalue"
    umbral = int(input("Ingresá el umbral de cambio brusco (ej: 1000): "))
    cambios = detectar_cambios_bruscos(df, columna, umbral)
    
    if cambios.empty:
        print("No se detectaron cambios bruscos.")
    else:
        print(f"Se detectaron {len(cambios)} cambios bruscos en '{columna}':")
        print(cambios)
    
    registrar_consulta("cambios_bruscos", {"columna": columna, "umbral": umbral})

def ver_historial():
    conn = sqlite3.connect("data/memoria.db")
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, tipo_consulta, parametros, timestamp 
        FROM historial_consultas 
        ORDER BY timestamp DESC 
        LIMIT 10
    """)
    resultados = cursor.fetchall()
    conn.close()
    
    print("\n--- ÚLTIMAS CONSULTAS ---")
    for fila in resultados:
        params = eval(fila[2]) if fila[2].startswith("{") else fila[2]
        
        if fila[1] == "consulta_ia":
            print(f"\n[CONSULTA IA - {fila[3]}]")
            print(f"Pregunta: {params['pregunta']}")
            print(f"Respuesta: {params['respuesta']}")
        else:
            print(f"\n[{fila[1]} - {fila[3]}]")
            print(f"Parámetros: {params}")

# En la función consultar_ia()
def consultar_ia():
    historial = []  # Podrías cargar el historial desde la base de datos
    
    while True:
        pregunta = input("\nIngresá tu pregunta para la IA (o 'salir' para volver): ")
        if pregunta.lower() == 'salir':
            break
            
        respuesta, historial = consultar_bot(pregunta, historial)
        print("\nRespuesta de la IA:", respuesta)
        
        registrar_consulta("consulta_ia", {
            "pregunta": pregunta,
            "respuesta": respuesta,
            "modelo": "deepseek-chat"
        })

# Loop principal
while True:
    mostrar_menu()
    opcion = input("Elegí una opción (1-6): ")
    
    if opcion == "1":
        ver_primeros_n(df)
    elif opcion == "2":
        filtrar_por_intervalo(df)
    elif opcion == "3":
        detectar_cambios(df)
    elif opcion == "4":
        ver_historial()
    elif opcion == "5":
        consultar_ia()
    elif opcion == "6":
        print("Saliendo del programa.")
        break
    else:
        print("\nOpción inválida. Por favor elegí un número del 1 al 6.")