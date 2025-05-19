import streamlit as st
import pandas as pd
from IA.datos import cargar_csv, registrar_consulta, limpiar_timestamp
from IA.analisis import detectar_cambios_bruscos, analizar_tendencia
from IA.ia import consultar_bot
import sqlite3
from datetime import datetime

# Configuración de página
st.set_page_config(page_title="🚂 Analizador de Locomotoras", page_icon="🚂", layout="wide")

# Cargar CSV con manejo de errores
@st.cache_data(ttl=3600, show_spinner="Cargando datos...")
def cargar_datos():
    try:
        df = cargar_csv("data/LOG ENTRADAS Y SALIDAS FISICAS0.csv")
        if df.empty:
            st.error("⚠️ El archivo CSV está vacío o no se pudo leer correctamente.")
        return df
    except Exception as e:
        st.error(f"Error al cargar el archivo CSV: {e}")
        return pd.DataFrame()

# Menú lateral
def mostrar_menu():
    st.sidebar.title("Menú Principal")
    opcion = st.sidebar.radio(
        "Selecciona una operación:",
        [
            "📊 Primeros N datos",
            "⏳ Filtrar por tiempo",
            "⚡ Cambios bruscos",
            "📈 Tendencia de desgaste",
            "🤖 Consultar IA",
            "📜 Historial",
            "🚪 Salir"
        ],
        index=0
    )
    st.sidebar.markdown("---")
    st.sidebar.info("Sistema v1.0 | Locomotoras Diésel")
    return opcion

def main():
    df = cargar_datos()
    st.title("🔍 Análisis Predictivo de Locomotoras")
    st.markdown("---")

    if df.empty:
        st.stop()

    # Mostrar estructura para debug
    st.write("✅ Columnas disponibles:", df.columns.tolist())

    opcion = mostrar_menu()

    # Opción 1: Mostrar N datos
    if "Primeros" in opcion:
        st.header("📊 Visualización Rápida")
        n = st.number_input("Número de filas:", min_value=1, max_value=100, value=5)
        if st.button("Mostrar"):
            st.dataframe(df.head(n), height=300)
            registrar_consulta("primeros_n", {"n": n})

    # Opción 2: Filtro por tiempo
    elif "Filtrar" in opcion:
        st.header("⏳ Filtro por Tiempo")
        col_tiempo = "TimeString"
        try:
            df[col_tiempo] = limpiar_timestamp(df[col_tiempo])
            inicio = st.text_input("Desde (dd.mm.YYYY HH:MM:SS)", "01.01.2024 00:00:00")
            fin = st.text_input("Hasta (dd.mm.YYYY HH:MM:SS)", "31.12.2024 23:59:59")
            if st.button("Filtrar"):
                desde = pd.to_datetime(inicio, format="%d.%m.%Y %H:%M:%S")
                hasta = pd.to_datetime(fin, format="%d.%m.%Y %H:%M:%S")
                filtrado = df[(df[col_tiempo] >= desde) & (df[col_tiempo] <= hasta)]
                if not filtrado.empty:
                    st.success(f"{len(filtrado)} registros encontrados")
                    st.dataframe(filtrado[[col_tiempo, "VarName", "VarValue"]])
                else:
                    st.warning("No hay datos en ese rango")
                registrar_consulta("filtro_temporal", {"inicio": inicio, "fin": fin})
        except Exception as e:
            st.error(f"Error en filtrado temporal: {e}")

    # Opción 3: Cambios bruscos
    elif "bruscos" in opcion:
        st.header("⚡ Detección de Cambios Bruscos")
        col = st.selectbox("Variable numérica:", [c for c in df.columns if pd.api.types.is_numeric_dtype(df[c])])
        umbral = st.slider("Umbral:", 0.0, 10000.0, 1000.0, step=50.0)
        if st.button("Analizar"):
            cambios = detectar_cambios_bruscos(df, columna=col, umbral=umbral)
            if not cambios.empty:
                st.warning(f"{len(cambios)} anomalías detectadas")
                st.dataframe(cambios)
            else:
                st.success("No se encontraron cambios bruscos")
            registrar_consulta("cambios_bruscos", {"columna": col, "umbral": umbral})

    # Opción 4: Tendencia
    elif "Tendencia" in opcion:
        st.header("📈 Análisis de Tendencia")
        col = st.selectbox("Variable:", [c for c in df.columns if pd.api.types.is_numeric_dtype(df[c])])
        ventana = st.slider("Ventana temporal:", 5, 100, 30)
        if st.button("Calcular tendencia"):
            try:
                resultado = analizar_tendencia(df, col, ventana)
                st.line_chart(resultado.set_index("TimeString")[[col, 'tendencia']])
                registrar_consulta("tendencia", {"columna": col, "ventana": ventana})
            except Exception as e:
                st.error(f"Error al calcular tendencia: {e}")

    # Opción 5: Consultar IA
    elif "IA" in opcion:
        st.header("🤖 Asistente Técnico")
        pregunta = st.text_area("Describe tu consulta:")
        if st.button("Consultar IA"):
            if pregunta.strip():
                respuesta = consultar_bot(pregunta)
                st.success("Respuesta generada por IA:")
                st.markdown(f"> {respuesta}")
                registrar_consulta("consulta_ia", {"pregunta": pregunta, "respuesta": respuesta})
            else:
                st.warning("Ingresá una pregunta válida.")

    # Opción 6: Historial
    elif "Historial" in opcion:
        st.header("📜 Registro de Actividad")
        try:
            conn = sqlite3.connect("data/memoria.db")
            rows = conn.execute("SELECT * FROM historial_consultas ORDER BY timestamp DESC LIMIT 10").fetchall()
            if rows:
                for idx, (id, payload, tipo, timestamp) in enumerate(rows, 1):
                    with st.expander(f"{idx}. {tipo} - {timestamp}"):
                        st.json(payload)
            else:
                st.info("No hay registros aún.")
        except Exception as e:
            st.error(f"Error al leer historial: {e}")
        finally:
            conn.close()

    # Opción 7: Salir
    elif "Salir" in opcion:
        st.success("✅ Sesión cerrada. Gracias por usar el sistema.")
        st.balloons()
        st.stop()

if __name__ == "__main__":
    main()