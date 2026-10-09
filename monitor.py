"""Hilos de monitorización de páginas y presentación del ranking."""
import time
import threading

from selenium.webdriver.common.by import By

from config import INTERVALO_DETECCION, INTERVALO_RANKING, MAS_DE_UNA_HORA, MINUTOS_ALERTA
from logging_utils import log
from login import completar_login
from notifications import alerta_entrando, alertar
from queue_logic import (
    actualizar_historial,
    avisar_si_tendencia_rapida,
    extraer_queue_id,
    parsear_estado,
)
from state import AppState


def detectar_cola(driver, nombre: str, state: AppState) -> None:
    while not state.stop_event.is_set():
        try:
            time.sleep(INTERVALO_DETECCION)
            if state.stop_event.is_set():
                break

            texto = driver.find_element(By.TAG_NAME, "body").text.lower()
            qid = extraer_queue_id(texto)

            if qid:
                with state.lock:
                    state.vio_cola.add(nombre)
                    nuevo_id = state.queue_ids.get(nombre) != qid
                    state.queue_ids[nombre] = qid
                if nuevo_id:
                    log(f"🔑 {nombre} → Queue ID: {qid}")

            estado, minutos = parsear_estado(texto)
            if estado in ("mas_hora", "menos_1", "minutos", "en_cola"):
                with state.lock:
                    state.vio_cola.add(nombre)

            with state.lock:
                state.estados[nombre] = estado

            if estado == "entrando":
                with state.lock:
                    state.tiempos.pop(nombre, None)
                    paso_por_cola = nombre in state.vio_cola

                if paso_por_cola:
                    log(f"🟢 {nombre}: se detectó salida de la fila virtual.")
                    alerta_entrando(nombre)
                    completar_login(driver, nombre)
                else:
                    log(
                        f"⚪ {nombre}: se detectó una página de ingreso inicial; "
                        "no hay evidencia de que haya pasado por la fila."
                    )
                break

            if estado == "mas_hora":
                with state.lock:
                    state.tiempos[nombre] = MAS_DE_UNA_HORA
                log(f"⏰ {nombre}: más de una hora de espera")
            elif estado == "menos_1":
                with state.lock:
                    state.tiempos[nombre] = 0
                log(f"🚀 {nombre}: menos de 1 min")
                alertar(state, nombre, 0)
            elif estado == "minutos":
                with state.lock:
                    state.tiempos[nombre] = minutos
                actualizar_historial(state, nombre, minutos)
                log(f"⏳ {nombre}: {minutos} min")
                if minutos <= MINUTOS_ALERTA:
                    alertar(state, nombre, minutos)
                else:
                    avisar_si_tendencia_rapida(state, nombre, minutos)
            elif estado == "en_cola":
                log(f"🕐 {nombre}: en cola (esperando número...)")
            else:
                log(f"⚪ {nombre}: esperando apertura de venta...")

        except Exception as exc:
            if not state.stop_event.is_set():
                log(f"[ERROR] {nombre}: {exc}")
            with state.lock:
                state.tiempos.pop(nombre, None)
            break


def formatear_minutos(nombre: str, minutos: int, snapshot_estados: dict) -> str:
    estado = snapshot_estados.get(nombre)
    if estado == "mas_hora":
        return "+60"
    if estado == "menos_1":
        return "<1"
    return str(minutos)


def mostrar_ranking(state: AppState) -> None:
    while not state.stop_event.is_set():
        time.sleep(INTERVALO_RANKING)
        with state.lock:
            snapshot_tiempos = dict(state.tiempos)
            snapshot_ids = dict(state.queue_ids)
            snapshot_estados = dict(state.estados)

        if snapshot_tiempos:
            ordenados = sorted(snapshot_tiempos.items(), key=lambda item: item[1])
            log("\n📊 RANKING GLOBAL:")
            log(f"  {'#':<4} {'Browser':<16} {'Minutos':<10} {'Queue ID'}")
            log(f"  {'-' * 55}")
            for i, (nombre, tiempo) in enumerate(ordenados):
                qid = snapshot_ids.get(nombre, "sin ID")
                qid_corto = qid[:8] + "..." if len(qid) > 8 else qid
                minutos_fmt = formatear_minutos(nombre, tiempo, snapshot_estados)
                estrella = " ⭐" if i == 0 else ""
                log(f"  {i + 1:<4} {nombre:<16} {minutos_fmt:<10} {qid_corto}{estrella}")

            mejor = ordenados[0]
            mejor_fmt = formatear_minutos(mejor[0], mejor[1], snapshot_estados)
            log(f"\n  👉 MENOR TIEMPO ESTIMADO: {mejor[0]} — {mejor_fmt} min restantes\n")
        elif snapshot_ids and not snapshot_tiempos:
            log(f"\n  ⏳ {len(snapshot_ids)} navegador(es) con ID de fila; esperando tiempo estimado...\n")
