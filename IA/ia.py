import requests
import warnings
from typing import Tuple

# Configuración de la API (deberías mover esto a un archivo de configuración)
API_KEY = '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'  # Obtén una en: https://openrouter.ai/keys
API_URL = 'https://openrouter.ai/api/v1/chat/completions'

def consultar_bot(mensaje_usuario: str, historial: list = None) -> Tuple[str, list]:
    """
    Consulta a la API de DeepSeek Chat
    
    Args:
        mensaje_usuario: Pregunta del usuario
        historial: Lista de mensajes previos (opcional)
    
    Returns:
        Tuple con (respuesta, historial_actualizado)
    """
    if historial is None:
        historial = []
    
    headers = {
        'Authorization': f'Bearer {API_KEY}',
        'HTTP-Referer': 'https://tu-sitio.com',  # Opcional pero recomendado
        'X-Title': 'trAIn'         # Opcional
    }
    
    # Construimos el historial de mensajes
    messages = [
        {
            "role": "system",
            "content": "Eres un experto en locomotoras diésel. Responde de manera técnica pero clara en español."
        }
    ]
    
    # Agregamos historial previo
    messages.extend(historial)
    
    # Agregamos la nueva pregunta
    messages.append({"role": "user", "content": mensaje_usuario})
    
    data = {
        "model": "deepseek/deepseek-chat",  # Modelo a usar
        "messages": messages,
        "temperature": 0.7,
        "max_tokens": 500
    }
    
    try:
        response = requests.post(API_URL, json=data, headers=headers, timeout=30)
        response.raise_for_status()  # Lanza error si hay problemas
        
        respuesta_api = response.json()
        respuesta = respuesta_api['choices'][0]['message']['content']
        
        # Actualizamos el historial con la respuesta
        historial_actualizado = messages + [
            {"role": "assistant", "content": respuesta}
        ]
        
        return respuesta, historial_actualizado
    
    except requests.exceptions.RequestException as e:
        warnings.warn(f"Error al consultar la API: {str(e)}")
        return "Lo siento, no pude conectarme al servicio de IA. Intenta nuevamente más tarde.", historial
