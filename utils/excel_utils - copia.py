from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import os

SERVICE_ACCOUNT_FILE = 'sfai-talents-ai-hiring-f5aa291b8446.json'
SCOPES = ['https://www.googleapis.com/auth/drive', 'https://www.googleapis.com/auth/spreadsheets']
TEMPLATE_XLSX_PATH = 'input/[TEMPLATE][SFAI-open] Talents - Onboarding _ Credentials of _FULL NAME_.xlsx'

def verificar_credenciales():
    """Autentica usando el archivo de servicio y devuelve servicios de Sheets y Drive."""
    if not os.path.exists(SERVICE_ACCOUNT_FILE):
        print(f"❌ El archivo de credenciales no se encuentra en la ruta: {SERVICE_ACCOUNT_FILE}")
        return None

    try:
        creds = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, scopes=SCOPES
        )
        drive_service = build('drive', 'v3', credentials=creds)
        sheets_service = build('sheets', 'v4', credentials=creds)
        print("✅ Autenticación exitosa.")
        return sheets_service, drive_service
    except Exception as e:
        print(f"❌ Error de autenticación: {e}")
        return None

def crear_hoja_credenciales(nombre_completo, correo_personal, carpeta_drive_id):
    """Crea una hoja de credenciales duplicando una plantilla, personalizándola y subiéndola a Drive."""
    resultado = verificar_credenciales()
    if not resultado:
        return None
    sheets_service, drive_service = resultado

    try:
        nombre_drive = f"[SFAI-open] Talents - {nombre_completo} - Credentials"

        if not os.path.exists(TEMPLATE_XLSX_PATH):
            print(f"❌ No se encontró la plantilla local en: {TEMPLATE_XLSX_PATH}")
            return None

        file_metadata = {
            'name': nombre_drive,
            'parents': [carpeta_drive_id],
            'mimeType': 'application/vnd.google-apps.spreadsheet'
        }
        media = MediaFileUpload(
            TEMPLATE_XLSX_PATH,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        archivo_creado = drive_service.files().create(
            body=file_metadata,
            media_body=media,
            supportsAllDrives=True  # Aseguramos que es compatible con unidades compartidas
        ).execute()
        nueva_hoja_id = archivo_creado.get('id')
        print(f"✅ Hoja creada en Drive: {nueva_hoja_id}")

        # Insertar datos básicos
        valores = [[nombre_completo, correo_personal]]
        sheets_service.spreadsheets().values().update(
            spreadsheetId=nueva_hoja_id,
            range="B4:C4",
            valueInputOption="RAW",
            body={"values": valores}
        ).execute()
        print("✅ Datos del usuario actualizados en la hoja.")

        # Leer y modificar valores generales
        try:
            sheet_data = sheets_service.spreadsheets().values().get(
                spreadsheetId=nueva_hoja_id,
                range="A1:Z100"
            ).execute()
            valores_originales = sheet_data.get("values", [])
        except Exception as e:
            print(f"⚠️ No se pudieron leer los valores de la hoja: {e}")
            return None

        nuevos_valores = []
        correo_empresa = nombre_completo.lower().replace(" ", ".") + "@softwarefactoryai.com"

        for fila in valores_originales:
            nueva_fila = []
            for celda in fila:
                celda_modificada = celda.replace(
                    "NOMBRE.APELLIDO@softwarefactoryai.com", correo_empresa
                ).replace("PERSONAL@gmail.com", correo_personal)
                nueva_fila.append(celda_modificada)
            nuevos_valores.append(nueva_fila)

        sheets_service.spreadsheets().values().update(
            spreadsheetId=nueva_hoja_id,
            range="A1:Z100",
            valueInputOption="RAW",
            body={"values": nuevos_valores}
        ).execute()
        print("✅ Correos actualizados en todas las celdas relevantes.")

        # Permiso público
        drive_service.permissions().create(
            fileId=nueva_hoja_id,
            body={'role': 'reader', 'type': 'anyone'},
            supportsAllDrives=True  # Asegura que el permiso se aplique correctamente en unidades compartidas
        ).execute()

        enlace = f"https://docs.google.com/spreadsheets/d/{nueva_hoja_id}/edit"
        print(f"✅ Hoja disponible en Drive: {enlace}")

        return enlace

    except Exception as e:
        print(f"❌ Error al crear o actualizar la hoja: {e}")
        return None

def subir_responsabilidades_a_drive(ruta_local_docx, nombre_completo, carpeta_drive_id):
    """Sube el archivo de responsabilidades a Drive con permisos públicos."""
    resultado = verificar_credenciales()
    if not resultado:
        return None
    _, drive_service = resultado

    try:
        nombre_drive = f"[SFAI-open] Talents - {nombre_completo} - Responsabilidades"

        file_metadata = {
            'name': nombre_drive + ".docx",
            'parents': [carpeta_drive_id],
            'mimeType': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        }
        media = MediaFileUpload(
            ruta_local_docx,
            mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        )

        archivo_creado = drive_service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id',
            supportsAllDrives=True  # Asegura que la carga funcione en unidades compartidas
        ).execute()

        file_id = archivo_creado.get('id')
        print(f"✅ Archivo de responsabilidades subido a Drive: {file_id}")

        drive_service.permissions().create(
            fileId=file_id,
            body={'role': 'reader', 'type': 'anyone'},
            supportsAllDrives=True  # Asegura que el permiso se aplique correctamente en unidades compartidas
        ).execute()

        enlace_drive = f"https://drive.google.com/file/d/{file_id}/view"
        print(f"✅ Enlace compartible del archivo: {enlace_drive}")
        return enlace_drive

    except Exception as e:
        print(f"❌ Error al subir el archivo de responsabilidades a Drive: {e}")
        return None
