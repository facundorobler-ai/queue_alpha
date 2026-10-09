"""Envía un mensaje de prueba a la cuenta configurada."""
import os
import sys

from notifications import enviar_telegram, telegram_configurado


def main() -> None:
    if not os.getenv("BOCA_TELEGRAM_BOT_TOKEN", "").strip():
        sys.exit('Falta BOCA_TELEGRAM_BOT_TOKEN en esta ventana de CMD.')
    if not os.getenv("BOCA_TELEGRAM_CHAT_ID", "").strip():
        sys.exit('Falta BOCA_TELEGRAM_CHAT_ID en esta ventana de CMD.')
    if not telegram_configurado():
        sys.exit("Telegram no quedó configurado.")

    if enviar_telegram("✅ Prueba correcta: el monitor de Boca Socios puede enviarte notificaciones por Telegram."):
        print("Mensaje de prueba enviado. Revisá Telegram.")
    else:
        sys.exit("No se pudo enviar el mensaje. Revisá el token, chat ID y conexión.")


if __name__ == "__main__":
    main()
