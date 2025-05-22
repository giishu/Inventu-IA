import streamlit as st
import pandas as pd
from IA.analisis import detectar_cambios_porcentuales
from IA.ia import consultar_bot
from main import ver_historial

st.set_page_config(page_title="Inventu IA", layout="centered")

st.title("🤖 Inventu IA – Análisis inteligente de archivos CSV")

# Inicializar estado
if "archivos" not in st.session_state:
    st.session_state.archivos = {}  # clave: nombre, valor: DataFrame
if "historial" not in st.session_state:
    st.session_state.historial = []

# Subida de archivos (1 o más)
uploaded_files = st.file_uploader("📎 Subí uno o más archivos CSV", type="csv", accept_multiple_files=True)
if uploaded_files:
    for file in uploaded_files:
        try:
            df = pd.read_csv(file, sep=';', on_bad_lines='skip')
            st.session_state.archivos[file.name] = df
            st.success(f"✅ Archivo '{file.name}' cargado.")
        except Exception as e:
            st.error(f"❌ Error cargando '{file.name}': {e}")

# Mostrar archivos cargados
if st.session_state.archivos:
    st.subheader("📂 Archivos activos")
    archivos_a_borrar = []
    for nombre, df in st.session_state.archivos.items():
        col1, col2 = st.columns([8, 1])
        col1.markdown(f"📄 **{nombre}** ({len(df)} filas)")
        if col2.button("❌", key=f"del_{nombre}"):
            archivos_a_borrar.append(nombre)

    for nombre in archivos_a_borrar:
        del st.session_state.archivos[nombre]
        st.success(f"🗑️ Archivo '{nombre}' eliminado.")

    # Selección de archivo
    nombre_sel = st.selectbox("📌 Elegí un archivo para trabajar", list(st.session_state.archivos.keys()))
    df = st.session_state.archivos[nombre_sel]

    st.subheader("👁️ Ver primeros N datos")
    n = st.number_input("Cantidad de filas a mostrar", min_value=1, max_value=len(df), value=5)
    st.dataframe(df.head(n))

    st.subheader("⏳ Filtrar por intervalo de tiempo (columna 'fecha')")
    time_col = next((col for col in df.columns if 'timestring' in col.lower()), None)
    if 'time_col' in df.columns:
        try:
            df['time_col'] = pd.to_datetime(df['time_col'])
            inicio = st.date_input("Desde", df['time_col'].min().date())
            fin = st.date_input("Hasta", df['time_col'].max().date())
            df_filtrado = df[(df['time_col'] >= pd.to_datetime(inicio)) & (df['time_col'] <= pd.to_datetime(fin))]
            st.write(f"🔎 {len(df_filtrado)} filas encontradas en ese rango:")
            st.dataframe(df_filtrado)
        except Exception as e:
            st.error(f"⚠️ Error procesando fechas: {e}")
    else:
        st.info("ℹ️ Este archivo no contiene una columna llamada 'TimeString'.")

    st.subheader("⚠️ Detectar cambios bruscos")
    columna_numerica = st.selectbox("Columna a analizar", df.select_dtypes(include='number').columns)
    umbral = st.number_input("Umbral de cambio brusco (%)", value=20.0)
    if st.button("Detectar cambios bruscos"):
        cambios = detectar_cambios_porcentuales(df, columna_numerica, umbral)
        if cambios.empty:
            st.success("✅ No se detectaron cambios bruscos con ese umbral.")
        else:
            st.warning(f"⚠️ Se detectaron {len(cambios)} cambios bruscos:")
            st.dataframe(cambios)

    st.subheader("💬 Consultar IA sobre el archivo")
    prompt = st.text_area("Escribí tu consulta")
    if st.button("Consultar IA"):
        if prompt.strip() == "":
            st.warning("⚠️ Escribí algo primero.")
        else:
            with st.spinner("Pensando..."):
                respuesta = consultar_bot(prompt, df)
                st.success("Respuesta de la IA:")
                st.write(respuesta)

    st.subheader("🕓 Ver historial de consultas")
    if st.button("Mostrar historial"):
        historial = ver_historial()
        if historial:
            for entrada in historial:
                st.markdown(f"**🗨️ Consulta:** {entrada['consulta']}")
                st.markdown(f"**🤖 Respuesta:** {entrada['respuesta']}")
                st.markdown("---")
        else:
            st.info("No hay historial guardado todavía.")
else:
    st.info("📌 Subí al menos un archivo CSV para empezar.")
