"""
Continuum Lab - Universal Multi-Platform Social Media Publisher
Simultaneously broadcasts vertical simulations across YouTube Shorts, TikTok, and Instagram Reels.
Enforces strict account/channel filters to ensure publication ONLY occurs on 'Continuum Lab'.
"""
import os
import sys

if sys.stdout:
    sys.stdout.reconfigure(encoding="utf-8")
import argparse
from publicador_metadata import generate_social_payload
from subir_youtube import upload_video as upload_yt, TOKEN_FILE as YT_TOKEN_FILE
from subir_instagram import upload_reel as upload_ig
from subir_tiktok import upload_to_tiktok as upload_tt

def publish_everywhere(video_path, title_concept, topic="fourier_series", cover_path=None, platforms="all"):
    if not os.path.exists(video_path):
        print(f"[X] El archivo de video no existe: {video_path}")
        return False

    print("=" * 70)
    print("CONTINUUM LAB // UNIVERSAL MULTI-PLATFORM BROADCAST ENGINE")
    print(f"Concept: {title_concept}")
    print(f"Topic:   {topic}")
    print(f"Video:   {video_path}")
    if cover_path:
        print(f"Cover:   {cover_path}")
    print(f"Targets: {platforms}")
    print("=" * 70)

    payload = generate_social_payload(video_id="01", title_concept=title_concept, topic=topic)
    results = {}
    target_list = [p.strip().lower() for p in platforms.split(",")] if platforms != "all" else ["instagram", "tiktok", "youtube"]

    # 1. Instagram Reels (Account: @continuumlab_)
    if "instagram" in target_list or "all" in target_list:
        print("\n" + "-" * 50)
        print("[1/3] BROADCASTING TO INSTAGRAM REELS (@continuumlab_)...")
        print("-" * 50)
        ig_caption = payload["instagram"]["caption"]
        try:
            ig_res = upload_ig(video_path=video_path, caption=ig_caption, cover_path=cover_path)
            results["instagram"] = bool(ig_res)
        except Exception as e:
            print(f"[X] Instagram error: {e}")
            results["instagram"] = False

    # 2. TikTok (Continuum Lab)
    if "tiktok" in target_list or "all" in target_list:
        print("\n" + "-" * 50)
        print("[2/3] BROADCASTING TO TIKTOK...")
        print("-" * 50)
        tt_caption = payload["tiktok"]["caption"]
        try:
            tt_res = upload_tt(video_path=video_path, description=tt_caption)
            results["tiktok"] = bool(tt_res)
        except Exception as e:
            print(f"[X] TikTok error: {e}")
            results["tiktok"] = False

    # 3. YouTube Shorts (Channel: Continuum Lab)
    if "youtube" in target_list or "all" in target_list:
        print("\n" + "-" * 50)
        print("[3/3] BROADCASTING TO YOUTUBE SHORTS (Continuum Lab)...")
        print("-" * 50)
        yt_data = payload["youtube"]
        try:
            yt_res = upload_yt(
                file_path=video_path,
                title=yt_data["title"],
                description=yt_data["description"],
                tags=yt_data["tags"],
                privacy=yt_data["privacy_status"],
                category_id=yt_data["category_id"]
            )
            results["youtube"] = bool(yt_res)
        except Exception as e:
            print(f"[X] YouTube error: {e}")
            results["youtube"] = False

    print("\n" + "=" * 70)
    print("RESUMEN DE TRANSMISION MULTICANAL:")
    for plat, ok in results.items():
        status_str = "EXITOSO [OK]" if ok else "FALLIDO O PENDIENTE [X]"
        print(f" - {plat.upper()}: {status_str}")
    print("=" * 70)
    return results

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Publicador Multicanal de Continuum Lab")
    parser.add_argument("--video", required=False, help="Ruta al video MP4 9:16")
    parser.add_argument("--title", required=False, default="Drawing Any Shape with Rotating Circles", help="Concepto del video")
    parser.add_argument("--topic", required=False, default="fourier_series", help="Topico de hashtags (fourier_series, lbm_karman, airfoil_aerodynamics)")
    parser.add_argument("--cover", required=False, help="Ruta a la miniatura/portada")
    parser.add_argument("--platforms", required=False, default="instagram,tiktok", help="Plataformas: instagram, tiktok, youtube, o all")
    args = parser.parse_args()

    default_video = r"c:\Users\andre\OneDrive\Desktop\Continuum Lab\RENDERS\3 Series de Fourier Geometricas\videos\Geometric Fourier Series EN.mp4"
    default_cover = r"c:\Users\andre\OneDrive\Desktop\Continuum Lab\RENDERS\3 Series de Fourier Geometricas\extra\capturas\fourier_shapes_hero.png"

    v_path = args.video or default_video
    c_path = args.cover or (default_cover if os.path.exists(default_cover) else None)

    publish_everywhere(
        video_path=v_path,
        title_concept=args.title,
        topic=args.topic,
        cover_path=c_path,
        platforms=args.platforms
    )
