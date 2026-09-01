from math import comb
from .models import Condition, PopulationItem


def _category_totals(items: list[PopulationItem]) -> dict[str, int]:
    totals: dict[str, int] = {}
    for item in items:
        totals[item.category] = totals.get(item.category, 0) + item.quantity
    return totals


def exact_probability(
    items: list[PopulationItem], sample_size: int, conditions: list[Condition]
) -> float:
    """Probabilidad hipergeométrica multivariante para mínimos unidos por AND."""
    population_size = sum(item.quantity for item in items)
    if sample_size < 0 or sample_size > population_size:
        raise ValueError("El tamaño de muestra debe estar entre 0 y el total poblacional.")

    required: dict[str, int] = {}
    for condition in conditions:
        required[condition.category] = max(required.get(condition.category, 0), condition.minimum)

    totals = _category_totals(items)
    selected_categories = list(required)
    if any(required[c] > totals.get(c, 0) for c in selected_categories):
        return 0.0

    other_total = population_size - sum(totals.get(c, 0) for c in selected_categories)
    denominator = comb(population_size, sample_size)
    if denominator == 0:
        return 0.0

    favorable = 0

    def walk(index: int, chosen: int, ways: int) -> None:
        nonlocal favorable
        if index == len(selected_categories):
            remaining = sample_size - chosen
            if 0 <= remaining <= other_total:
                favorable += ways * comb(other_total, remaining)
            return

        category = selected_categories[index]
        available = totals.get(category, 0)
        minimum = required[category]
        maximum = min(available, sample_size - chosen)
        for amount in range(minimum, maximum + 1):
            walk(index + 1, chosen + amount, ways * comb(available, amount))

    walk(0, 0, 1)
    return favorable / denominator
