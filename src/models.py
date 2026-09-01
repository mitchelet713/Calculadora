from dataclasses import dataclass, field

@dataclass(frozen=True)
class PopulationItem:
    name: str
    quantity: int
    category: str = "Sin clasificar"
    def __post_init__(self):
        if not self.name.strip(): raise ValueError("El nombre no puede estar vacío.")
        if self.quantity <= 0: raise ValueError("La cantidad debe ser mayor que cero.")

@dataclass(frozen=True)
class Condition:
    category: str
    minimum: int
    maximum: int
    def __post_init__(self):
        if self.minimum < 0: raise ValueError("El mínimo no puede ser negativo.")
        if self.maximum < self.minimum: raise ValueError("El máximo no puede ser menor que el mínimo.")

@dataclass
class AnalysisResult:
    exact_probability: float
    empirical_frequency: float
    successes: int
    simulation_count: int
    detailed_samples: list[dict] = field(default_factory=list)
