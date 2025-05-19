from IA.datos import cargar_csv, registrar_consulta
from IA.analisis import detectar_cambios_bruscos
from IA.ia import consultar_bot
import pandas as pd
import sqlite3

# Cargar datos iniciales
try:
    df = cargar_csv("data/LOG ENTRADAS Y SALIDAS FISICAS0.csv")
    if df.empty:
        raise ValueError("El DataFrame está vacío después de cargar el CSV")
except Exception as e:
    print(f"Error al cargar datos: {str(e)}")
    df = pd.DataFrame()

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

# Main loop
def main():
    if df.empty:
        print("¡Advertencia! No se cargaron datos correctamente")
    
    while True:
        try:
            mostrar_menu()
            opcion = input("Opción (1-6): ").strip()
            
            if opcion == "1":
                consultar_ia()
            elif opcion == "2":
                ver_primeros_n(df)
            elif opcion == "3":
                filtrar_por_intervalo(df)
            elif opcion == "4":
                detectar_cambios(df)
            elif opcion == "5":
                ver_historial()
            elif opcion == "6":
                print("Saliendo...")
                break
            else:
                print("Opción inválida")
        except Exception as e:
            print(f"\nError inesperado: {str(e)}\n")

if __name__ == "__main__":
    main()