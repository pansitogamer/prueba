import os
import re
import io
from datetime import datetime
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload, MediaFileUpload
from dotenv import load_dotenv

load_dotenv()

# Autenticación PyDrive
gauth = GoogleAuth()
gauth.LoadCredentialsFile("credentials.json")

if gauth.credentials is None:
    gauth.LocalWebserverAuth()
elif gauth.access_token_expired:
    gauth.Refresh()
else:
    gauth.Authorize()

gauth.SaveCredentialsFile("credentials.json")
drive = GoogleDrive(gauth)

# Autenticación Google Sheets
SCOPES = ['https://www.googleapis.com/auth/drive', 'https://www.googleapis.com/auth/spreadsheets']
SERVICE_ACCOUNT_FILE = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

credentials = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
sheets_service = build('sheets', 'v4', credentials=credentials)
drive_service = build('drive', 'v3', credentials=credentials)

def crear_carpeta_candidato_en_drive(nombre_candidato, carpeta_padre_id):
    file_metadata = {
        'title': nombre_candidato,
        'parents': [{'id': carpeta_padre_id}],
        'mimeType': 'application/vnd.google-apps.folder'
    }
    carpeta = drive.CreateFile(file_metadata)
    carpeta.Upload()
    return carpeta['id']

def subir_minuta_a_drive(path_local, nombre_candidato, carpeta_id):
    archivo_drive = drive.CreateFile({
        'title': os.path.basename(path_local),
        'parents': [{'id': carpeta_id}]
    })
    archivo_drive.SetContentFile(path_local)
    archivo_drive.Upload()
    return f"https://drive.google.com/file/d/{archivo_drive['id']}/view"

def subir_evaluacion_a_drive(path_local, nombre_candidato, carpeta_id):
    archivo_drive = drive.CreateFile({
        'title': os.path.basename(path_local),
        'parents': [{'id': carpeta_id}]
    })
    archivo_drive.SetContentFile(path_local)
    archivo_drive.Upload()
    return f"https://drive.google.com/file/d/{archivo_drive['id']}/view"

def subir_archivo_txt_a_drive(path_local, nombre_archivo, nombre_candidato, carpeta_id):
    archivo_drive = drive.CreateFile({
        'title': nombre_archivo,
        'parents': [{'id': carpeta_id}]
    })
    archivo_drive.SetContentFile(path_local)
    archivo_drive.Upload()
    return f"https://drive.google.com/file/d/{archivo_drive['id']}/view"

def crear_hoja_credenciales(nombre_candidato, correo, carpeta_drive_id):
    spreadsheet = {
        'properties': {
            'title': f'Credenciales - {nombre_candidato}'
        },
        'parents': [carpeta_drive_id]
    }

    sheet = sheets_service.spreadsheets().create(body=spreadsheet, fields='spreadsheetId').execute()
    sheet_id = sheet.get('spreadsheetId')

    values = [
        ['Nombre', 'Correo', 'Fecha de creación'],
        [nombre_candidato, correo, datetime.now().strftime("%Y-%m-%d")]
    ]
    body = {'values': values}

    sheets_service.spreadsheets().values().update(
        spreadsheetId=sheet_id,
        range="A1:C2",
        valueInputOption="RAW",
        body=body
    ).execute()

    # Mover el archivo a la carpeta correspondiente
    drive_service.files().update(
        fileId=sheet_id,
        addParents=carpeta_drive_id,
        removeParents='root',
        fields='id, parents'
    ).execute()

    return f"https://docs.google.com/spreadsheets/d/{sheet_id}/edit"

def subir_responsabilidades_a_drive(path_local, nombre_candidato, carpeta_id):
    archivo_drive = drive.CreateFile({
        'title': os.path.basename(path_local),
        'parents': [{'id': carpeta_id}]
    })
    archivo_drive.SetContentFile(path_local)
    archivo_drive.Upload()
    return archivo_drive['id']

def listar_subcarpetas_drive(carpeta_padre_id):
    query = f"'{carpeta_padre_id}' in parents and mimeType = 'application/vnd.google-apps.folder' and trashed = false"
    resultado = drive.ListFile({'q': query}).GetList()
    return [{'id': carpeta['id'], 'name': carpeta['title']} for carpeta in resultado]

def descargar_archivos_carpeta_drive(carpeta_id, carpeta_local_destino):
    query = f"'{carpeta_id}' in parents and trashed = false"
    archivos = drive.ListFile({'q': query}).GetList()
    os.makedirs(carpeta_local_destino, exist_ok=True)

    for archivo in archivos:
        nombre = archivo['title']
        path_destino = os.path.join(carpeta_local_destino, nombre)
        archivo.GetContentFile(path_destino)
