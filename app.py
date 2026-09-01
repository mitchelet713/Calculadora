"""Punto de entrada de la aplicación Streamlit."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from src.app_logic import construir_condiciones, construir_poblacion, ejecutar_calculo


st.set_page_config(page_title="Probabilidad en poblaciones finitas", page_icon="📊", layout="wide")

DATOS_INICIALES = pd.DataFrame(
    [
        {"Elemento": "Elemento A", "Cantidad": 12, "Categoría": "Categoría 1"},
        {"Elemento": "Elemento B", "Cantidad": 8, "Categoría": "Categoría 2"},
    ]
)
CONDICIONES_INICIALES = pd.DataFrame(
    [{"Categoría": "Categoría 1", "Operador": ">=", "Valor": 1, "Máximo": None}]
)


def reiniciar_datos() -> None:
    st.session_state.poblacion_df = DATOS_INICIALES.copy()
    st.session_state.condiciones_df = CONDICIONES_INICIALES.copy()
    st.session_state.tamano_muestra = 5
    st.session_state.simulaciones = 10000
    st.session_state.semilla = 2026
    st.session_state.resultado = None


if "poblacion_df" not in st.session_state:
    reiniciar_datos()

st.title("Probabilidad exacta y simulación")
st.caption("Extracciones sin reemplazo en una población finita con categorías definidas por el usuario.")

encabezado_izq, encabezado_der = st.columns([4, 1])
with encabezado_izq:
    st.subheader("1. Población")
with encabezado_der:
    st.button("Reiniciar Datos", on_click=reiniciar_datos, use_container_width=True)

st.session_state.poblacion_df = st.data_editor(
    st.session_state.poblacion_df,
    key="editor_poblacion",
    num_rows="dynamic",
    use_container_width=True,
    hide_index=True,
    column_config={
        "Elemento": st.column_config.TextColumn("Elemento", required=True),
        "Cantidad": st.column_config.NumberColumn("Cantidad", min_value=0, step=1, required=True),
        "Categoría": st.column_config.TextColumn("Categoría", required=True),
    },
)

try:
    poblacion_actual = construir_poblacion(st.session_state.poblacion_df.to_dict("records"))
    categorias_actuales = list(poblacion_actual.categorias)
    metricas = st.columns(3)
    metricas[0].metric("Población total", poblacion_actual.total)
    metricas[1].metric("Elementos únicos", poblacion_actual.elementos_unicos)
    metricas[2].metric("Categorías", len(categorias_actuales))
except ValueError as error:
    poblacion_actual = None
    categorias_actuales = []
    st.error(str(error))

st.subheader("2. Condiciones")
st.write("Todas las filas se combinan mediante AND lógico. Use =, >=, <= o RANGO.")
st.session_state.condiciones_df = st.data_editor(
    st.session_state.condiciones_df,
    key="editor_condiciones",
    num_rows="dynamic",
    use_container_width=True,
    hide_index=True,
    column_config={
        "Categoría": st.column_config.SelectboxColumn(
            "Categoría", options=categorias_actuales, required=True
        ),
        "Operador": st.column_config.SelectboxColumn(
            "Operador", options=["=", ">=", "<=", "RANGO"], required=True
        ),
        "Valor": st.column_config.NumberColumn("Valor", min_value=0, step=1, required=True),
        "Máximo": st.column_config.NumberColumn("Máximo", min_value=0, step=1),
    },
)

st.subheader("3. Configuración")
columna_a, columna_b, columna_c = st.columns(3)
maximo_muestra = max(0, poblacion_actual.total if poblacion_actual else 0)
st.session_state.tamano_muestra = columna_a.number_input(
    "Tamaño de muestra",
    min_value=0,
    max_value=maximo_muestra,
    value=min(int(st.session_state.tamano_muestra), maximo_muestra),
    step=1,
)
st.session_state.simulaciones = columna_b.number_input(
    "Cantidad de simulaciones",
    min_value=1,
    max_value=1_000_000,
    value=int(st.session_state.simulaciones),
    step=1000,
)
st.session_state.semilla = columna_c.number_input(
    "Semilla de simulación",
    min_value=0,
    value=int(st.session_state.semilla),
    step=1,
)

if st.button("Calcular probabilidad y simular", type="primary", use_container_width=True):
    try:
        poblacion = construir_poblacion(st.session_state.poblacion_df.to_dict("records"))
        condiciones = construir_condiciones(st.session_state.condiciones_df.to_dict("records"))
        with st.spinner("Calculando..."):
            st.session_state.resultado = ejecutar_calculo(
                poblacion=poblacion,
                tamano_muestra=int(st.session_state.tamano_muestra),
                condiciones=condiciones,
                simulaciones=int(st.session_state.simulaciones),
                semilla=int(st.session_state.semilla),
            )
    except (ValueError, TypeError) as error:
        st.session_state.resultado = None
        st.error(str(error))

resultado = st.session_state.resultado
if resultado is not None:
    st.subheader("4. Resultados")
    resultados = st.columns(4)
    resultados[0].metric("Probabilidad exacta", f"{resultado.probabilidad_decimal:.8%}")
    resultados[1].metric("Frecuencia empírica", f"{resultado.frecuencia_empirica:.8%}")
    resultados[2].metric("Éxitos simulados", f"{resultado.exitos_simulados:,}")
    resultados[3].metric("Diferencia absoluta", f"{abs(resultado.probabilidad_decimal - resultado.frecuencia_empirica):.8%}")
    st.code(
        f"Probabilidad exacta = {resultado.probabilidad_exacta.numerator} / "
        f"{resultado.probabilidad_exacta.denominator}",
        language="text",
    )
