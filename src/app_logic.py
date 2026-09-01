"""Validaciones y orquestación independientes de Streamlit."""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from typing import Any, Iterable, Mapping, Optional, Sequence, Tuple

from .math_engine import probabilidad_condiciones
from .models import Condicion, Elemento, Operador, Poblacion
from .sim_engine import simular_frecuencia


@dataclass(frozen=True)
class ResultadoCalculo:
    probabilidad_exacta: Fraction
    exitos_simulados: int
    simulaciones: int
    frecuencia_empirica: float

    @property
    def probabilidad_decimal(self) -> float:
        return float(self.probabilidad_exacta)


def construir_poblacion(filas: Sequence[Mapping[str, Any]]) -> Poblacion:
    elementos = []
    for numero, fila in enumerate(filas, start=1):
        nombre = str(fila.get("Elemento", "")).strip()
        categoria = str(fila.get("Categoría", "")).strip()
        cantidad_bruta = fila.get("Cantidad", 0)
        fila_vacia = not nombre and not categoria and (cantidad_bruta in (None, "", 0, 0.0))
        if fila_vacia:
            continue
        try:
            cantidad_float = float(cantidad_bruta)
            cantidad = int(cantidad_float)
        except (TypeError, ValueError):
            raise ValueError(f"Fila {numero}: la cantidad debe ser un entero.") from None
        if cantidad != cantidad_float:
            raise ValueError(f"Fila {numero}: la cantidad debe ser un entero.")
        elementos.append(Elemento(nombre=nombre, cantidad=cantidad, categoria=categoria))
    return Poblacion.desde_iterable(elementos)


def construir_condiciones(filas: Sequence[Mapping[str, Any]]) -> Tuple[Condicion, ...]:
    condiciones = []
    for numero, fila in enumerate(filas, start=1):
        categoria = str(fila.get("Categoría", "")).strip()
        if not categoria:
            continue
        operador_texto = str(fila.get("Operador", "=")).strip()
        operador = Operador(operador_texto)
        valor = int(fila.get("Valor", 0))
        maximo_bruto = fila.get("Máximo")
        maximo = int(maximo_bruto) if operador == Operador.RANGO and maximo_bruto is not None else None
        condiciones.append(Condicion(categoria, operador, valor, maximo))
    return tuple(condiciones)


def validar_configuracion(poblacion: Poblacion, tamano_muestra: int, condiciones: Iterable[Condicion]) -> None:
    condiciones = tuple(condiciones)
    if poblacion.total <= 0:
        raise ValueError("La población debe contener al menos una unidad.")
    if tamano_muestra < 0 or tamano_muestra > poblacion.total:
        raise ValueError("El tamaño de muestra debe estar entre cero y el total de la población.")
    if not condiciones:
        raise ValueError("Debe definir al menos una condición.")
    categorias = set(poblacion.categorias)
    desconocidas = sorted({c.categoria for c in condiciones} - categorias)
    if desconocidas:
        raise ValueError("Hay condiciones con categorías inexistentes: " + ", ".join(desconocidas))


def ejecutar_calculo(
    poblacion: Poblacion,
    tamano_muestra: int,
    condiciones: Iterable[Condicion],
    simulaciones: int,
    semilla: Optional[int] = None,
) -> ResultadoCalculo:
    condiciones = tuple(condiciones)
    validar_configuracion(poblacion, tamano_muestra, condiciones)
    exacta = probabilidad_condiciones(poblacion.cantidades_por_categoria(), tamano_muestra, condiciones)
    exitos, total, empirica = simular_frecuencia(
        poblacion, tamano_muestra, condiciones, simulaciones, semilla
    )
    return ResultadoCalculo(exacta, exitos, total, empirica)
