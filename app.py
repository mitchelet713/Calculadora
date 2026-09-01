import pandas as pd
import streamlit as st

from src.app_logic import go_to, initialise_state, reset_all
from src.data_parser import ParseError, decode_uploaded_file, parse_population
from src.math_engine import exact_probability
from src.models import AnalysisResult, Condition, PopulationItem
from src.sim_engine import run_simulations

st.set_page_config(layout="wide", page_title="Simulador Probabilístico Avanzado", page_icon="◈")

st.markdown("""
<style>
:root { --cyan:#20d9ff; --violet:#8b5cf6; --panel:#111827; --muted:#94a3b8; }
.stApp { background: radial-gradient(circle at 15% 0%, #172554 0%, #070b16 40%, #030712 100%); color:#e5f3ff; }
#MainMenu, footer, header { visibility:hidden; }
.block-container { max-width:1450px; padding:2rem 3rem 4rem; }
.hero { padding:1.4rem 1.6rem; border:1px solid rgba(32,217,255,.28); border-radius:18px;
 background:linear-gradient(135deg,rgba(15,23,42,.96),rgba(17,24,39,.84)); box-shadow:0 18px 50px rgba(0,0,0,.35); }
.eyebrow { color:var(--cyan); letter-spacing:.18em; font-size:.72rem; font-weight:800; }
.hero h1 { margin:.25rem 0; font-size:2rem; }
.hero p { color:var(--muted); margin:0; }
.stepper { display:flex; gap:.7rem; margin:1.1rem 0 1.5rem; }
.step { flex:1; padding:.8rem 1rem; border-radius:12px; background:rgba(15,23,42,.72); border:1px solid #263248; color:#64748b; }
.step.active { color:#fff; border-color:var(--cyan); box-shadow:0 0 20px rgba(32,217,255,.12); }
.step.done { color:#b6f3ff; border-color:#155e75; }
[data-testid="stVerticalBlockBorderWrapper"] { background:rgba(15,23,42,.66); border-color:rgba(148,163,184,.18); border-radius:16px; }
.stButton>button { border:1px solid var(--cyan); border-radius:10px; font-weight:750; color:#e8fbff; background:linear-gradient(90deg,#0e7490,#6d28d9); transition:.2s; }
.stButton>button:hover { border-color:#fff; transform:translateY(-1px); box-shadow:0 0 22px rgba(32,217,255,.25); }
[data-testid="stMetric"] { background:linear-gradient(145deg,rgba(15,23,42,.92),rgba(30,41,59,.72)); padding:1rem; border-radius:14px; border:1px solid rgba(32,217,255,.2); }
[data-testid="stMetricValue"] { color:var(--cyan); }
.stTextInput input, .stNumberInput input, textarea { background:#0b1220 !important; }
.small-note { color:#94a3b8; font-size:.86rem; }
</style>
""", unsafe_allow_html=True)

initialise_state()

st.markdown("""
<div class="hero"><div class="eyebrow">MOTOR HIPERGEOMÉTRICO · SIMULACIÓN SIN REEMPLAZO</div>
<h1>Simulador Probabilístico Avanzado</h1>
<p>Construye la población, clasifica sus elementos y compara el cálculo exacto con la frecuencia empírica.</p></div>
""", unsafe_allow_html=True)

labels = ["01 · Importación", "02 · Clasificación", "03 · Análisis"]
steps_html = '<div class="stepper">'
for index, label in enumerate(labels, start=1):
    state = "active" if index == st.session_state.step else "done" if index < st.session_state.step else ""
    steps_html += f'<div class="step {state}">{label}</div>'
steps_html += '</div>'
st.markdown(steps_html, unsafe_allow_html=True)

if st.session_state.step == 1:
    left, right = st.columns([1.15, 1], gap="large")
    with left:
        with st.container(border=True):
            st.subheader("Categorías personalizadas")
            st.caption("Define las categorías que estarán disponibles durante la clasificación.")
            categories_text = st.text_area(
                "Una categoría por línea",
                value="\n".join(st.session_state.categories),
                height=150,
                placeholder="Categoría A\nCategoría B",
            )
    with right:
        with st.container(border=True):
            st.subheader("Importar población")
            quantities_first = st.checkbox("Las cantidades están al inicio de cada línea", value=True)
            uploaded = st.file_uploader("Cargar archivo TXT", type=["txt"])
            source_text = st.text_area(
                "Datos línea por línea",
                value=st.session_state.source_text,
                height=180,
                placeholder="3 Elemento Alfa\n2 Elemento Beta\n1 Elemento Gamma",
            )
            st.markdown('<div class="small-note">Formato: Cantidad, espacio y nombre del elemento.</div>', unsafe_allow_html=True)

    if st.button("Continuar al Paso 2", type="primary", use_container_width=True):
        try:
            text = decode_uploaded_file(uploaded) if uploaded is not None else source_text
            categories = list(dict.fromkeys(c.strip() for c in categories_text.splitlines() if c.strip()))
            if not categories:
                raise ValueError("Debes crear al menos una categoría.")
            items = parse_population(text, quantities_first)
            st.session_state.categories = categories
            st.session_state.population_items = items
            st.session_state.source_text = text
            st.session_state.population_df = pd.DataFrame(
                [{"Nombre": i.name, "Cantidad": i.quantity, "Categoría": "Sin clasificar"} for i in items]
            )
            go_to(2)
            st.rerun()
        except (ParseError, ValueError) as error:
            st.error(str(error))

