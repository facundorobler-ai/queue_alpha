"""Estado compartido entre los hilos del programa."""
from collections import deque
from dataclasses import dataclass, field
import threading
from typing import Any


@dataclass
class AppState:
    drivers: list[tuple[Any, str]] = field(default_factory=list)
    stop_event: threading.Event = field(default_factory=threading.Event)
    tiempos: dict[str, int] = field(default_factory=dict)
    estados: dict[str, str] = field(default_factory=dict)
    queue_ids: dict[str, str] = field(default_factory=dict)
    historial: dict[str, deque] = field(default_factory=dict)
    ya_alerto: set[str] = field(default_factory=set)
    ya_aviso_tendencia: set[str] = field(default_factory=set)
    vio_cola: set[str] = field(default_factory=set)
    lock: threading.Lock = field(default_factory=threading.Lock)
