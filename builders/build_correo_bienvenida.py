import os
from utils.email_utils import aplicar_base_template, enviar_correo
from utils.gemini_utils import obtener_respuesta

def armar_prompt_con_langchain(nombre_completo, fecha_inicio=None, rol_primario=None):
    try:
        # Cargar el prompt base
        with open(os.path.join('prompt', '[SFAI-internal] Talents - 3. Prompt_ First Interview Feedback.txt'), 'r', encoding='utf-8') as f:
            base_prompt = f.read()

        # Cargar el estilo de comunicación
        estilo_path = os.path.join('prompt', 'SFAI-internal_Talents_Prompt_Communication_style.txt')
        if os.path.exists(estilo_path):
            with open(estilo_path, 'r', encoding='utf-8') as f:
                estilo = f.read()
        else:
            estilo = "Profesional, cercano, motivador, alineado con la cultura de SoftwareFactoryAI."

        # Armar el prompt completo con todos los datos
        prompt_completo = f"""{base_prompt}

Estilo de comunicación:
{estilo}

Nombre del nuevo colaborador: {nombre_completo}
Fecha de inicio: {fecha_inicio}
Rol: {rol_primario or "No especificado"}

Instrucciones adicionales: Devuelve el contenido en formato HTML válido, usando etiquetas como <p>, <strong>, <br>, etc., para mantener la estructura y legibilidad.
"""
        return prompt_completo
    except FileNotFoundError:
        print("❌ No se encontró el archivo de prompt de bienvenida.")
        return ""

def enviar_correo_bienvenida(nombre_completo, email_destinatario, fecha_inicio, rol_primario):
    try:
        prompt = armar_prompt_con_langchain(nombre_completo, fecha_inicio, rol_primario)
        if not prompt:
            return

        contenido_generado = obtener_respuesta(prompt)

        if not contenido_generado:
            print("❌ Gemini no generó contenido válido.")
            return

        cuerpo_html = aplicar_base_template(contenido_generado)
        asunto = "¡Bienvenido a SoftwareFactoryAI! 🎉"
        enviado = enviar_correo(email_destinatario, asunto, cuerpo_html)

        if enviado:
            print(f"📧 Correo de bienvenida enviado a {email_destinatario}")
        else:
            print(f"⚠️ No se pudo enviar el correo a {email_destinatario}")
    except Exception as e:
        print(f"❌ Error al enviar el correo de bienvenida: {e}")