elif st.session_state.step == 2:
    main, summary = st.columns([3, 1], gap="large")
    with main:
        with st.container(border=True):
            st.subheader("Edición y clasificación")
            st.caption("Ajusta las cantidades y asigna una categoría a cada elemento.")
            options = ["Sin clasificar"] + st.session_state.categories
            edited = st.data_editor(
                st.session_state.population_df,
                hide_index=True,
                use_container_width=True,
                num_rows="fixed",
                column_config={
                    "Nombre": st.column_config.TextColumn("Nombre", disabled=True),
                    "Cantidad": st.column_config.NumberColumn("Cantidad", min_value=1, step=1, required=True),
                    "Categoría": st.column_config.SelectboxColumn("Categoría", options=options, required=True),
                },
                key="population_editor",
            )
    with summary:
        with st.container(border=True):
            st.subheader("Resumen poblacional")
            valid_qty = pd.to_numeric(edited["Cantidad"], errors="coerce").fillna(0)
            st.metric("Total población", f"{int(valid_qty.sum()):,}")
            st.metric("Elementos únicos", f"{len(edited):,}")
            st.metric("Categorías definidas", len(st.session_state.categories))

    back, forward = st.columns(2)
    if back.button("Atrás", use_container_width=True):
        st.session_state.population_df = edited
        go_to(1)
        st.rerun()
    if forward.button("Continuar al Análisis", type="primary", use_container_width=True):
        try:
            items = []
            for row in edited.to_dict("records"):
                quantity = int(row["Cantidad"])
                items.append(PopulationItem(str(row["Nombre"]), quantity, str(row["Categoría"])))
            st.session_state.population_items = items
            st.session_state.population_df = edited
            go_to(3)
            st.rerun()
        except (ValueError, TypeError) as error:
            st.error(f"Revisa las cantidades: {error}")

else:
    items = st.session_state.population_items
    total_population = sum(item.quantity for item in items)
    configured_categories = [
        c for c in ["Sin clasificar"] + st.session_state.categories
        if any(item.category == c for item in items)
    ]

    config, conditions_panel = st.columns([1, 1.25], gap="large")
    with config:
        with st.container(border=True):
            st.subheader("Parámetros de ejecución")
            sample_size = st.number_input("Tamaño de muestra", 1, total_population, min(5, total_population), 1)
            simulations = st.number_input("Número total de simulaciones", 100, 1_000_000, 10_000, 100)
            details_to_show = st.number_input(
                "Cantidad de simulaciones a visualizar detalladamente",
                0, int(simulations), min(10, int(simulations)), 1,
            )
    with conditions_panel:
        with st.container(border=True):
            st.subheader("Condiciones acumulativas")
            st.caption("Todas las condiciones deben cumplirse simultáneamente (AND lógico).")
            condition_count = st.number_input("Número de condiciones", 1, max(1, len(configured_categories)), 1, 1)
            conditions: list[Condition] = []
            for index in range(int(condition_count)):
                c1, c2 = st.columns([2, 1])
                category = c1.selectbox(
                    f"Categoría {index + 1}", configured_categories,
                    key=f"condition_category_{index}",
                )
                minimum = c2.number_input(
                    f"Cantidad mínima {index + 1}", 0, int(sample_size), 1, 1,
                    key=f"condition_min_{index}",
                )
                conditions.append(Condition(category, int(minimum)))

    if st.button("Ejecutar Análisis", type="primary", use_container_width=True):
        if len({c.category for c in conditions}) != len(conditions):
            st.error("Cada condición debe utilizar una categoría diferente.")
        else:
            with st.spinner("Ejecutando cálculo exacto y simulaciones..."):
                exact = exact_probability(items, int(sample_size), conditions)
                empirical, successes, details = run_simulations(
                    items, int(sample_size), conditions, int(simulations), int(details_to_show)
                )
                st.session_state.analysis_result = AnalysisResult(
                    exact, empirical, successes, int(simulations), details
                )

    result = st.session_state.analysis_result
    if result:
        st.divider()
        st.subheader("Resultados del análisis")
        m1, m2, m3 = st.columns(3)
        m1.metric("Probabilidad exacta", f"{result.exact_probability:.4%}")
        m2.metric("Frecuencia empírica", f"{result.empirical_frequency:.4%}")
        difference = abs(result.exact_probability - result.empirical_frequency)
        m3.metric("Diferencia absoluta", f"{difference:.4%}")
        st.caption(
            f"Éxitos observados: {result.successes:,} de {result.simulation_count:,} simulaciones. "
            "La simulación se realiza sin reemplazo."
        )
        with st.expander("Visualización detallada de simulaciones", expanded=True):
            if result.detailed_samples:
                st.dataframe(pd.DataFrame(result.detailed_samples), hide_index=True, use_container_width=True)
            else:
                st.info("La cantidad seleccionada para visualización detallada es cero.")

    back, reset = st.columns(2)
    if back.button("Atrás a clasificación", use_container_width=True):
        go_to(2)
        st.rerun()
    if reset.button("Reiniciar todo", use_container_width=True):
        reset_all()
        st.rerun()
