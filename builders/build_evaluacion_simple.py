import os
from docx import Document
from builders.build_prompt import build_prompt
from utils.gemini_utils import obtener_respuesta

def generar_evaluacion_simple(resumen_texto):
    prompt_template = build_prompt("[SFAI-internal] Talents - 2. Prompt_ Evaluate talent.txt")
    prompt_final = prompt_template.format(resumen=resumen_texto)
    respuesta = obtener_respuesta(prompt_final)

    return respuesta

def guardar_evaluacion_simple(nombre_completo, evaluacion_simple, carpeta_output):
    try:
        # Asegurarse de que la carpeta de salida exista
        os.makedirs(carpeta_output, exist_ok=True)

        # Nombre del archivo con el nombre completo del candidato
        filename = f"[SFAI-internal] Talents - {nombre_completo} - 2. First interview_ Evaluation.docx"
        output_path = os.path.join(carpeta_output, filename)

        # Crear y guardar el archivo .docx con la evaluación
        doc = Document()
        doc.add_paragraph(evaluacion_simple)
        doc.save(output_path)

        return output_path
    except Exception as e:
        print(f"❌ Error al guardar la evaluación: {e}")
        return None
