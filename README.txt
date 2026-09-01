SIMULADOR PROBABILÍSTICO AVANZADO V2.2

Instalación:
pip install -r requirements.txt

Ejecución:
streamlit run app.py

Corrección V2.2:
- Eliminado el uso de una expresión condicional en una sola línea dentro de st.expander.
- La tabla detallada se renderiza mediante un bloque if/else explícito.
- Los botones Atrás y Reiniciar todo permanecen fuera del bloque de resultados.
- Se conserva el intervalo mínimo/máximo por categoría.
