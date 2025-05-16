# builders/build_minuta.py

from utils.file_utils import leer_pdf, leer_docx, cargar_prompt  # Asegúrate de importar cargar_prompt
from utils.gemini_utils import obtener_respuesta

def construir_minuta(nombre, transcripcion, path_cv, path_metadatos):
    # Leer el CV y metadatos
    cv_contenido = leer_pdf(path_cv)
    metadatos_contenido = leer_docx(path_metadatos)
    
    # Cargar el prompt
    prompt_base = cargar_prompt("prompt/[SFAI-internal] Talents - 1.1. Prompt_ Minuta.txt")
    
    # Crear el prompt final
    prompt_final = f"{prompt_base}\n\nEntrevistado: {nombre}\n\nTranscripción:\n{transcripcion}\n\nCV:\n{cv_contenido}\n\nMetadatos:\n{metadatos_contenido}"
    
    # Obtener la respuesta desde Gemini
    respuesta = obtener_respuesta(prompt_final)

    # Retornar el resumen
    return {
        "nombre": nombre,
        "contenido": respuesta.strip()
    }
