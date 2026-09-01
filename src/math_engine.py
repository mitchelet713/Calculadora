from math import comb
from .models import Condition, PopulationItem

def exact_probability(items:list[PopulationItem], sample_size:int, conditions:list[Condition]) -> float:
    population_size=sum(i.quantity for i in items)
    if not 0 <= sample_size <= population_size: raise ValueError("Tamaño de muestra no válido.")
    totals={}
    for item in items: totals[item.category]=totals.get(item.category,0)+item.quantity
    selected=[c.category for c in conditions]
    if len(set(selected)) != len(selected): raise ValueError("Las categorías de las condiciones no pueden repetirse.")
    if any(c.minimum > totals.get(c.category,0) for c in conditions): return 0.0
    other_total=population_size-sum(totals.get(c.category,0) for c in conditions)
    favorable=0; denominator=comb(population_size,sample_size)
    def walk(index, chosen, ways):
        nonlocal favorable
        if index == len(conditions):
            remaining=sample_size-chosen
            if 0 <= remaining <= other_total: favorable += ways*comb(other_total,remaining)
            return
        c=conditions[index]; available=totals.get(c.category,0)
        upper=min(c.maximum, available, sample_size-chosen)
        for amount in range(c.minimum, upper+1):
            walk(index+1, chosen+amount, ways*comb(available,amount))
    walk(0,0,1)
    return favorable/denominator if denominator else 0.0
