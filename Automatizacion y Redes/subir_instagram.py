"""
Continuum Lab - Instagram Reels Automated Publisher (instagrapi)
Uploads vertical 9:16 simulations directly to Instagram Reels with custom captions, hashtags, and covers.
Enforces strict security checks to ensure uploads ONLY go to @continuumlab_ (never personal accounts).
"""
import os
import sys

if sys.stdout:
    sys.stdout.reconfigure(encoding="utf-8")
from pathlib import Path
from instagrapi import Client

CREDENTIALS_DIR = os.path.dirname(os.path.abspath(__file__))
SESSION_FILE = os.path.join(CREDENTIALS_DIR, "ig_session.json")
TARGET_ACCOUNT = "continuumlab_"

def get_instagram_client(username=None, password=None):
    cl = Client()
    if os.path.exists(SESSION_FILE):
        try:
            cl.load_settings(SESSION_FILE)
            account_info = cl.account_info()
            print(f"[OK] Sesion persistente de Instagram activa: @{account_info.username} (ID: {account_info.pk})")
            
            # MANDATORY SECURITY GUARD: Prevent uploading to personal account
            if TARGET_ACCOUNT.lower() not in account_info.username.lower() and "continu" not in account_info.username.lower():
                raise PermissionError(
                    f"ALERTA DE SEGURIDAD: La cuenta activa es @{account_info.username}, "
                    f"pero las instrucciones del usuario exigen publicar EXCLUSIVAMENTE en @{TARGET_ACCOUNT}."
                )
            return cl
        except Exception as e:
            print(f"[!] Error al verificar sesion existente: {e}")
            if "ALERTA DE SEGURIDAD" in str(e):
                raise

    if not username or not password:
        print("\n[!] AVISO DE AUTENTICACION DE INSTAGRAM:")
        print("Para publicar Reels automaticamente, se requiere iniciar sesion una unica vez.")
        print("Ejecuta: python subir_instagram.py --login <tu_usuario> <tu_password>")
        print("La sesion se guardara en 'ig_session.json' y no volveras a ingresar credenciales.\n")
        return None

    try:
        print(f"Iniciando sesion en Instagram como @{username}...")
        cl.login(username, password)
        account_info = cl.account_info()
        if TARGET_ACCOUNT.lower() not in account_info.username.lower() and "continu" not in account_info.username.lower():
            raise PermissionError(f"Cuenta iniciada es @{account_info.username}, no @{TARGET_ACCOUNT}.")
        cl.dump_settings(SESSION_FILE)
        print(f"[OK] Sesion guardada permanentemente en ig_session.json para @{account_info.username}.")
        return cl
    except Exception as e:
        print(f"[X] Error en el inicio de sesion: {e}")
        return None

def upload_reel(video_path, caption, cover_path=None):
    cl = get_instagram_client()
    if not cl:
        return False

    vpath = Path(video_path)
    cpath = Path(cover_path) if cover_path and os.path.exists(cover_path) else None

    print(f"Subiendo Reel a Instagram (@{cl.account_info().username}): {vpath.name}...")
    try:
        media = cl.clip_upload(
            path=vpath,
            caption=caption,
            thumbnail=cpath
        )
        print(f"[OK] Reel publicado exitosamente en Instagram!")
        print(f"Media ID: {media.pk}")
        print(f"URL: https://www.instagram.com/reel/{media.code}/")
        return media
    except Exception as e:
        print(f"[X] Fallo la subida a Instagram: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) >= 4 and sys.argv[1] == "--login":
        get_instagram_client(username=sys.argv[2], password=sys.argv[3])
    else:
        print("Modulo Instagram Reels inicializado.")
        get_instagram_client()
