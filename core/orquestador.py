import os
import re
from dotenv import load_dotenv
from datetime import datetime
from docx import Document
from builders.build_minuta import construir_minuta
from builders.build_evaluacion_simple import generar_evaluacion_simple, guardar_evaluacion_simple
from builders.build_correo_bienvenida import enviar_correo_bienvenida
from builders.build_correo_rechazo import enviar_correo_rechazo
from utils.file_utils import leer_docx, guardar_archivos_candidato
from utils.excel_utils import crear_hoja_credenciales
from builders.build_responsabilidades import build_responsabilidades
from utils.excel_utils import subir_responsabilidades_a_drive
from utils.excel_utils import crear_carpeta_candidato_en_drive, subir_minuta_a_drive, subir_evaluacion_a_drive
from utils.excel_utils import subir_archivo_txt_a_drive
from utils.excel_utils import listar_subcarpetas_drive, descargar_archivos_carpeta_drive
import json

load_dotenv()

OUTPUT_DIR = "output"
TMP_INPUT_DIR = "tmp_input"

def extraer_nombre_completo(texto_metadatos):
    match = re.search(r"(?i)Nombre completo:\s*(.+?)(,|\n|$)", texto_metadatos)
    if match:
        return match.group(1).strip()
    return "Nombre_Desconocido"

def extraer_email(texto_metadatos):
    for linea in texto_metadatos.split("\n"):
        if "Email:" in linea:
            return linea.split("Email:")[1].strip().rstrip(",")
    return None

def extraer_fecha_inicio(texto_metadatos):
    for linea in texto_metadatos.split("\n"):
        if "Fecha de inicio:" in linea:
            match = re.search(r"\d{2}-\d{2}-\d{4}", linea)
            if match:
                return match.group(0)
    return None

def extraer_rol_primario(texto_metadatos):
    for linea in texto_metadatos.split("\n"):
        if "Rol primario:" in linea:
            return linea.split("Rol primario:")[1].strip().rstrip(",")
    return "No especificado"

def guardar_minuta(nombre_completo, contenido):
    filename = f"[SFAI-internal] Talents - {nombre_completo} - 1. First interview_ Minuta.docx"
    carpeta_output_candidato = os.path.join(OUTPUT_DIR, nombre_completo)
    os.makedirs(carpeta_output_candidato, exist_ok=True)

    output_path = os.path.join(carpeta_output_candidato, filename)
    doc = Document()
    doc.add_paragraph(contenido)
    doc.save(output_path)
    return output_path

def loggear(nombre_completo, texto):
    carpeta_output_candidato = os.path.join(OUTPUT_DIR, nombre_completo)
    os.makedirs(carpeta_output_candidato, exist_ok=True)
    log_file_candidato = os.path.join(carpeta_output_candidato, "log.txt")
    
    with open(log_file_candidato, "a", encoding="utf-8") as f:
        f.write(f"{datetime.now().isoformat()} - {texto}\n")

def encontrar_archivo_por_patron(carpeta_path, patron):
    archivos = os.listdir(carpeta_path)
    print(f"🔍 Archivos en {carpeta_path}: {archivos}")
    for archivo in archivos:
        print(f"Revisando archivo: {archivo}")
        if re.search(patron, archivo, re.IGNORECASE):
            return os.path.join(carpeta_path, archivo)
    return None

