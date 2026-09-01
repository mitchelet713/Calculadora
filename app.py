import pandas as pd
import streamlit as st
from src.app_logic import go_to, initialise_state, reset_all
from src.data_parser import ParseError, decode_uploaded_file, parse_population
from src.math_engine import exact_probability
from src.models import AnalysisResult, Condition, PopulationItem
from src.sim_engine import run_simulations

st.set_page_config(layout="wide", page_title="Simulador Probabilístico Avanzado", page_icon="◈")
st.markdown('''<style>
:root{--cyan:#20d9ff;--violet:#8b5cf6;--ink:#f8fafc}.stApp{background:radial-gradient(circle at 15% 0%,#172554 0%,#070b16 40%,#030712 100%);color:var(--ink)}
#MainMenu,footer,header{visibility:hidden}.block-container{max-width:1450px;padding:2rem 3rem 4rem}.hero{padding:1.4rem 1.6rem;border:1px solid rgba(32,217,255,.28);border-radius:18px;background:linear-gradient(135deg,rgba(15,23,42,.96),rgba(17,24,39,.84));box-shadow:0 18px 50px rgba(0,0,0,.35)}.eyebrow{color:var(--cyan);letter-spacing:.18em;font-size:.72rem;font-weight:800}.hero h1{margin:.25rem 0}.hero p{color:#b6c3d6;margin:0}.stepper{display:flex;gap:.7rem;margin:1.1rem 0 1.5rem}.step{flex:1;padding:.8rem 1rem;border-radius:12px;background:#0f172a;border:1px solid #263248;color:#718096}.step.active{color:#fff;border-color:var(--cyan);box-shadow:0 0 20px rgba(32,217,255,.12)}.step.done{color:#b6f3ff;border-color:#155e75}
[data-testid="stVerticalBlockBorderWrapper"]{background:rgba(15,23,42,.72);border-color:rgba(148,163,184,.2);border-radius:16px}.stButton>button{border:1px solid var(--cyan);border-radius:10px;font-weight:750;color:#fff;background:linear-gradient(90deg,#0e7490,#6d28d9)}[data-testid="stMetric"]{background:#101827;padding:1rem;border-radius:14px;border:1px solid rgba(32,217,255,.2)}[data-testid="stMetricValue"]{color:var(--cyan)}
/* Contraste corregido para todos los controles editables */
.stTextInput input,.stNumberInput input,.stTextArea textarea,[data-baseweb="select"]>div{background:#08111f!important;color:#f8fafc!important;-webkit-text-fill-color:#f8fafc!important;border-color:#334155!important}.stTextInput input::placeholder,.stTextArea textarea::placeholder{color:#94a3b8!important;-webkit-text-fill-color:#94a3b8!important}[data-baseweb="select"] span,[data-baseweb="popover"] li{color:#f8fafc!important}.stDataFrame,.stDataEditor{color:#f8fafc!important}[data-testid="stDataFrameResizable"]{background:#0b1220!important}div[data-testid="stDataEditor"] canvas{color:#f8fafc!important}.small-note{color:#aebbd0;font-size:.86rem}
</style>''',unsafe_allow_html=True)
initialise_state()
st.markdown('''<div class="hero"><div class="eyebrow">MOTOR HIPERGEOMÉTRICO · SIMULACIÓN SIN REEMPLAZO</div><h1>Simulador Probabilístico Avanzado</h1><p>Construye la población, clasifica sus elementos y compara el cálculo exacto con la frecuencia empírica.</p></div>''',unsafe_allow_html=True)
labels=["01 · Importación","02 · Clasificación","03 · Análisis"]
html='<div class="stepper">'+''.join(f'<div class="step {"active" if i==st.session_state.step else "done" if i<st.session_state.step else ""}">{x}</div>' for i,x in enumerate(labels,1))+'</div>'
st.markdown(html,unsafe_allow_html=True)

if st.session_state.step==1:
    left,right=st.columns([1.15,1],gap="large")
    with left,st.container(border=True):
        st.subheader("Categorías personalizadas"); categories_text=st.text_area("Una categoría por línea",value="\n".join(st.session_state.categories),height=160)
    with right,st.container(border=True):
        st.subheader("Importar población"); quantities_first=st.checkbox("Las cantidades están al inicio de cada línea",value=True); uploaded=st.file_uploader("Cargar archivo TXT",type=["txt"]); source_text=st.text_area("Datos línea por línea",value=st.session_state.source_text,height=180,placeholder="3 Elemento Alfa\n2 Elemento Beta")
    if st.button("Continuar al Paso 2",type="primary",use_container_width=True):
        try:
            text=decode_uploaded_file(uploaded) if uploaded else source_text; categories=list(dict.fromkeys(x.strip() for x in categories_text.splitlines() if x.strip()))
            if not categories: raise ValueError("Debes crear al menos una categoría.")
            items=parse_population(text,quantities_first); st.session_state.categories=categories; st.session_state.population_items=items; st.session_state.source_text=text; st.session_state.population_df=pd.DataFrame([{"Nombre":i.name,"Cantidad":i.quantity,"Categoría":"Sin clasificar"} for i in items]); go_to(2); st.rerun()
        except (ParseError,ValueError) as e: st.error(str(e))
