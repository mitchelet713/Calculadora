"""Funciones puras para simulación de extracciones sin reemplazo."""
from __future__ import annotations
import random
from typing import Iterable, Mapping, Optional, Sequence, Tuple
from .models import Condicion, Poblacion, cumplen_todas

def expandir_poblacion(poblacion: Poblacion) -> Tuple[str, ...]:
    return tuple(e.categoria for e in poblacion.elementos for _ in range(e.cantidad))
def extraer_sin_reemplazo(poblacion: Sequence[str], muestra: int,
                          generador: random.Random) -> list[str]:
    if muestra < 0 or muestra > len(poblacion):
        raise ValueError("El tamaño de muestra no es válido para la población.")
    return generador.sample(poblacion, muestra)
def contar_categorias(muestra: Iterable[str]) -> Mapping[str, int]:
    conteos: dict[str, int] = {}
    for categoria in muestra:
        conteos[categoria] = conteos.get(categoria, 0) + 1
    return conteos
def simular_frecuencia(poblacion: Poblacion, muestra: int, condiciones: Iterable[Condicion],
                       simulaciones: int, semilla: Optional[int] = None) -> Tuple[int, int, float]:
    if simulaciones <= 0:
        raise ValueError("La cantidad de simulaciones debe ser mayor que cero.")
    expandida = expandir_poblacion(poblacion)
    generador = random.Random(semilla)
    condiciones = tuple(condiciones)
    exitos = 0
    for _ in range(simulaciones):
        extraida = extraer_sin_reemplazo(expandida, muestra, generador)
        exitos += int(cumplen_todas(contar_categorias(extraida), condiciones))
    return exitos, simulaciones, exitos / simulaciones
