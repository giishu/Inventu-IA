# llave = 'AIzaSyA2PipvauvVPmrGQz-Hn7nhu_VcWHypeEo'
import google.generativeai as genai
import pandas as pd
import io
import contextlib
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
            contexto = "Eres un ingeniero senior de locomotoras diésel. " + \
                     "Combina conocimiento técnico con explicaciones claras.\n\n"
            
            if "corriente" in pregunta:
                contexto += "Foco en análisis eléctrico (umbral seguro: 15-25A)"
            elif "temperatura" in pregunta:
                contexto += "Foco en termodinámica (rango óptimo: 65-90°C)"
            
            datos_relevantes = df.tail(50).to_string()
            
            prompt = f"""
            Eres un ingeniero especializado en locomotoras diésel. Analiza estos datos:

            **Variables Clave**:
            - Presión aceite: Rango normal (10000-12000)
            - RPM: Rango normal (8000-9000)
            - Temperaturas (IMT): Rango normal (-30 a 50)

            **Datos Recientes**:
            {df.tail(20).to_string()}

            **Pregunta**: "{pregunta}"

            **Formato de Respuesta**:
            1. 📌 Hallazgo principal
            2. 🔍 Variable crítica (si aplica)
            3. 🚨 Nivel de riesgo (1-5)
            4. 🛠️ Acción recomendada
            """
            
            response = self.model.generate_content(prompt)
            return self._formatear_respuesta(response.text)
            
        except Exception as e:
            return f"{random.choice(self.errores)}. Detalle: {str(e)}"

    def _formatear_respuesta(self, respuesta: str) -> str:
        """Da formato humano a la respuesta técnica"""
        lineas = respuesta.split('\n')
        if len(lineas) > 2:  # Se ajustó el chequeo porque ya no hay tip
            return "\n".join([
                f"🔧 **Análisis Técnico** 🔧",
                f"{lineas[0]}", 
                "",
                "🚨 **Riesgo/Causas**:",
                f"{lineas[1]}",
                "",
                "🛠 **Acciones Recomendadas**:",
                f"{lineas[2]}"
            ])
        return respuesta
    
    def analisis_con_codigo_sin_ver_df(self, pregunta: str, df: pd.DataFrame) -> str:
        """La IA genera código basándose solo en la pregunta. Luego lo ejecuta localmente sobre el df."""
        try:
            columnas = df.columns.tolist()

            # Paso 1: Generar el código
            prompt_codigo = f"""
            Eres un experto en análisis de datos con pandas.

            El DataFrame se llama `df` y tiene las siguientes columnas: {columnas}.

            - `VarName` contiene el nombre de la variable (por ejemplo, 'RPM - 7KF00', 'PRESION ACEITE COMPRESOR - 7KF00', etc.)
            - `VarValue` contiene el valor medido (número).
            - `TimeString` contiene la fecha y hora de la medición.
            - Cada fila representa una única medición de una variable en un instante de tiempo.

            Usá pandas para responder la siguiente pregunta. Si es necesario, filtrá las filas que coincidan con palabras clave dentro de la columna 'VarName'.

            Pregunta del usuario:
            \"{pregunta}\"

            Genera solamente el código Python necesario para responder a esa pregunta. Sin explicaciones. Sin comentarios.
            """

            response = self.model.generate_content(prompt_codigo)
            codigo = response.text.strip().strip("```python").strip("```")

            # Paso 2: Ejecutar el código
            local_vars = {"df": df.copy()}
            buffer = io.StringIO()
            with contextlib.redirect_stdout(buffer):
                exec(codigo, {}, local_vars)
            resultado = buffer.getvalue().strip()

            # Paso 3: Explicar el resultado
            prompt_explicacion = f"""
            Este fue el resultado de ejecutar código Python sobre un DataFrame en pandas:

            Código:
            {codigo}

            Resultado:
            {resultado}

            Explica al usuario qué significa este resultado, como si no supiera programar.
            """

            explicacion = self.model.generate_content(prompt_explicacion).text.strip()
            return f"📊 Código generado:\n```python\n{codigo}\n```\n\n📈 Resultado:\n{resultado}\n\n🧠 Explicación:\n{explicacion}"

        except Exception as e:
            return f"❌ Error ejecutando el análisis: {str(e)}"


bot=LocomotoraBot()

# Interfaz mejorada
def consultar_bot(pregunta: str, df: Optional[pd.DataFrame] = None, ruta_csv: Optional[str] = None) -> str:
    if df is None and ruta_csv:
        df = cargar_csv(ruta_csv)
    
    return bot.generar_respuesta(pregunta, df)