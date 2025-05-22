# ia.py 'AIzaSyA2PipvauvVPmrGQz-Hn7nhu_VcWHypeEo'
import google.generativeai as genai
import pandas as pd
from IA.datos import cargar_csv, seleccionar_archivo
from typing import Optional
import random

# Configuración (usa variable de entorno en producción!)
genai.configure(api_key='AIzaSyA2PipvauvVPmrGQz-Hn7nhu_VcWHypeEo')

class LocomotoraBot:
    def __init__(self):
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        self.saludos = [
            "¡Hola! 👋 Soy tu asistente de locomotoras. ¿En qué puedo ayudarte hoy?",
            "¡Buenas! 🚂 Aquí analizando datos ferroviarios. ¿Qué necesitas?",
            "¡Hola humano! 🤖💬 Listo para diagnosticar esas máquinas."
        ]
        self.despedidas = [
            "¡Hasta luego! Que tus rieles siempre estén alineados 🛤️",
            "Nos vemos. ¡Recuerda hacer mantenimiento preventivo! 🔧",
            "Bot desconectado. ¡Chuuu-chuuu! 🚆"
        ]
        self.errores = [
            "Ups, tengo un cortocircuito... 💥 Intenta reformular tu pregunta",
            "Parece que mi motor analítico falló 🛠️ ¿Podrías repetirlo?",
            "Error 404: No encontré esa respuesta en mi banco de datos"
        ]

    def generar_respuesta(self, pregunta: str, df: Optional[pd.DataFrame] = None) -> str:
        """Evalúa el tipo de pregunta y responde acorde"""
        pregunta = pregunta.lower().strip()
        
        # Modo conversacional
        if any(palabra in pregunta for palabra in ["hola", "hi", "qué tal", "cómo estás"]):
            return random.choice(self.saludos)
            
        if any(palabra in pregunta for palabra in ["adiós", "chao", "hasta luego"]):
            return random.choice(self.despedidas)
        
        # Modo técnico
        if df is not None and not df.empty:
            return self._analisis_tecnico(pregunta, df)
        else:
            return "🔍 Por favor carga datos primero para análisis técnico"

    def _analisis_tecnico(self, pregunta: str, df: pd.DataFrame) -> str:
        """Análisis especializado con datos"""
        try:
            # Prepara contexto adaptativo
            contexto = "Eres un ingeniero senior de locomotoras diésel. " + \
                     "Combina conocimiento técnico con explicaciones claras.\n\n"
            
            if "corriente" in pregunta:
                contexto += "Foco en análisis eléctrico (umbral seguro: 15-25A)"
            elif "temperatura" in pregunta:
                contexto += "Foco en termodinámica (rango óptimo: 65-90°C)"
            
            datos_relevantes = df.tail(50).to_string()  # Muestra reducida
            
            prompt = f"""
            {contexto}
            
            **Datos Recientes**:
            {datos_relevantes}
            
            **Consulta del Usuario**:
            "{pregunta}"
            
            **Formato de Respuesta**:
            1. 🧐 Interpretación (máx. 2 oraciones)
            2. ⚠️ Riesgo (1-5) + Causas posibles
            3. 🛠️ Acciones recomendadas (lista concisa)
            4. 💡 Consejo práctico (opcional)
            """
            
            response = self.model.generate_content(prompt)
            return self._formatear_respuesta(response.text)
            
        except Exception as e:
            return f"{random.choice(self.errores)}. Detalle: {str(e)}"

    def _formatear_respuesta(self, respuesta: str) -> str:
        """Da formato humano a la respuesta técnica"""
        lineas = respuesta.split('\n')
        if len(lineas) > 3:  # Si es respuesta estructurada
            return "\n".join([
                f"🔧 **Análisis Técnico** 🔧",
                f"{lineas[0]}", 
                "",
                "🚨 **Riesgo/Causas**:",
                f"{lineas[1]}",
                "",
                "🛠 **Acciones Recomendadas**:",
                f"{lineas[2]}",
                "",
                "💡 **Tip Práctico**:",
                f"{random.choice(['Revisar manual página 78', 'Verificar sellos hermeticos', 'Lubricar componentes móviles'])}"
            ])
        return respuesta

# Interfaz mejorada
def consultar_bot(pregunta: str, df: Optional[pd.DataFrame] = None, ruta_csv: Optional[str] = None) -> str:
    bot = LocomotoraBot()
    
    if df is None and ruta_csv:
        df = cargar_csv(ruta_csv)
    
    return bot.generar_respuesta(pregunta, df)