elif st.session_state.step==2:
    main,summary=st.columns([3,1],gap="large")
    with main,st.container(border=True):
        st.subheader("Edición y clasificación"); options=["Sin clasificar"]+st.session_state.categories
        edited=st.data_editor(st.session_state.population_df,hide_index=True,use_container_width=True,num_rows="fixed",column_config={"Nombre":st.column_config.TextColumn("Nombre",disabled=True),"Cantidad":st.column_config.NumberColumn("Cantidad",min_value=1,step=1,required=True),"Categoría":st.column_config.SelectboxColumn("Categoría",options=options,required=True)},key="population_editor")
    with summary,st.container(border=True):
        qty=pd.to_numeric(edited["Cantidad"],errors="coerce").fillna(0); st.subheader("Resumen poblacional"); st.metric("Total población",f"{int(qty.sum()):,}"); st.metric("Elementos únicos",len(edited)); st.metric("Categorías definidas",len(st.session_state.categories))
    back,forward=st.columns(2)
    if back.button("Atrás",use_container_width=True): st.session_state.population_df=edited; go_to(1); st.rerun()
    if forward.button("Continuar al Análisis",type="primary",use_container_width=True):
        try:
            st.session_state.population_items=[PopulationItem(str(r["Nombre"]),int(r["Cantidad"]),str(r["Categoría"])) for r in edited.to_dict("records")]; st.session_state.population_df=edited; go_to(3); st.rerun()
        except Exception as e: st.error(f"Revisa las cantidades: {e}")
else:
    items=st.session_state.population_items; total=sum(i.quantity for i in items); cats=[c for c in ["Sin clasificar"]+st.session_state.categories if any(i.category==c for i in items)]
    config,panel=st.columns([1,1.4],gap="large")
    with config,st.container(border=True):
        st.subheader("Parámetros de ejecución"); sample_size=st.number_input("Tamaño de muestra",1,total,min(5,total),1); simulations=st.number_input("Número total de simulaciones",100,1000000,10000,100); details=st.number_input("Cantidad de simulaciones a visualizar detalladamente",0,int(simulations),min(10,int(simulations)),1)
    with panel,st.container(border=True):
        st.subheader("Condiciones acumulativas"); st.caption("Cada categoría debe quedar dentro de su intervalo mínimo y máximo. Todas las condiciones se unen mediante AND lógico."); count=st.number_input("Número de condiciones",1,max(1,len(cats)),1,1); conditions=[]
        for index in range(int(count)):
            c1,c2,c3=st.columns([2,1,1]); category=c1.selectbox(f"Categoría {index+1}",cats,key=f"cat_{index}"); minimum=c2.number_input(f"Mínimo {index+1}",0,int(sample_size),1,1,key=f"min_{index}"); maximum=c3.number_input(f"Máximo {index+1}",0,int(sample_size),int(sample_size),1,key=f"max_{index}"); conditions.append(Condition(category,int(minimum),int(maximum)))
    if st.button("Ejecutar Análisis",type="primary",use_container_width=True):
        try:
            if len({c.category for c in conditions})!=len(conditions): raise ValueError("Cada condición debe usar una categoría diferente.")
            exact=exact_probability(items,int(sample_size),conditions); empirical,successes,detail_rows=run_simulations(items,int(sample_size),conditions,int(simulations),int(details)); st.session_state.analysis_result=AnalysisResult(exact,empirical,successes,int(simulations),detail_rows)
        except ValueError as e: st.error(str(e))
    result=st.session_state.analysis_result
    if result:
        st.divider(); st.subheader("Resultados del análisis"); a,b,c=st.columns(3); a.metric("Probabilidad exacta",f"{result.exact_probability:.4%}"); b.metric("Frecuencia empírica",f"{result.empirical_frequency:.4%}"); c.metric("Diferencia absoluta",f"{abs(result.exact_probability-result.empirical_frequency):.4%}"); st.caption(f"Éxitos observados: {result.successes:,} de {result.simulation_count:,} simulaciones.")
        with st.expander("Visualización detallada de simulaciones",expanded=True): st.dataframe(pd.DataFrame(result.detailed_samples),hide_index=True,use_container_width=True) if result.detailed_samples else st.info("No se solicitaron detalles.")
    back,reset=st.columns(2)
    if back.button("Atrás a clasificación",use_container_width=True): go_to(2); st.rerun()
    if reset.button("Reiniciar todo",use_container_width=True): reset_all(); st.rerun()
