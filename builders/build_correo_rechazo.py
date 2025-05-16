import os
from utils.email_utils import aplicar_base_template, enviar_correo
from utils.gemini_utils import obtener_respuesta

def armar_prompt_rechazo(nombre_completo, rol_primario=None):
    try:
        # Cargar el prompt base
        with open(os.path.join('prompt', 'feedback_rechazo.txt'), 'r', encoding='utf-8') as f:
            base_prompt = f.read()

        # Cargar el estilo de comunicación
        estilo_path = os.path.join('prompt', 'SFAI-internal_Talents_Prompt_Communication_style.txt')
        if os.path.exists(estilo_path):
            with open(estilo_path, 'r', encoding='utf-8') as f:
                estilo = f.read()
        else:
            estilo = "Profesional, cordial, agradecido, alineado con la cultura de SoftwareFactoryAI."

        # Armar el prompt completo con todos los datos
        prompt_completo = f"""{base_prompt}

Estilo de comunicación:
{estilo}

Nombre del candidato: {nombre_completo}
Rol: {rol_primario or "la posición ofrecida"}

Instrucciones adicionales: Devuelve el contenido en formato HTML válido, usando etiquetas como <p>, <strong>, <br>, etc., para mantener la estructura y legibilidad.
"""
        return prompt_completo
    except FileNotFoundError:
        print("❌ No se encontró el archivo de prompt de rechazo.")
        return ""

def enviar_correo_rechazo(nombre_completo, email_destinatario, rol_primario=None):
    try:
        prompt = armar_prompt_rechazo(nombre_completo, rol_primario)
        if not prompt:
            return

        contenido_generado = obtener_respuesta(prompt)

        if not contenido_generado:
            print("❌ Gemini no generó contenido válido para rechazo.")
            return

        cuerpo_html = aplicar_base_template(contenido_generado)

        # Verificar el contenido antes de enviarlo
        # print("Contenido HTML generado:\n", cuerpo_html)

        # Asunto del correo
        asunto = f"Actualización sobre tu candidatura para el puesto de {rol_primario or 'SoftwareFactoryAI'}"
        
        enviado = enviar_correo(email_destinatario, asunto, cuerpo_html)

        if enviado:
            print(f"📧 Correo de rechazo enviado a {email_destinatario}")
        else:
            print(f"⚠️ No se pudo enviar el correo de rechazo a {email_destinatario}")
    except Exception as e:
        print(f"❌ Error al enviar el correo de rechazo: {e}")
