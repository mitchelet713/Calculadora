from math import comb

def exact_probability(items, sample_size, conditions):
    population_size=sum(i.quantity for i in items)
    if not 0 <= sample_size <= population_size: raise ValueError("Tamaño de muestra no válido.")
    totals={}
    for item in items: totals[item.category]=totals.get(item.category,0)+item.quantity
    if len({c.category for c in conditions}) != len(conditions):
        raise ValueError("Cada condición debe usar una categoría diferente.")
    if any(c.minimum > totals.get(c.category,0) for c in conditions): return 0.0
    other_total=population_size-sum(totals.get(c.category,0) for c in conditions)
    denominator=comb(population_size,sample_size); favorable=0
    def visit(index,chosen,ways):
        nonlocal favorable
        if index == len(conditions):
            rest=sample_size-chosen
            if 0 <= rest <= other_total: favorable += ways*comb(other_total,rest)
            return
        c=conditions[index]; available=totals.get(c.category,0)
        upper=min(c.maximum,available,sample_size-chosen)
        for amount in range(c.minimum,upper+1):
            visit(index+1,chosen+amount,ways*comb(available,amount))
    visit(0,0,1)
    return favorable/denominator if denominator else 0.0
