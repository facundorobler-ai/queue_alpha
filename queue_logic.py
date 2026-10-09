"""Funciones puras y utilidades para interpretar el texto de una fila virtual."""
from collections import deque
import re
import time

from config import HISTORIAL_MAX, MAS_DE_UNA_HORA, MINUTOS_ALERTA, INTERVALO_DETECCION
from state import AppState
from logging_utils import log


def extraer_queue_id(texto: str):
    """Extrae un identificador con formato UUID si aparece en el texto."""
    match = re.search(r'identificador de fila[:\s]+([a-f0-9\-]{36})', texto, re.I)
    if match:
        return match.group(1)
    match = re.search(
        r'([a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})',
        texto,
        re.I,
    )
    return match.group(1) if match else None


def parsear_estado(texto: str):
    """Devuelve (estado, minutos) a partir del texto visible de la página."""
    texto = texto.lower()

    # Mantiene los marcadores del programa original; la validación visual
    # sigue siendo importante porque una palabra aislada puede dar falsos positivos.
    if any(frase in texto for frase in [
        "ya podés", "ya podes", "ingresá", "ingresa ahora",
        "bienvenido", "comprar entradas", "iniciar sesión", "iniciar sesion"
    ]):
        return "entrando", None

    if re.search(r'm[aá]s de (?:una|1) hora', texto):
        return "mas_hora", MAS_DE_UNA_HORA

    if re.search(r'menos de \d+ minuto', texto):
        return "menos_1", 0

    match = re.search(r'tiempo de espera[^\d]{0,40}(\d+)\s*(?:minutos?|min\b)', texto)
    if not match:
        match = re.search(r'(\d+)\s*(?:minutos?|min\b)', texto)
    if match:
        return "minutos", int(match.group(1))

    if "entrarás dentro de" in texto or "entras dentro de" in texto:
        return "en_cola", None

    return "esperando_venta", None


def actualizar_historial(state: AppState, nombre: str, minutos: int) -> None:
    with state.lock:
        if nombre not in state.historial:
            state.historial[nombre] = deque(maxlen=HISTORIAL_MAX)
        state.historial[nombre].append((time.time(), minutos))


def estimar_tendencia(state: AppState, nombre: str):
    """Estima minutos de espera que bajan por segundo real."""
    with state.lock:
        datos = list(state.historial.get(nombre, []))
    if len(datos) < 2:
        return None
    (t0, m0), (t1, m1) = datos[0], datos[-1]
    dt = t1 - t0
    if dt <= 0:
        return None
    return (m0 - m1) / dt


def avisar_si_tendencia_rapida(state: AppState, nombre: str, minutos_actual: int) -> None:
    tasa = estimar_tendencia(state, nombre)
    if not tasa or tasa <= 0:
        return

    segundos_para_alerta = (minutos_actual - MINUTOS_ALERTA) * 60 / tasa
    if segundos_para_alerta <= INTERVALO_DETECCION * 1.5:
        with state.lock:
            if nombre in state.ya_aviso_tendencia:
                return
            state.ya_aviso_tendencia.add(nombre)
        log(
            f"📉 {nombre}: el tiempo estimado está bajando rápido "
            f"(~{tasa * 60:.1f} min por minuto real)."
        )
