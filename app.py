import streamlit as st
import pandas as pd
from IA.datos import cargar_csv, registrar_consulta
from IA.analisis import detectar_cambios_porcentuales
from IA.ia import consultar_bot
import os

st.set_page_config(page_title="Analizador de Locomotoras", layout="wide")

# ---------------------- ESTADO GLOBAL ----------------------
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "dataframe" not in st.session_state:
    st.session_state.dataframe = pd.DataFrame()

# ---------------------- CARGA DE DATOS ----------------------
st.sidebar.title("Carga de datos")

opcion = st.sidebar.radio("¿Cómo querés cargar los datos?", ["Archivo por defecto", "Subir CSV"])
if opcion == "Archivo por defecto":
    ruta = "data/LOG ENTRADAS Y SALIDAS FISICAS0.csv"
    if os.path.exists(ruta):
        df = cargar_csv(ruta)
        st.sidebar.success("Archivo cargado")
    else:
        st.sidebar.error("No se encontró el archivo por defecto.")
        df = pd.DataFrame()
else:
    archivo = st.sidebar.file_uploader("Subí uno o dos archivos CSV", type="csv", accept_multiple_files=True)
    if archivo:
        rutas = [a.name for a in archivo]
        df = cargar_csv(*archivo)
        st.sidebar.success("Archivo cargado")
    else:
        df = pd.DataFrame()

# Guardamos DataFrame en estado global
if not df.empty:
    st.session_state.dataframe = df

# ---------------------- INTERFAZ PRINCIPAL ----------------------
st.title("🔍 Analizador de Datos de Locomotoras")

tabs = st.tabs(["📊 Ver datos", "🧠 Chat con IA", "⚠️ Cambios bruscos"])

# ---------------------- TAB 1: VER DATOS ----------------------
with tabs[0]:
    if st.session_state.dataframe.empty:
        st.warning("Todavía no se cargaron datos.")
    else:
        st.subheader("Vista previa de los datos")
        n = st.slider("¿Cuántas filas mostrar?", 5, 100, 10)
        st.dataframe(st.session_state.dataframe.head(n))

# ---------------------- TAB 2: CHAT CON IA ----------------------
with tabs[1]:
    st.subheader("💬 Chat técnico con IA")
    prompt = st.text_input("Escribí tu consulta:", key="user_input")
    if st.button("Enviar"):
        if prompt:
            respuesta = consultar_bot(prompt)
            st.session_state.chat_history.append(("Tú", prompt))
            st.session_state.chat_history.append(("IA", respuesta))
            registrar_consulta("consulta_ia", {"pregunta": prompt, "respuesta": respuesta[:500]})

    for autor, mensaje in st.session_state.chat_history[::-1]:
        if autor == "IA":
            st.markdown(f"**🤖 IA:** {mensaje}")
        else:
            st.markdown(f"**🧑 Vos:** {mensaje}")

# ---------------------- TAB 3: DETECCIÓN DE CAMBIOS ----------------------
with tabs[2]:
    st.subheader("⚠️ Detección de cambios porcentuales")
    df = st.session_state.dataframe

    if df.empty:
        st.warning("Cargá un archivo para analizar.")
    else:
        # Parsing por si viene como una columna única
        if len(df.columns) == 1:
            df = df[df.columns[0]].str.split(';', expand=True)

        if "VarName" not in df.columns or "VarValue" not in df.columns:
            st.error("El archivo no contiene columnas 'VarName' y 'VarValue'.")
        else:
            variables = sorted(df["VarName"].dropna().unique())
            seleccion = st.selectbox("Seleccioná una variable para analizar:", variables)
            umbral = st.slider("Umbral de cambio porcentual (%)", 1, 100, 30)

            if st.button("Detectar cambios"):
                cambios = detectar_cambios_porcentuales(df, seleccion, umbral)
                if cambios.empty:
                    st.info("No se detectaron cambios significativos.")
                else:
                    st.success(f"Se detectaron {len(cambios)} cambios significativos.")
                    st.dataframe(cambios)
