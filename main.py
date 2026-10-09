"""Punto de entrada del proyecto Boca Socios Monitor."""
import tls_setup  # Debe cargarse antes de Selenium y de los módulos de red.

import os
import threading
import time

from browsers import abrir_chrome, abrir_chrome_incognito, abrir_edge
from config import CANTIDAD_POR_TIPO, DELAY, LOG_FILE, MINUTOS_ALERTA
from logging_utils import configurar_logging, log
from monitor import detectar_cola, mostrar_ranking
from notifications import telegram_configurado
from state import AppState


def iniciar() -> None:
    configurar_logging(LOG_FILE)
    state = AppState()

    log("\n" + "=" * 50)
    log("  BOCA SOCIOS — Monitor de estado de página")
    log("=" * 50 + "\n")
    log(
        "Aviso: respetá las condiciones del sitio y evitá abrir sesiones "
        "simultáneas para intentar alterar el orden de la fila."
    )

    # Se mantiene la configuración del programa previo para que pueda
    # ajustarse desde el entorno. Para una prueba inicial, configurá
    # BOCA_CANTIDAD_POR_TIPO=1 y comprobá primero con una instancia por tipo
    # (Chrome normal, incógnito y Edge: tres navegadores en total).
    fabricas = [abrir_chrome, abrir_chrome_incognito, abrir_edge]

    try:
        for fabrica in fabricas:
            for index in range(CANTIDAD_POR_TIPO):
                if state.stop_event.is_set():
                    break
                try:
                    driver, nombre = fabrica(index)
                    state.drivers.append((driver, nombre))
                    hilo = threading.Thread(
                        target=detectar_cola,
                        args=(driver, nombre, state),
                        daemon=True,
                        name=f"monitor-{nombre}",
                    )
                    hilo.start()
                    time.sleep(DELAY)
                except Exception as exc:
                    log(f"[ERROR] No se pudo abrir {fabrica.__name__}-{index}: {exc}")

        ranking_thread = threading.Thread(
            target=mostrar_ranking,
            args=(state,),
            daemon=True,
            name="ranking",
        )
        ranking_thread.start()

        log(f"\nSistema activo — {len(state.drivers)} navegador(es) abiertos.")
        log(f"Alerta local cuando queden {MINUTOS_ALERTA} minuto(s) o menos.")
        log("Telegram: activado." if telegram_configurado() else "Telegram: no configurado; solo habrá alertas locales.")
        log(f"Registro: {os.path.abspath(LOG_FILE)}\n")
        input("Presioná ENTER para cerrar el programa...\n")
    except (KeyboardInterrupt, EOFError):
        log("\nCierre solicitado.")
    finally:
        state.stop_event.set()
        for driver, nombre in state.drivers:
            try:
                driver.quit()
            except Exception as exc:
                log(f"[AVISO] No se pudo cerrar {nombre}: {exc}")
        log("\nPrograma cerrado.\n")


if __name__ == "__main__":
    iniciar()
