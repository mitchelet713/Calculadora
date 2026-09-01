"""Parseo, validaciones y orquestación de resultados."""
from __future__ import annotations
import re
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

def separar_valores(texto: str) -> Tuple[str, ...]:
    """Separa líneas, comas o punto y coma; elimina vacíos y duplicados conservando orden."""
    candidatos = re.split(r"[\n,;]+", texto)
    vistos: set[str] = set()
    resultado = []
    for candidato in candidatos:
        valor = candidato.strip()
        clave = valor.casefold()
        if valor and clave not in vistos:
            vistos.add(clave)
            resultado.append(valor)
    return tuple(resultado)

def construir_poblacion(filas: Sequence[Mapping[str, Any]]) -> Poblacion:
    elementos = []
    for numero, fila in enumerate(filas, start=1):
        nombre = str(fila.get("Elemento", "")).strip()
        categoria = str(fila.get("Categoría", "")).strip()
        try:
            numero_float = float(fila.get("Cantidad", 0))
            cantidad = int(numero_float)
        except (TypeError, ValueError):
            raise ValueError(f"Fila {numero}: la cantidad debe ser un entero.") from None
        if cantidad != numero_float:
            raise ValueError(f"Fila {numero}: la cantidad debe ser un entero.")
        elementos.append(Elemento(nombre, cantidad, categoria))
    if not elementos:
        raise ValueError("Debe existir al menos un elemento.")
    return Poblacion.desde_iterable(elementos)

def construir_condiciones(filas: Sequence[Mapping[str, Any]]) -> Tuple[Condicion, ...]:
    condiciones = []
    for numero, fila in enumerate(filas, start=1):
        categoria = str(fila.get("Categoría", "")).strip()
        if not categoria:
            continue
        try:
            operador = Operador(str(fila.get("Operador", "=")).strip())
            valor = int(float(fila.get("Valor", 0)))
            maximo_bruto = fila.get("Máximo")
            maximo = int(float(maximo_bruto)) if operador == Operador.RANGO and maximo_bruto not in (None, "") else None
        except (ValueError, TypeError):
            raise ValueError(f"Condición {numero}: revise operador y cantidades.") from None
        condiciones.append(Condicion(categoria, operador, valor, maximo))
    return tuple(condiciones)

def validar_configuracion(poblacion: Poblacion, muestra: int, condiciones: Iterable[Condicion]) -> None:
    condiciones = tuple(condiciones)
    if poblacion.total <= 0:
        raise ValueError("La población total debe ser mayor que cero.")
    if not 0 <= muestra <= poblacion.total:
        raise ValueError("El tamaño de muestra debe estar entre cero y el total de la población.")
    if not condiciones:
        raise ValueError("Debe definir al menos una condición.")
    desconocidas = sorted({c.categoria for c in condiciones} - set(poblacion.categorias))
    if desconocidas:
        raise ValueError("Categorías inexistentes en las condiciones: " + ", ".join(desconocidas))

def ejecutar_calculo(poblacion: Poblacion, muestra: int, condiciones: Iterable[Condicion],
                     simulaciones: int, semilla: Optional[int] = None) -> ResultadoCalculo:
    condiciones = tuple(condiciones)
    validar_configuracion(poblacion, muestra, condiciones)
    exacta = probabilidad_condiciones(poblacion.cantidades_por_categoria(), muestra, condiciones)
    exitos, total, empirica = simular_frecuencia(poblacion, muestra, condiciones, simulaciones, semilla)
    return ResultadoCalculo(exacta, exitos, total, empirica)
