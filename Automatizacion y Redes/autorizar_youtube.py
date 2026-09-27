"""
Continuum Lab - Asistente de Autorización Segura de YouTube
Abre el navegador para vincular EXCLUSIVAMENTE el canal secundario 'Continuum Lab'.
Verifica el ID y título del canal antes de guardar el token definitivo.
"""
import os
import sys

if sys.stdout:
    sys.stdout.reconfigure(encoding="utf-8")

from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube"
]

CREDENTIALS_DIR = os.path.dirname(os.path.abspath(__file__))
CLIENT_SECRETS_FILE = os.path.join(CREDENTIALS_DIR, "client_secret.json")
TOKEN_FILE = os.path.join(CREDENTIALS_DIR, "token.json")

def authorize_channel():
    if not os.path.exists(CLIENT_SECRETS_FILE):
        print(f"[X] No se encontro client_secret.json en: {CLIENT_SECRETS_FILE}")
        return False

    print("=" * 65)
    print("CONTINUUM LAB // AUTORIZACION SEGURA DE YOUTUBE")
    print("=" * 65)
    print("Se abrira tu navegador web en la pagina de inicio de sesion de Google.")
    print("\nPASO CRUCIAL:")
    print("-> Cuando Google te pregunte 'Elige una cuenta o canal':")
    print("   SELECCIONA: 'Continuum Lab' (tu canal secundario).")
    print("   NO selecciones tu cuenta personal.\n")
    print("Iniciando servidor local de autenticacion...")

    flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES)
    creds = flow.run_local_server(port=0)

    # Validar canal vinculado
    youtube = build("youtube", "v3", credentials=creds)
    resp = youtube.channels().list(mine=True, part="snippet").execute()
    items = resp.get("items", [])
    
    if not items:
        print("[!] No se encontro ningun canal de YouTube en la cuenta autorizada.")
        return False

    channel_name = items[0]["snippet"]["title"]
    channel_id = items[0]["id"]

    print("-" * 65)
    print(f"Canal vinculado detectado: '{channel_name}' (ID: {channel_id})")
    
    if "continu" in channel_name.lower():
        print(f"[OK] CANAL CORRECTO VINCULADO: '{channel_name}'")
        with open(TOKEN_FILE, "w", encoding="utf-8") as f:
            f.write(creds.to_json())
        print(f"[OK] Credencial persistente guardada en: {TOKEN_FILE}")
        print("A partir de este momento, todas las subidas de YouTube Shorts seran 100% automaticas.")
        return True
    else:
        print(f"\n[!] ALERTA: Vinculaste el canal '{channel_name}', que NO es Continuum Lab.")
        print("Por seguridad, el token NO ha sido guardado para evitar subir contenido a tu cuenta personal.")
        print("Vuelve a ejecutar este script y en la pantalla de Google asegurate de elegir 'Continuum Lab'.\n")
        return False

if __name__ == "__main__":
    authorize_channel()
