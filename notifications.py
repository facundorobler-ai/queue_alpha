"""Alertas locales y notificaciones opcionales por Telegram."""
import tls_setup  # Configura TLS antes de importar urllib.

import json
import os
import sys
import threading
import time
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, TELEGRAM_TIMEOUT
from logging_utils import log
from state import AppState


def beep() -> None:
    """Emite una alerta sonora repetida según el sistema operativo."""
    try:
        if sys.platform == "win32":
            import winsound
            for _ in range(5):
                winsound.Beep(1000, 300)
                time.sleep(0.1)
        elif sys.platform == "darwin":
            os.system('say "Entra ya, entra ya"')
        else:
            for _ in range(5):
                os.system('echo -e "\\a"')
                time.sleep(0.2)
    except Exception:
        pass


def telegram_configurado() -> bool:
    """Indica si hay token y chat ID configurados."""
    return bool(TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID)


def enviar_telegram(mensaje: str) -> bool:
    """Envía un mensaje con la API oficial de Telegram (sin dependencias externas).

    Se usa desde un hilo independiente para no bloquear la monitorización.
    """
    if not telegram_configurado():
        return False

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    body = urlencode({"chat_id": TELEGRAM_CHAT_ID, "text": mensaje}).encode("utf-8")
    request = Request(url, data=body, headers={"Content-Type": "application/x-www-form-urlencoded"}, method="POST")
    try:
        with urlopen(request, timeout=TELEGRAM_TIMEOUT) as response:
            payload = json.loads(response.read().decode("utf-8"))
        if payload.get("ok"):
            log("📨 Telegram: notificación enviada.")
            return True
        log(f"[AVISO] Telegram rechazó la notificación: {payload.get('description', 'error desconocido')}")
    except HTTPError as exc:
        # No registramos la URL para evitar que el token aparezca en los logs.
        log(f"[AVISO] Telegram respondió con HTTP {exc.code}.")
    except (URLError, TimeoutError, OSError, ValueError) as exc:
        log(f"[AVISO] No se pudo enviar la notificación por Telegram: {type(exc).__name__}.")
    return False


def _enviar_telegram_en_segundo_plano(mensaje: str) -> None:
    if telegram_configurado():
        threading.Thread(
            target=enviar_telegram, args=(mensaje,), daemon=True, name="telegram-notification"
        ).start()


def alertar(state: AppState, nombre: str, minutos: int) -> None:
    """Aviso local cuando el tiempo estimado llega al umbral configurado."""
    log(f"\n{'=' * 50}")
    log(f"🚨 ALERTA: {nombre} entra en {minutos} min!")
    log("👉 Revisá esa ventana y preparate para continuar manualmente.")
    log(f"{'=' * 50}\n")

    with state.lock:
        debe_sonar = nombre not in state.ya_alerto
        if debe_sonar:
            state.ya_alerto.add(nombre)

    if debe_sonar:
        threading.Thread(target=beep, daemon=True).start()


def alerta_entrando(nombre: str) -> None:
    """Aviso cuando el monitor detecta una página de ingreso tras ver la fila."""
    log(f"\n{'*' * 50}")
    log(f"🟢 {nombre}: se detectó una pantalla de ingreso.")
    log("🔎 Revisá la ventana para confirmar que sea el paso esperado.")
    log(f"{'*' * 50}\n")
    threading.Thread(target=beep, daemon=True).start()
    _enviar_telegram_en_segundo_plano(
        f"🟢 Boca Socios: {nombre} salió de la fila virtual y llegó a una pantalla de ingreso. "
        "Revisá esa ventana en tu computadora para confirmar y continuar."
    )
