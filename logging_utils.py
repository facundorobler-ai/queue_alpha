"""Configuración de registro en consola y archivo."""
import logging

_logger = logging.getLogger("boca_socios")
_logger.setLevel(logging.INFO)
_logger.propagate = False


def configurar_logging(archivo: str) -> None:
    # Evitar agregar handlers duplicados si se vuelve a llamar en una prueba.
    if _logger.handlers:
        for handler in list(_logger.handlers):
            _logger.removeHandler(handler)
            handler.close()

    handler = logging.FileHandler(archivo, encoding="utf-8")
    handler.setFormatter(
        logging.Formatter("%(asctime)s | %(message)s", datefmt="%H:%M:%S")
    )
    _logger.addHandler(handler)


def log(mensaje: str) -> None:
    print(mensaje, flush=True)
    try:
        _logger.info(mensaje)
    except Exception:
        # El registro a archivo no debe detener el monitor.
        pass
