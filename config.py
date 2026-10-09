"""Configuración central del monitor Boca Socios.

Las credenciales NO se guardan aquí: se leen desde variables de entorno
cuando se necesita completar el formulario de acceso.
"""
import os

URL = "https://bocasocios.bocajuniors.com.ar/auth/login"


def _int_env(nombre: str, predeterminado: int) -> int:
    valor = os.getenv(nombre)
    if not valor:
        return predeterminado
    try:
        return int(valor)
    except ValueError as exc:
        raise ValueError(f"La variable {nombre} debe ser un número entero.") from exc


# Se conserva la configuración base del programa original. Se puede cambiar
# sin editar el código, por ejemplo: set BOCA_CANTIDAD_POR_TIPO=1 en CMD.
CANTIDAD_POR_TIPO = _int_env("BOCA_CANTIDAD_POR_TIPO", 14)
DELAY = _int_env("BOCA_DELAY", 1)
INTERVALO_DETECCION = _int_env("BOCA_INTERVALO_DETECCION", 5)
INTERVALO_RANKING = _int_env("BOCA_INTERVALO_RANKING", 10)
TIMEOUT_PAGINA = _int_env("BOCA_TIMEOUT_PAGINA", 30)
MINUTOS_ALERTA = _int_env("BOCA_MINUTOS_ALERTA", 2)
MAS_DE_UNA_HORA = 9999
HISTORIAL_MAX = 5
LOG_FILE = os.getenv("BOCA_LOG_FILE", "boca_socios.log")

# Telegram es opcional: si las variables no están configuradas, el monitor
# continúa funcionando con las alertas locales.
TELEGRAM_BOT_TOKEN = os.getenv("BOCA_TELEGRAM_BOT_TOKEN", "").strip()
TELEGRAM_CHAT_ID = os.getenv("BOCA_TELEGRAM_CHAT_ID", "").strip()
TELEGRAM_TIMEOUT = _int_env("BOCA_TELEGRAM_TIMEOUT", 8)
