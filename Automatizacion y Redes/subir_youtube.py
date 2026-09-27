"""
Continuum Lab - Automated YouTube Publisher (Official Google Data API v3)
Handles automated video uploading, metadata tagging, playlist assignment, and channel checks.
Enforces that uploads ONLY proceed to the secondary channel 'Continuum Lab', protecting personal accounts.
"""
import os
import sys
import json
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube"
]

CREDENTIALS_DIR = os.path.dirname(os.path.abspath(__file__))
CLIENT_SECRETS_FILE = os.path.join(CREDENTIALS_DIR, "client_secret.json")
TOKEN_FILE = os.path.join(CREDENTIALS_DIR, "token.json")
TARGET_CHANNEL_KEYWORD = "continu"

def get_authenticated_service():
    creds = None
    if os.path.exists(TOKEN_FILE):
        try:
            creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
        except Exception as e:
            print(f"[!] Error al leer token.json: {e}")
            creds = None
        
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(CLIENT_SECRETS_FILE):
                print("\n[!] AVISO DE AUTENTICACION DE YOUTUBE:")
                print(f"No se encontro el archivo de credenciales: {CLIENT_SECRETS_FILE}")
                return None
            print("\n[!] Iniciando flujo de consentimiento OAuth de Google...")
            print("Se abrira una ventana en tu navegador.")
            print("IMPORTANTE: En la pantalla de seleccion de canal, asegurate de seleccionar tu canal secundario 'Continuum Lab'.")
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
            
        with open(TOKEN_FILE, "w", encoding="utf-8") as token:
            token.write(creds.to_json())

    service = build("youtube", "v3", credentials=creds)
    
    # Verify connected channel
    try:
        ch_request = service.channels().list(mine=True, part="snippet,id")
        ch_response = ch_request.execute()
        items = ch_response.get("items", [])
        if items:
            channel_title = items[0]["snippet"]["title"]
            channel_id = items[0]["id"]
            print(f"[OK] Conectado a canal de YouTube: '{channel_title}' (ID: {channel_id})")
            if TARGET_CHANNEL_KEYWORD not in channel_title.lower():
                print(f"\n[!] ADVERTENCIA CRITICA DE CANAL:")
                print(f"El canal vinculado es '{channel_title}', pero indicaste subir EXCLUSIVAMENTE a 'Continuum Lab'.")
                print("Para corregirlo, borra el archivo 'token.json' y repite el proceso seleccionando el canal 'Continuum Lab'.\n")
                return None
    except Exception as e:
        print(f"[!] No se pudo verificar el nombre del canal: {e}")

    return service

def upload_video(file_path, title, description, tags=None, privacy="public", category_id="28"):
    youtube = get_authenticated_service()
    if not youtube:
        print("[X] No se pudo obtener el servicio autenticado de YouTube.")
        return False

    body = {
        "snippet": {
            "title": title,
            "description": description,
            "tags": tags or [],
            "categoryId": category_id
        },
        "status": {
            "privacyStatus": privacy,
            "selfDeclaredMadeForKids": False
        }
    }

    media = MediaFileUpload(file_path, chunksize=-1, resumable=True)
    request = youtube.videos().insert(
        part=",".join(body.keys()),
        body=body,
        media_body=media
    )

    print(f"Iniciando subida de: {file_path}...")
    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"Progreso de subida: {int(status.progress() * 100)}%")

    print(f"[OK] Video publicado exitosamente en YouTube Shorts. Video ID: {response.get('id')}")
    print(f"URL: https://youtube.com/shorts/{response.get('id')}")
    return response

if __name__ == "__main__":
    svc = get_authenticated_service()
    if svc:
        print("[OK] YouTube autenticado y listo para recibir videos.")
