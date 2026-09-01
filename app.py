"""Interfaz Streamlit organizada como asistente de tres pasos."""
from __future__ import annotations
import pandas as pd
import streamlit as st
from src.app_logic import (construir_condiciones, construir_poblacion, ejecutar_calculo,
                           separar_valores)

st.set_page_config(page_title="Analizador de probabilidad", page_icon="📊", layout="wide")
st.markdown("""
<style>
.stApp {background: linear-gradient(180deg,#f6f8fc 0%,#ffffff 45%);}
.block-container {max-width: 1100px; padding-top: 2rem; padding-bottom: 4rem;}
.hero {padding: 1.5rem 1.7rem; border-radius: 20px; color: white;
 background: linear-gradient(120deg,#172554,#2563eb); margin-bottom: 1.2rem;
 box-shadow: 0 12px 30px rgba(37,99,235,.16);}
.hero h1 {margin:0; font-size:2.05rem}.hero p {margin:.4rem 0 0; opacity:.9}
.stepbar {display:flex; gap:8px; margin: 1rem 0 1.5rem;}
.step {flex:1; padding:.7rem; text-align:center; border-radius:12px; font-weight:700;
 background:#e8edf7; color:#506078;}
.active {background:#2563eb; color:white}.done {background:#dbeafe; color:#1d4ed8}
.panel {background:white; border:1px solid #e5eaf2; border-radius:18px; padding:1.2rem 1.35rem;
 box-shadow:0 8px 24px rgba(15,23,42,.06); margin-bottom:1rem;}
.small-note {color:#64748b; font-size:.92rem}
div.stButton > button, div.stFormSubmitButton > button {border-radius:12px; font-weight:700; min-height:44px;}
[data-testid="stMetric"] {background:white; border:1px solid #e5eaf2; border-radius:14px; padding:14px;}
</style>
""", unsafe_allow_html=True)

def iniciar() -> None:
    valores = {
        "paso": 1, "texto_elementos": "", "texto_categorias": "",
        "elementos": tuple(), "categorias_definidas": tuple(), "tabla_poblacion": None,
        "poblacion": None, "condiciones_df": None, "resultado": None,
        "muestra": 1, "simulaciones": 10000, "semilla": 2026,
    }
    for clave, valor in valores.items():
        if clave not in st.session_state:
            st.session_state[clave] = valor

def reiniciar() -> None:
    for clave in list(st.session_state.keys()):
        del st.session_state[clave]
    st.rerun()

def ir_a(paso: int) -> None:
    st.session_state.paso = paso
    st.rerun()

iniciar()
st.markdown('<div class="hero"><h1>Analizador de probabilidad</h1><p>Poblaciones finitas, cálculo exacto y simulación sin reemplazo.</p></div>', unsafe_allow_html=True)
enc1, enc2 = st.columns([5,1])
with enc2:
    st.button("↻ Reiniciar", on_click=reiniciar, use_container_width=True)
paso = st.session_state.paso
clases = ["active" if paso == i else "done" if paso > i else "" for i in (1,2,3)]
st.markdown(f'<div class="stepbar"><div class="step {clases[0]}">1. Definición</div><div class="step {clases[1]}">2. Cantidades</div><div class="step {clases[2]}">3. Cálculo</div></div>', unsafe_allow_html=True)

if paso == 1:
    st.markdown('<div class="panel"><h3>Define los elementos y las categorías</h3><p class="small-note">Puedes pegar listas completas. Se admite un valor por línea, separado por comas o por punto y coma. Los duplicados se eliminan automáticamente.</p></div>', unsafe_allow_html=True)
    with st.form("form_paso_1"):
        izquierda, derecha = st.columns(2, gap="large")
        with izquierda:
            texto_elementos = st.text_area("Lista de elementos", value=st.session_state.texto_elementos,
                height=300, placeholder="Elemento A\nElemento B\nElemento C", help="Escribe o pega todos los elementos de la población.")
        with derecha:
            texto_categorias = st.text_area("Categorías disponibles", value=st.session_state.texto_categorias,
                height=300, placeholder="Categoría 1\nCategoría 2", help="Estas categorías estarán disponibles en el paso siguiente.")
        continuar = st.form_submit_button("Continuar a cantidades →", type="primary", use_container_width=True)
    if continuar:
        elementos = separar_valores(texto_elementos)
        categorias = separar_valores(texto_categorias)
        if not elementos:
            st.error("Ingresa al menos un elemento.")
        elif not categorias:
            st.error("Define al menos una categoría.")
        else:
            st.session_state.texto_elementos = texto_elementos
            st.session_state.texto_categorias = texto_categorias
            st.session_state.elementos = elementos
            st.session_state.categorias_definidas = categorias
            st.session_state.tabla_poblacion = pd.DataFrame({"Elemento": elementos, "Cantidad": [1]*len(elementos), "Categoría": [categorias[0]]*len(elementos)})
            st.session_state.paso = 2
            st.rerun()

