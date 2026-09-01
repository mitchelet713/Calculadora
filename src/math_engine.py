"""Funciones puras para combinatoria e hipergeométrica multivariada."""
from __future__ import annotations
from fractions import Fraction
from math import comb
from typing import Dict, Iterable, Iterator, Mapping, Sequence, Tuple
from .models import Condicion, cumplen_todas

def combinaciones(n: int, k: int) -> int:
    if n < 0 or k < 0 or k > n:
        return 0
    return comb(n, k)

def probabilidad_vector(cantidades: Sequence[int], extracciones: Sequence[int]) -> Fraction:
    if len(cantidades) != len(extracciones):
        raise ValueError("Las cantidades y extracciones deben tener la misma longitud.")
    denominador = combinaciones(sum(cantidades), sum(extracciones))
    if denominador == 0:
        return Fraction(0, 1)
    numerador = 1
    for cantidad, extraccion in zip(cantidades, extracciones):
        numerador *= combinaciones(cantidad, extraccion)
    return Fraction(numerador, denominador)

def _vectores_factibles(cantidades: Sequence[int], muestra: int) -> Iterator[Tuple[int, ...]]:
    if not cantidades:
        if muestra == 0:
            yield tuple()
        return
    sufijos = [0] * (len(cantidades) + 1)
    for i in range(len(cantidades) - 1, -1, -1):
        sufijos[i] = sufijos[i + 1] + cantidades[i]
    def recorrer(i: int, restante: int, actual: list[int]) -> Iterator[Tuple[int, ...]]:
        if i == len(cantidades) - 1:
            if 0 <= restante <= cantidades[i]:
                yield tuple(actual + [restante])
            return
        minimo = max(0, restante - sufijos[i + 1])
        maximo = min(cantidades[i], restante)
        for valor in range(minimo, maximo + 1):
            yield from recorrer(i + 1, restante - valor, actual + [valor])
    if 0 <= muestra <= sum(cantidades):
        yield from recorrer(0, muestra, [])

def probabilidad_condiciones(cantidades_por_categoria: Mapping[str, int], muestra: int,
                             condiciones: Iterable[Condicion]) -> Fraction:
    condiciones = tuple(condiciones)
    categorias = tuple(sorted(cantidades_por_categoria))
    cantidades = tuple(int(cantidades_por_categoria[c]) for c in categorias)
    denominador = combinaciones(sum(cantidades), muestra)
    if denominador == 0:
        return Fraction(0, 1)
    favorables = 0
    for vector in _vectores_factibles(cantidades, muestra):
        conteos: Dict[str, int] = dict(zip(categorias, vector))
        if cumplen_todas(conteos, condiciones):
            maneras = 1
            for cantidad, extraida in zip(cantidades, vector):
                maneras *= combinaciones(cantidad, extraida)
            favorables += maneras
    return Fraction(favorables, denominador)
