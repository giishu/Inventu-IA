# ia.py 'AIzaSyA2PipvauvVPmrGQz-Hn7nhu_VcWHypeEo'
import google.generativeai as genai
import pandas as pd
from IA.datos import cargar_csv

genai.configure(api_key='AIzaSyA2PipvauvVPmrGQz-Hn7nhu_VcWHypeEo')

def consultar_bot(pregunta: str, ruta_csv="data/LOG ENTRADAS Y SALIDAS FISICAS0.csv"):
    """Consulta técnica a Gemini con filtrado por relevancia"""
    df = cargar_csv(ruta_csv)
    if df.empty:
        return "Error: No hay datos para analizar"
    
    datos = df.tail(100).to_string()
    
    model = genai.GenerativeModel('gemini-1.5-flash')
    prompt = f"""
    Eres un ingeniero de locomotoras. Analiza estos datos:
    {datos}
    
    Responde en español con:
    1. 🔍 Hallazgos clave
    2. ⚠️ Riesgos (1-5)
    3. 🛠️ Acciones
    """
    
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error en Gemini: {str(e)}"