elif paso == 2:
    st.markdown('<div class="panel"><h3>Asigna cantidades y categorías</h3><p class="small-note">Los elementos se cargaron automáticamente desde tu lista. Solo completa la cantidad y selecciona la categoría correspondiente.</p></div>', unsafe_allow_html=True)
    with st.form("form_paso_2"):
        tabla = st.data_editor(st.session_state.tabla_poblacion, hide_index=True, use_container_width=True,
            disabled=["Elemento"], num_rows="fixed",
            column_config={
                "Elemento": st.column_config.TextColumn("Elemento", width="large"),
                "Cantidad": st.column_config.NumberColumn("Cantidad", min_value=0, step=1, required=True),
                "Categoría": st.column_config.SelectboxColumn("Categoría", options=list(st.session_state.categorias_definidas), required=True),
            })
        col_atras, col_continuar = st.columns([1,2])
        atras = col_atras.form_submit_button("← Volver", use_container_width=True)
        continuar = col_continuar.form_submit_button("Continuar al cálculo →", type="primary", use_container_width=True)
    if atras:
        ir_a(1)
    if continuar:
        try:
            poblacion = construir_poblacion(tabla.to_dict("records"))
            st.session_state.tabla_poblacion = tabla.copy()
            st.session_state.poblacion = poblacion
            categorias_activas = list(poblacion.categorias)
            st.session_state.condiciones_df = pd.DataFrame([{"Categoría": categorias_activas[0], "Operador": ">=", "Valor": 1, "Máximo": None}])
            st.session_state.muestra = min(max(1, st.session_state.muestra), poblacion.total)
            st.session_state.resultado = None
            st.session_state.paso = 3
            st.rerun()
        except ValueError as error:
            st.error(str(error))

else:
    poblacion = st.session_state.poblacion
    st.markdown('<div class="panel"><h3>Configura el cálculo y la simulación</h3><p class="small-note">Todas las condiciones se combinan mediante AND lógico.</p></div>', unsafe_allow_html=True)
    m1, m2, m3 = st.columns(3)
    m1.metric("Población total", poblacion.total)
    m2.metric("Elementos únicos", poblacion.elementos_unicos)
    m3.metric("Categorías activas", len(poblacion.categorias))
    with st.expander("Ver resumen de la población"):
        st.dataframe(st.session_state.tabla_poblacion, hide_index=True, use_container_width=True)
    with st.form("form_calculo"):
        st.subheader("Condiciones")
        condiciones_df = st.data_editor(st.session_state.condiciones_df, hide_index=True,
            use_container_width=True, num_rows="dynamic",
            column_config={
                "Categoría": st.column_config.SelectboxColumn("Categoría", options=list(poblacion.categorias), required=True),
                "Operador": st.column_config.SelectboxColumn("Operador", options=["=", ">=", "<=", "RANGO"], required=True),
                "Valor": st.column_config.NumberColumn("Valor o mínimo", min_value=0, step=1, required=True),
                "Máximo": st.column_config.NumberColumn("Máximo para RANGO", min_value=0, step=1),
            })
        st.subheader("Parámetros")
        c1, c2, c3 = st.columns(3)
        muestra = c1.number_input("Tamaño de muestra", min_value=0, max_value=poblacion.total, value=int(st.session_state.muestra), step=1)
        simulaciones = c2.number_input("Cantidad de simulaciones", min_value=1, max_value=1_000_000, value=int(st.session_state.simulaciones), step=1000)
        semilla = c3.number_input("Semilla", min_value=0, value=int(st.session_state.semilla), step=1)
        calcular = st.form_submit_button("Calcular y simular", type="primary", use_container_width=True)
    if calcular:
        try:
            condiciones = construir_condiciones(condiciones_df.to_dict("records"))
            st.session_state.condiciones_df = condiciones_df.copy()
            st.session_state.muestra = muestra
            st.session_state.simulaciones = simulaciones
            st.session_state.semilla = semilla
            with st.spinner("Realizando cálculo exacto y simulaciones..."):
                st.session_state.resultado = ejecutar_calculo(poblacion, int(muestra), condiciones, int(simulaciones), int(semilla))
        except (ValueError, TypeError) as error:
            st.session_state.resultado = None
            st.error(str(error))
    resultado = st.session_state.resultado
    if resultado:
        st.success("Proceso completado correctamente.")
        r1, r2, r3, r4 = st.columns(4)
        r1.metric("Probabilidad exacta", f"{resultado.probabilidad_decimal:.6%}")
        r2.metric("Frecuencia empírica", f"{resultado.frecuencia_empirica:.6%}")
        r3.metric("Éxitos", f"{resultado.exitos_simulados:,}")
        r4.metric("Diferencia", f"{abs(resultado.probabilidad_decimal-resultado.frecuencia_empirica):.6%}")
        st.info(f"Resultado exacto: {resultado.probabilidad_exacta.numerator} / {resultado.probabilidad_exacta.denominator}")
    nav1, nav2 = st.columns([1,3])
    if nav1.button("← Editar cantidades", use_container_width=True):
        ir_a(2)
