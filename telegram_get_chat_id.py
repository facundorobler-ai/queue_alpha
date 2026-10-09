"""Muestra los chat_id de mensajes recibidos por el bot, sin revelar el token."""
import tls_setup  # Configura TLS antes de importar urllib.

import json
import os
from urllib.error import HTTPError, URLError
from urllib.request import urlopen


def main() -> None:
    token = os.getenv("BOCA_TELEGRAM_BOT_TOKEN", "").strip()
    if not token:
        raise SystemExit('Falta BOCA_TELEGRAM_BOT_TOKEN. Configuralo en esta misma ventana de CMD.')

    url = f"https://api.telegram.org/bot{token}/getUpdates"
    try:
        with urlopen(url, timeout=10) as response:
            data = json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        raise SystemExit(
            f"Telegram respondió HTTP {exc.code}. Revisá el token y que el bot exista."
        ) from None
    except URLError as exc:
        # Mostramos el motivo de conexión, pero nunca la URL completa porque contiene el token.
        motivo = getattr(exc, "reason", exc)
        raise SystemExit(
            "No se pudieron consultar los mensajes (URLError).\n"
            f"Detalle de conexión: {type(motivo).__name__}: {motivo}\n"
            "Puede deberse a DNS, conexión, proxy, firewall o validación TLS; "
            "este mensaje por sí solo no indica que el token sea incorrecto."
        ) from None
    except (TimeoutError, OSError, ValueError) as exc:
        raise SystemExit(
            f"No se pudieron consultar los mensajes: {type(exc).__name__}: {exc}"
        ) from None

    if not data.get("ok"):
        raise SystemExit(f"Telegram informó un error: {data.get('description', 'desconocido')}")

    encontrados = set()
    for update in data.get("result", []):
        message = update.get("message") or update.get("edited_message") or update.get("channel_post")
        if message and message.get("chat", {}).get("id") is not None:
            encontrados.add(str(message["chat"]["id"]))

    if not encontrados:
        print("Todavía no hay mensajes recibidos.")
        print("Abrí el chat de tu bot en Telegram, tocá Iniciar o enviá /start y volvé a ejecutar este archivo.")
        return

    print("Chat ID encontrados (elegí el de tu chat personal):")
    for chat_id in sorted(encontrados):
        print(chat_id)
    print('\nConfigurá el elegido con: set "BOCA_TELEGRAM_CHAT_ID=ID_AQUI"')


if __name__ == "__main__":
    main()
