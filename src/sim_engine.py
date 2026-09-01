import random
from .models import Condition, PopulationItem

def run_simulations(items, sample_size, conditions, simulations, details_to_show, seed=None):
    population=[(i.name,i.category) for i in items for _ in range(i.quantity)]
    rng=random.Random(seed); successes=0; details=[]
    for n in range(1,simulations+1):
        sample=rng.sample(population,sample_size); counts={}
        for _,cat in sample: counts[cat]=counts.get(cat,0)+1
        success=all(c.minimum <= counts.get(c.category,0) <= c.maximum for c in conditions)
        successes += int(success)
        if n <= details_to_show:
            details.append({"Muestra":n,"Elementos obtenidos":", ".join(x[0] for x in sample),"Éxito":"Sí" if success else "No"})
    return successes/simulations, successes, details
