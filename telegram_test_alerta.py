"""Prueba controlada de la misma función de alerta que usa el monitor.

Guardá este archivo en la carpeta donde está main.py y ejecutalo con el
entorno virtual y las variables de Telegram ya configuradas.
"""
import time

import tls_setup  # Configura TLS antes de cualquier solicitud HTTPS.
from notifications import alerta_entrando, telegram_configurado


def main() -> None:
    if not telegram_configurado():
        raise SystemExit(
            "Telegram no está configurado en esta terminal. Definí "
            "BOCA_TELEGRAM_BOT_TOKEN y BOCA_TELEGRAM_CHAT_ID primero."
        )

    print("Enviando una alerta de prueba (no se está comprobando una fila real)...")
    alerta_entrando("PRUEBA-Chrome-1")
    # alerta_entrando envía Telegram en un hilo daemon; esperar permite que termine.
    time.sleep(10)
    print("Prueba finalizada. Revisá Telegram y la consola para ver el resultado.")


if __name__ == "__main__":
    main()
