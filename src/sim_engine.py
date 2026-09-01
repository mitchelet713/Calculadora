import random

def run_simulations(items,sample_size,conditions,simulations,details_to_show,seed=None):
    population=[(i.name,i.category) for i in items for _ in range(i.quantity)]
    if sample_size > len(population): raise ValueError("La muestra no puede superar la población.")
    rng=random.Random(seed); successes=0; details=[]
    for number in range(1,simulations+1):
        sample=rng.sample(population,sample_size); counts={}
        for _,category in sample: counts[category]=counts.get(category,0)+1
        success=all(c.minimum <= counts.get(c.category,0) <= c.maximum for c in conditions)
        successes += int(success)
        if number <= details_to_show:
            details.append({"Muestra":number,"Elementos obtenidos":", ".join(name for name,_ in sample),"Éxito":"Sí" if success else "No"})
    return successes/simulations,successes,details
