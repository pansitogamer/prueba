import os
from utils.email_utils import aplicar_base_template, enviar_correo
from utils.gemini_utils import obtener_respuesta

def armar_prompt_con_langchain(nombre_completo, fecha_inicio, link_credenciales, link_responsabilidades, rol_primario=""):
    try:
        # Cargar el prompt base
        with open(os.path.join('prompt', '[SFAI-internal] Talents - 9. Email_ Share credentials.txt'), 'r', encoding='utf-8') as f:
            base_prompt = f.read()

        # Cargar el estilo de comunicación
        estilo_path = os.path.join('prompt', 'SFAI-internal_Talents_Prompt_Communication_style.txt')
        if os.path.exists(estilo_path):
            with open(estilo_path, 'r', encoding='utf-8') as f:
                estilo = f.read()
        else:
            estilo = "Profesional, cercano, motivador, alineado con la cultura de SoftwareFactoryAI."

        # Armar el prompt completo con instrucción de HTML e inclusión de enlaces
        prompt_completo = f"""{base_prompt}

Estilo de comunicación:
{estilo}

Nombre del nuevo colaborador: {nombre_completo}
Rol primario: {rol_primario}
Fecha de inicio: {fecha_inicio}

Acceso a credenciales: {link_credenciales}
Acceso a responsabilidades: {link_responsabilidades}

Instrucciones adicionales: Devuelve el contenido en formato HTML válido, usando etiquetas como <p>, <strong>, <br>, etc., para mantener la estructura y legibilidad.
"""
        return prompt_completo
    except FileNotFoundError:
        print("❌ No se encontró el archivo de prompt de bienvenida.")
        return ""

def enviar_correo_credenciales(nombre_completo, email_destinatario, fecha_inicio=None, link_credenciales="", link_responsabilidades="", rol_primario=""):
    try:
        prompt = armar_prompt_con_langchain(nombre_completo, fecha_inicio, link_credenciales, link_responsabilidades, rol_primario)
        if not prompt:
            return

        contenido_generado = obtener_respuesta(prompt)

        if not contenido_generado:
            print("❌ Gemini no generó contenido válido.")
            return

        cuerpo_html = aplicar_base_template(contenido_generado)
        asunto = "Tus credenciales y responsabilidades en SoftwareFactoryAI ✨"
        enviado = enviar_correo(email_destinatario, asunto, cuerpo_html)

        if enviado:
            print(f"📧 Correo de credenciales enviado a {email_destinatario}")
        else:
            print(f"⚠️ No se pudo enviar el correo a {email_destinatario}")
    except Exception as e:
        print(f"❌ Error al enviar el correo de credenciales: {e}")
