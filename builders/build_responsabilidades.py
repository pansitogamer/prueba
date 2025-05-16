import os
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from utils.file_utils import guardar_archivo_docx, cargar_prompt
from utils.gemini_utils import obtener_respuesta  
from utils.excel_utils import subir_responsabilidades_a_drive

def build_responsabilidades(nombre_completo, rol1, rol2, evaluacion, output_dir="output"):
    try:
        # 1. Cargar el prompt base
        ruta_prompt = "prompt/[SFAI-open] Talents - Prompt Create Responsabilities.txt"
        prompt_template_str = cargar_prompt(ruta_prompt)
        if not prompt_template_str:
            raise ValueError("Prompt vacío o no encontrado.")

        # 2. Crear el prompt con los valores
        prompt = prompt_template_str.format(rol1=rol1, rol2=rol2, evaluacion=evaluacion)

        # 3. Generar respuesta con Gemini usando la función obtener_respuesta
        respuesta = obtener_respuesta(prompt).strip()

        # 4. Guardar en archivo .docx con el nombre actualizado
        carpeta_candidato = os.path.join(output_dir, nombre_completo)
        nombre_archivo = f"[SFAI-open] Talents - {nombre_completo} - Responsabilidades.docx"  # Cambio aquí
        ruta_archivo = os.path.join(carpeta_candidato, nombre_archivo)
        guardar_archivo_docx(respuesta, ruta_archivo)

        print(f"✅ Responsabilidades generadas y guardadas en {ruta_archivo}")
        return ruta_archivo

    except Exception as e:
        print(f"❌ Error al generar responsabilidades: {e}")
        return None
