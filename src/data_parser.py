from .models import PopulationItem
class ParseError(ValueError): pass

def parse_population(text: str, quantities_first: bool=True) -> list[PopulationItem]:
    items=[]; seen={}
    for number, raw in enumerate(text.splitlines(), 1):
        line=raw.strip()
        if not line: continue
        if quantities_first:
            if " " not in line: raise ParseError(f"Línea {number}: usa 'Cantidad Nombre del elemento'.")
            qtext, name=line.split(" ", 1); name=name.strip()
            try: quantity=int(qtext)
            except ValueError as exc: raise ParseError(f"Línea {number}: cantidad no válida.") from exc
            if quantity <= 0 or not name: raise ParseError(f"Línea {number}: revisa cantidad y nombre.")
        else: quantity, name=1, line
        key=name.casefold()
        if key in seen:
            i=seen[key]; old=items[i]; items[i]=PopulationItem(old.name, old.quantity+quantity)
        else: seen[key]=len(items); items.append(PopulationItem(name, quantity))
    if not items: raise ParseError("No se encontraron líneas válidas.")
    return items

def decode_uploaded_file(uploaded_file) -> str:
    raw=uploaded_file.getvalue()
    for encoding in ("utf-8-sig","utf-8","latin-1"):
        try: return raw.decode(encoding)
        except UnicodeDecodeError: pass
    raise ParseError("No fue posible leer el archivo.")
