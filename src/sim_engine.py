"""Funciones puras para simulaciones de extracción sin reemplazo."""

from __future__ import annotations

import random
from typing import Iterable, List, Mapping, Optional, Sequence, Tuple

from .models import Condicion, Poblacion, cumplen_todas


def expandir_poblacion(poblacion: Poblacion) -> Tuple[str, ...]:
    """Expande cada unidad en memoria usando su categoría como etiqueta."""
    return tuple(
        elemento.categoria
        for elemento in poblacion.elementos
        for _ in range(elemento.cantidad)
    )


def extraer_sin_reemplazo(
    poblacion_expandida: Sequence[str],
    tamano_muestra: int,
    generador: random.Random,
) -> List[str]:
    if tamano_muestra < 0 or tamano_muestra > len(poblacion_expandida):
        raise ValueError("El tamaño de muestra no es válido para la población.")
    return generador.sample(poblacion_expandida, tamano_muestra)


def contar_categorias(muestra: Iterable[str]) -> Mapping[str, int]:
    conteos: dict[str, int] = {}
    for categoria in muestra:
        conteos[categoria] = conteos.get(categoria, 0) + 1
    return conteos


def simular_frecuencia(
    poblacion: Poblacion,
    tamano_muestra: int,
    condiciones: Iterable[Condicion],
    simulaciones: int,
    semilla: Optional[int] = None,
) -> Tuple[int, int, float]:
    """Retorna éxitos, simulaciones y frecuencia empírica."""
    if simulaciones <= 0:
        raise ValueError("La cantidad de simulaciones debe ser mayor que cero.")
    expandida = expandir_poblacion(poblacion)
    generador = random.Random(semilla)
    condiciones = tuple(condiciones)
    exitos = 0
    for _ in range(simulaciones):
        muestra = extraer_sin_reemplazo(expandida, tamano_muestra, generador)
        if cumplen_todas(contar_categorias(muestra), condiciones):
            exitos += 1
    return exitos, simulaciones, exitos / simulaciones