def run_minutas_batch():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(TMP_INPUT_DIR, exist_ok=True)
    loggear("Global", "🟡 Inicio del procesamiento de candidatos")

    carpeta_input_drive_id = os.getenv('CARPETA_DRIVE_INPUT_ID')
    carpetas_candidatos = listar_subcarpetas_drive(carpeta_input_drive_id)

    for candidato in carpetas_candidatos:
        nombre_carpeta = candidato['name']
        candidato_drive_id = candidato['id']
        carpeta_path = os.path.join(TMP_INPUT_DIR, nombre_carpeta)

        print(f"\n📋 Procesando a {nombre_carpeta}")
        loggear(nombre_carpeta, f"Procesando: {nombre_carpeta}")

        try:
            os.makedirs(carpeta_path, exist_ok=True)
            descargar_archivos_carpeta_drive(candidato_drive_id, carpeta_path)

            transcripcion_path = encontrar_archivo_por_patron(carpeta_path, r"Transcript.*\.docx")
            metadatos_path = encontrar_archivo_por_patron(carpeta_path, r"Metadata.*\.docx")
            cv_path = encontrar_archivo_por_patron(carpeta_path, r"CV.*\.pdf")

            if not transcripcion_path or not metadatos_path or not cv_path:
                raise FileNotFoundError("Faltan archivos necesarios para procesar el candidato.")

            transcripcion = leer_docx(transcripcion_path)
            metadatos = leer_docx(metadatos_path)
            nombre_completo = extraer_nombre_completo(metadatos)
            email_candidato = extraer_email(metadatos)
            fecha_inicio = extraer_fecha_inicio(metadatos)
            rol_primario = extraer_rol_primario(metadatos)

            carpeta_padre_drive_id = os.getenv('CARPETA_DRIVE_ID')
            carpeta_drive_id = crear_carpeta_candidato_en_drive(nombre_completo, carpeta_padre_drive_id)
            loggear(nombre_completo, f"✅ Carpeta de Drive creada para {nombre_completo} con ID {carpeta_drive_id}")

            carpeta_output_candidato = guardar_archivos_candidato(nombre_completo, email_candidato, fecha_inicio)
            contenido_minuta = construir_minuta(nombre_completo, transcripcion, cv_path, metadatos_path)
            output_file_minuta = guardar_minuta(nombre_completo, contenido_minuta['contenido'])

            print(f"✅ Minuta generada: {output_file_minuta}")
            loggear(nombre_completo, f"✅ Minuta creada para {nombre_completo}: {output_file_minuta}")

            enlace_minuta = subir_minuta_a_drive(output_file_minuta, nombre_completo, carpeta_drive_id)
            if enlace_minuta:
                print(f"✅ Minuta subida a Google Drive: {enlace_minuta}")
                loggear(nombre_completo, f"✅ Minuta subida a Drive para {nombre_completo}: {enlace_minuta}")

            resumen_texto = transcripcion
            evaluacion_simple = generar_evaluacion_simple(resumen_texto)

            if evaluacion_simple:
                try:
                    output_file_evaluacion = guardar_evaluacion_simple(nombre_completo, evaluacion_simple, carpeta_output_candidato)
                    print(f"✅ Evaluación generada: {output_file_evaluacion}")
                    loggear(nombre_completo, f"✅ Evaluación creada para {nombre_completo}: {output_file_evaluacion}")

                    enlace_evaluacion = subir_evaluacion_a_drive(output_file_evaluacion, nombre_completo, carpeta_drive_id)
                    if enlace_evaluacion:
                        print(f"✅ Evaluación subida a Google Drive: {enlace_evaluacion}")
                        loggear(nombre_completo, f"✅ Evaluación subida a Drive para {nombre_completo}: {enlace_evaluacion}")

                    while True:
                        decision_usuario = input("\n🔵 ¿Deseas continuar con la contratación? (s/n): ").strip().lower()
                        if decision_usuario == "s":
                            print("✅ Usuario aprobó continuar con la contratación.")
                            loggear(nombre_completo, f"✅ Usuario aprobó la contratación para {nombre_completo}")

                            if email_candidato:
                                enviar_correo_bienvenida(nombre_completo, email_candidato, fecha_inicio, rol_primario)
                            else:
                                print("⚠️ No se encontró el email del candidato para enviar el correo de bienvenida.")

                            enlace_hoja = crear_hoja_credenciales(nombre_completo, email_candidato, carpeta_drive_id)

                            ruta_responsabilidades = build_responsabilidades(
                                nombre_completo=nombre_completo,
                                rol1=rol_primario,
                                rol2=rol_primario,
                                evaluacion=evaluacion_simple
                            )
                            print(f"✅ Responsabilidades generadas: {ruta_responsabilidades}")
                            loggear(nombre_completo, f"✅ Archivo de responsabilidades creado para {nombre_completo}: {ruta_responsabilidades}")

                            responsabilidades_id = subir_responsabilidades_a_drive(ruta_responsabilidades, nombre_completo, carpeta_drive_id)
                            responsabilidades_link = f"https://drive.google.com/file/d/{responsabilidades_id}/view"

                            links = {
                                "credenciales": enlace_hoja,
                                "responsabilidades": responsabilidades_link
                            }
                            links_path = os.path.join(carpeta_output_candidato, "links.json")
                            with open(links_path, "w", encoding="utf-8") as f:
                                json.dump(links, f, indent=2)

                            log_path = os.path.join(carpeta_output_candidato, "log.txt")
                            if os.path.exists(log_path):
                                subir_archivo_txt_a_drive(log_path, "log.txt", nombre_completo, carpeta_drive_id)

                            break

                        elif decision_usuario == "n":
                            print("❌ Usuario decidió no continuar con la contratación.")
                            loggear(nombre_completo, f"❌ Usuario decidió no contratar a {nombre_completo}")

                            if email_candidato:
                                enviar_correo_rechazo(nombre_completo, email_candidato)
                            else:
                                print("⚠️ No se encontró el email del candidato para enviar el correo de rechazo.")

                            log_path = os.path.join(carpeta_output_candidato, "log.txt")
                            if os.path.exists(log_path):
                                subir_archivo_txt_a_drive(log_path, "log.txt", nombre_completo, carpeta_drive_id)

                            break

                        else:
                            print("⚠️ Respuesta inválida. Por favor, ingresa 's' o 'n'.")
                except Exception as e:
                    print(f"❌ Error al generar la evaluación para {nombre_completo}: {e}")
                    loggear(nombre_completo, f"❌ Error al generar la evaluación para {nombre_completo}: {e}")
        except Exception as e:
            print(f"❌ Error al procesar al candidato {nombre_carpeta}: {e}")
            loggear(nombre_carpeta, f"❌ Error al procesar al candidato {nombre_carpeta}: {e}")

    loggear("Global", "🟢 Fin del procesamiento de candidatos")
