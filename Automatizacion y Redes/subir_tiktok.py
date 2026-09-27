"""
Continuum Lab - TikTok Automated Publisher (tiktok-uploader / Playwright)
Uploads vertical 9:16 scientific animations to TikTok with automated captioning and hashtag distribution.
Includes resilient modal and overlay dismissal for 2026 TikTok creator center web UI.
"""
import os
import sys
import time

if sys.stdout:
    sys.stdout.reconfigure(encoding="utf-8")

import tiktok_uploader.upload as tt_upload
from tiktok_uploader.upload import upload_video
from tiktok_uploader import config
from playwright.sync_api import Page

CREDENTIALS_DIR = os.path.dirname(os.path.abspath(__file__))
COOKIES_FILE = os.path.join(CREDENTIALS_DIR, "tiktok_cookies.txt")

def _dismiss_tiktok_modals(page: Page):
    """Dismiss any copyright, onboarding, or tutorial modals from the TikTok upload UI."""
    try:
        page.keyboard.press("Escape")
        time.sleep(0.5)
        # Click common dismissal buttons
        for btn in page.locator("button:has-text('Got it'), button:has-text('OK'), button:has-text('Entendido'), button:has-text('Dismiss'), button:has-text('Accept')").all():
            try:
                if btn.is_visible():
                    btn.click(force=True)
            except Exception:
                pass
        # Force-remove overlay elements that intercept clicks
        page.evaluate("""() => {
            const overlays = document.querySelectorAll('.TUXModal-overlay, [data-floating-ui-portal]');
            overlays.forEach(el => el.remove());
        }""")
    except Exception as e:
        pass

# Robust patched version of complete_upload_form
orig_complete = tt_upload.complete_upload_form

def resilient_complete_upload_form(page, path, description, schedule, skip_split_window, cover_path=None, product_id=None, visibility="everyone", num_retries=1, headless=False, *args, **kwargs):
    tt_upload._go_to_upload(page)
    tt_upload._remove_cookies_window(page)
    _dismiss_tiktok_modals(page)

    tt_upload._set_video(page, path=path, num_retries=num_retries, **kwargs)

    # Wait for initial upload processing
    time.sleep(3)
    _dismiss_tiktok_modals(page)

    if cover_path:
        tt_upload._set_cover(page, cover_path)
    if not skip_split_window:
        tt_upload._remove_split_window(page)

    _dismiss_tiktok_modals(page)
    tt_upload._set_interactivity(page, **kwargs)
    _dismiss_tiktok_modals(page)

    tt_upload._set_description(page, description)

    if visibility != "everyone":
        tt_upload._set_visibility(page, visibility)
    if schedule:
        tt_upload._set_schedule_video(page, schedule)
    if product_id:
        tt_upload._add_product_link(page, product_id)

    _dismiss_tiktok_modals(page)
    tt_upload._post_video(page)

# Robust patched version of _set_description
orig_set_desc = tt_upload._set_description

def resilient_set_description(page: Page, description: str) -> None:
    if description is None:
        return
    _dismiss_tiktok_modals(page)
    try:
        desc_xpath = config.selectors.upload.description
        desc_locator = page.locator(f"xpath={desc_xpath}")
        desc_locator.wait_for(state="visible", timeout=20000)
        
        # Use force click to bypass any overlay interception
        desc_locator.click(force=True)
        time.sleep(0.5)
        
        # Clear existing text
        page.keyboard.press("Control+A")
        page.keyboard.press("Backspace")
        time.sleep(0.5)

        # Type words and hashtags
        words = description.split(" ")
        for word in words:
            if not word:
                continue
            if word.startswith("#"):
                desc_locator.press_sequentially(word, delay=40)
                time.sleep(0.4)
                try:
                    mention_box = page.locator(f"xpath={config.selectors.upload.mention_box}")
                    if mention_box.is_visible(timeout=1500):
                        page.keyboard.press("Enter")
                    else:
                        page.keyboard.press("Space")
                except Exception:
                    page.keyboard.press("Space")
            else:
                desc_locator.press_sequentially(word + " ", delay=20)
                
        print("[OK] Descripcion y hashtags inyectados exitosamente en TikTok.")
    except Exception as e:
        print(f"[!] Aviso en set_description: {e}. Aplicando metodo alternativo...")
        _dismiss_tiktok_modals(page)
        orig_set_desc(page, description)

tt_upload.complete_upload_form = resilient_complete_upload_form
tt_upload._set_description = resilient_set_description

def upload_to_tiktok(video_path, description, headless=True):
    if not os.path.exists(COOKIES_FILE):
        print(f"\n[!] AVISO: No se encontro el archivo de cookies: {COOKIES_FILE}")
        return False

    print(f"Iniciando subida autonoma a TikTok: {os.path.basename(video_path)}...")
    try:
        failed = upload_video(
            filename=video_path,
            description=description,
            cookies=COOKIES_FILE,
            browser="chromium",
            headless=headless
        )
        if not failed:
            print("[OK] Video publicado exitosamente en TikTok!")
            return True
        else:
            print(f"[!] No se pudo completar la publicacion: {failed}")
            return False
    except Exception as e:
        print(f"[X] Error durante la carga a TikTok: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) > 2:
        upload_to_tiktok(sys.argv[1], sys.argv[2])
    else:
        print("Modulo TikTok Publisher activo.")
