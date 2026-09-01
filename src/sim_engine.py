import random
from .models import Condition, PopulationItem


def _expanded_population(items: list[PopulationItem]) -> list[tuple[str, str]]:
    return [
        (item.name, item.category)
        for item in items
        for _ in range(item.quantity)
    ]


def run_simulations(
    items: list[PopulationItem],
    sample_size: int,
    conditions: list[Condition],
    simulations: int,
    details_to_show: int,
    seed: int | None = None,
) -> tuple[float, int, list[dict]]:
    population = _expanded_population(items)
    if sample_size > len(population):
        raise ValueError("La muestra no puede superar la población.")
    if simulations <= 0:
        raise ValueError("El número de simulaciones debe ser mayor que cero.")

    rng = random.Random(seed)
    successes = 0
    details: list[dict] = []

    for simulation_number in range(1, simulations + 1):
        sample = rng.sample(population, sample_size)
        category_counts: dict[str, int] = {}
        for _, category in sample:
            category_counts[category] = category_counts.get(category, 0) + 1
        success = all(
            category_counts.get(condition.category, 0) >= condition.minimum
            for condition in conditions
        )
        successes += int(success)

        if simulation_number <= details_to_show:
            details.append(
                {
                    "Muestra": simulation_number,
                    "Elementos obtenidos": ", ".join(name for name, _ in sample),
                    "Éxito": "Sí" if success else "No",
                }
            )

    return successes / simulations, successes, details
