from .models import PopulationItem


class ParseError(ValueError):
    """Error de formato con ubicación precisa en el texto importado."""


def parse_population(text: str, quantities_first: bool = True) -> list[PopulationItem]:
    items: list[PopulationItem] = []
    seen: dict[str, int] = {}

    for line_number, raw_line in enumerate(text.splitlines(), start=1):
        line = raw_line.strip()
        if not line:
            continue

        if quantities_first:
            if " " not in line:
                raise ParseError(
                    f"Línea {line_number}: usa el formato 'Cantidad Nombre del elemento'."
                )
            quantity_text, name = line.split(" ", 1)
            name = name.strip()
            try:
                quantity = int(quantity_text)
            except ValueError as exc:
                raise ParseError(
                    f"Línea {line_number}: '{quantity_text}' no es una cantidad entera válida."
                ) from exc
            if quantity <= 0:
                raise ParseError(f"Línea {line_number}: la cantidad debe ser mayor que cero.")
            if not name:
                raise ParseError(f"Línea {line_number}: falta el nombre del elemento.")
        else:
            quantity, name = 1, line

        key = name.casefold()
        if key in seen:
            index = seen[key]
            previous = items[index]
            items[index] = PopulationItem(previous.name, previous.quantity + quantity)
        else:
            seen[key] = len(items)
            items.append(PopulationItem(name=name, quantity=quantity))

    if not items:
        raise ParseError("No se encontraron líneas válidas para crear la población.")
    return items


def decode_uploaded_file(uploaded_file) -> str:
    raw = uploaded_file.getvalue()
    for encoding in ("utf-8-sig", "utf-8", "latin-1"):
        try:
            return raw.decode(encoding)
        except UnicodeDecodeError:
            continue
    raise ParseError("No fue posible leer el archivo. Utiliza un archivo TXT en UTF-8.")
