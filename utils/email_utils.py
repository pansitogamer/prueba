import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dotenv import load_dotenv

# LangChain + Gemini
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI

# Cargar variables de entorno desde .env
load_dotenv()

# Inicializar LLM de Gemini con API Key
def obtener_llm_gemini():
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("❌ Falta GOOGLE_API_KEY en el archivo .env")
    return ChatGoogleGenerativeAI(
        model="gemini-pro",
        google_api_key=api_key,
        temperature=0.7
    )

# Generar contenido de bienvenida con LangChain + Gemini
def generar_contenido_bienvenida(nombre_completo, fecha_inicio):
    prompt = PromptTemplate(
        input_variables=["nombre", "fecha"],
        template="""
Eres un asistente de RRHH. Redacta un correo de bienvenida en formato HTML para un nuevo empleado llamado {nombre},
que empieza el {fecha}. El mensaje debe incluir etiquetas HTML como <html>, <head>, <body>, <p>, <h1>, etc.
Asegúrate de que el contenido esté bien estructurado y formateado para verse correctamente en un cliente de correo.
"""
    )
    chain = LLMChain(llm=obtener_llm_gemini(), prompt=prompt)
    html_generado = chain.run(nombre=nombre_completo, fecha=fecha_inicio)
    
    # Validación mínima: si no contiene <html>, lo envolvemos
    if "<html" not in html_generado.lower():
        html_generado = f"<html><body>{html_generado}</body></html>"
    return html_generado

# Función para aplicar la plantilla base
def aplicar_base_template(contenido_html):
    try:
        with open(os.path.join('templates', 'base_email.html'), 'r', encoding='utf-8') as f:
            base = f.read()
        return base.replace("{{ contenido }}", contenido_html)
    except FileNotFoundError:
        print("⚠️ No se encontró la plantilla base, usando el contenido sin envoltorio.")
        return contenido_html

# Función para cargar la plantilla de rechazo
def cargar_plantilla_rechazo(nombre_completo):
    try:
        with open(os.path.join('prompt', 'feedback_rechazo.txt'), 'r', encoding='utf-8') as file:
            plantilla = file.read()
        return plantilla.replace('[NOMBRE]', nombre_completo)
    except FileNotFoundError:
        print("❌ No se encontró la plantilla de rechazo.")
        return ""

# Función para enviar correo
def enviar_correo(destinatario, asunto, cuerpo_html):
    from_email = os.getenv('EMAIL_USER')
    password = os.getenv('EMAIL_PASSWORD')
    smtp_server = os.getenv('SMTP_SERVER')
    smtp_port = int(os.getenv('SMTP_PORT'))

    if not (from_email and password and smtp_server and smtp_port):
        print("❌ Faltan variables de entorno para el envío de correos.")
        return False

    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = destinatario
    msg['Subject'] = asunto
    msg.attach(MIMEText(cuerpo_html, 'html'))

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(from_email, password)
            server.sendmail(from_email, destinatario, msg.as_string())
        print(f"✅ Correo enviado a {destinatario}")
        return True
    except Exception as e:
        print(f"❌ Error al enviar correo a {destinatario}: {e}")
        return False

# Correo de bienvenida (usando Gemini)
def correo_bienvenida(nombre_completo, email_destinatario, fecha_inicio):
    asunto = "¡Bienvenido a SoftwareFactoryAI! 🎉"
    contenido_generado = generar_contenido_bienvenida(nombre_completo, fecha_inicio)
    cuerpo_html = aplicar_base_template(contenido_generado)
    return enviar_correo(email_destinatario, asunto, cuerpo_html)

# Correo de rechazo (sigue usando plantilla local)
def correo_rechazo(nombre_completo, email_destinatario):
    asunto = "Gracias por tu participación en el proceso de selección"
    contenido = cargar_plantilla_rechazo(nombre_completo)
    cuerpo_html = aplicar_base_template(contenido)
    return enviar_correo(email_destinatario, asunto, cuerpo_html)
