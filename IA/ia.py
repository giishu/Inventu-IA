from transformers import pipeline
import warnings

# Silenciamos advertencias irrelevantes
warnings.filterwarnings("ignore", message="Truncation was not explicitly activated")
warnings.filterwarnings("ignore", message="Setting `pad_token_id`")

def consultar_bot(mensaje_usuario):
    # Configuración optimizada para claridad
    chatbot = pipeline(
        "text-generation",
        model="gpt2-medium",
        device="cpu",
        truncation=True  # Activamos explícitamente
    )
    
    # Prompt mejor estructurado
    prompt = f"""Provide a clear, concise answer to this technical question in simple terms.
Question: {mensaje_usuario}
Answer in 1-2 sentences:"""  # Limitamos la extensión
    
    respuesta = chatbot(
        prompt,
        max_length=100,  # Más corto para mayor claridad
        num_return_sequences=1,
        temperature=0.4,  # Balance entre técnico y claro
        top_p=0.85,
        do_sample=True,
        repetition_penalty=2.5,  # Más fuerte contra repeticiones
        no_repeat_ngram_size=3,
        pad_token_id=50256  # Para evitar el warning
    )
    
    # Procesamiento limpio de la respuesta
    full_text = respuesta[0]["generated_text"]
    clean_answer = full_text.split("Answer in 1-2 sentences:")[1].strip().split('\n')[0]
    return clean_answer, []