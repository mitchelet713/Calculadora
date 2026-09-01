"""Funciones matemáticas puras para distribución hipergeométrica multivariada."""

from __future__ import annotations

from fractions import Fraction
from math import comb
from typing import Dict, Iterable, Iterator, Mapping, Sequence, Tuple

from .models import Condicion, cumplen_todas


def combinaciones(n: int, k: int) -> int:
    """Calcula combinaciones(n, k); retorna cero cuando k no es factible."""
    if n < 0 or k < 0 or k > n:
        return 0
    return comb(n, k)


def probabilidad_vector(cantidades: Sequence[int], extracciones: Sequence[int]) -> Fraction:
    """Probabilidad exacta de un vector de conteos multivariado."""
    if len(cantidades) != len(extracciones):
        raise ValueError("Las cantidades y extracciones deben tener la misma longitud.")
    total_poblacion = sum(cantidades)
    total_muestra = sum(extracciones)
    denominador = combinaciones(total_poblacion, total_muestra)
    if denominador == 0:
        return Fraction(0, 1)
    numerador = 1
    for cantidad, extraccion in zip(cantidades, extracciones):
        numerador *= combinaciones(cantidad, extraccion)
        if numerador == 0:
            return Fraction(0, 1)
    return Fraction(numerador, denominador)


def _vectores_factibles(cantidades: Sequence[int], tamano_muestra: int) -> Iterator[Tuple[int, ...]]:
    """Genera vectores cuyo total es tamano_muestra respetando cada capacidad."""
    if not cantidades:
        if tamano_muestra == 0:
            yield tuple()
        return

    sufijos = [0] * (len(cantidades) + 1)
    for indice in range(len(cantidades) - 1, -1, -1):
        sufijos[indice] = sufijos[indice + 1] + cantidades[indice]

    def recorrer(indice: int, restante: int, actual: list[int]) -> Iterator[Tuple[int, ...]]:
        if indice == len(cantidades) - 1:
            if 0 <= restante <= cantidades[indice]:
                yield tuple(actual + [restante])
            return
        minimo = max(0, restante - sufijos[indice + 1])
        maximo = min(cantidades[indice], restante)
        for valor in range(minimo, maximo + 1):
            yield from recorrer(indice + 1, restante - valor, actual + [valor])

    if 0 <= tamano_muestra <= sum(cantidades):
        yield from recorrer(0, tamano_muestra, [])


def probabilidad_condiciones(
    cantidades_por_categoria: Mapping[str, int],
    tamano_muestra: int,
    condiciones: Iterable[Condicion],
) -> Fraction:
    """Suma exactamente los casos multivariados que cumplen todas las condiciones."""
    condiciones = tuple(condiciones)
    categorias = tuple(sorted(cantidades_por_categoria))
    cantidades = tuple(int(cantidades_por_categoria[categoria]) for categoria in categorias)
    total = sum(cantidades)
    denominador = combinaciones(total, tamano_muestra)
    if denominador == 0:
        return Fraction(0, 1)

    favorables = 0
    for vector in _vectores_factibles(cantidades, tamano_muestra):
        conteos: Dict[str, int] = dict(zip(categorias, vector))
        if cumplen_todas(conteos, condiciones):
            maneras = 1
            for cantidad, extraida in zip(cantidades, vector):
                maneras *= combinaciones(cantidad, extraida)
            favorables += maneras
    return Fraction(favorables, denominador)
