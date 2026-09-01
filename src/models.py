"""Modelos de datos para poblaciones finitas y condiciones."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Iterable, List, Mapping, Optional, Tuple


class Operador(str, Enum):
    IGUAL = "="
    MAYOR_IGUAL = ">="
    MENOR_IGUAL = "<="
    RANGO = "RANGO"


@dataclass(frozen=True)
class Categoria:
    nombre: str

    def __post_init__(self) -> None:
        if not self.nombre.strip():
            raise ValueError("El nombre de la categoría no puede estar vacío.")


@dataclass(frozen=True)
class Elemento:
    nombre: str
    cantidad: int
    categoria: str

    def __post_init__(self) -> None:
        if not self.nombre.strip():
            raise ValueError("El nombre del elemento no puede estar vacío.")
        if not self.categoria.strip():
            raise ValueError("La categoría no puede estar vacía.")
        if isinstance(self.cantidad, bool) or not isinstance(self.cantidad, int) or self.cantidad < 0:
            raise ValueError("La cantidad debe ser un entero mayor o igual que cero.")


@dataclass(frozen=True)
class Poblacion:
    elementos: Tuple[Elemento, ...] = field(default_factory=tuple)

    @classmethod
    def desde_iterable(cls, elementos: Iterable[Elemento]) -> "Poblacion":
        return cls(tuple(elementos))

    @property
    def total(self) -> int:
        return sum(elemento.cantidad for elemento in self.elementos)

    @property
    def elementos_unicos(self) -> int:
        return sum(1 for elemento in self.elementos if elemento.cantidad > 0)

    @property
    def categorias(self) -> Tuple[str, ...]:
        return tuple(sorted({elemento.categoria for elemento in self.elementos if elemento.cantidad > 0}))

    def cantidades_por_categoria(self) -> Dict[str, int]:
        resultado: Dict[str, int] = {}
        for elemento in self.elementos:
            resultado[elemento.categoria] = resultado.get(elemento.categoria, 0) + elemento.cantidad
        return resultado


@dataclass(frozen=True)
class Condicion:
    categoria: str
    operador: Operador
    valor: int
    valor_maximo: Optional[int] = None

    def __post_init__(self) -> None:
        if not self.categoria.strip():
            raise ValueError("La categoría de la condición no puede estar vacía.")
        if isinstance(self.valor, bool) or not isinstance(self.valor, int) or self.valor < 0:
            raise ValueError("El valor debe ser un entero mayor o igual que cero.")
        if self.operador == Operador.RANGO:
            if self.valor_maximo is None or isinstance(self.valor_maximo, bool) or not isinstance(self.valor_maximo, int):
                raise ValueError("Una condición de rango requiere un máximo entero.")
            if self.valor_maximo < self.valor:
                raise ValueError("El máximo del rango no puede ser menor que el mínimo.")

    def cumple(self, cantidad_observada: int) -> bool:
        if self.operador == Operador.IGUAL:
            return cantidad_observada == self.valor
        if self.operador == Operador.MAYOR_IGUAL:
            return cantidad_observada >= self.valor
        if self.operador == Operador.MENOR_IGUAL:
            return cantidad_observada <= self.valor
        if self.operador == Operador.RANGO:
            return self.valor <= cantidad_observada <= int(self.valor_maximo)
        raise ValueError(f"Operador no soportado: {self.operador}")


def cumplen_todas(conteos: Mapping[str, int], condiciones: Iterable[Condicion]) -> bool:
    """Aplica AND lógico entre todas las condiciones."""
    return all(condicion.cumple(int(conteos.get(condicion.categoria, 0))) for condicion in condiciones)
