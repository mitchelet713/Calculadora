import streamlit as st
DEFAULT_CATEGORIES=["Categoría A","Categoría B"]
def initialise_state():
    defaults={"step":1,"categories":DEFAULT_CATEGORIES.copy(),"population_items":[],"population_df":None,"analysis_result":None,"source_text":""}
    for k,v in defaults.items():
        if k not in st.session_state: st.session_state[k]=v
def go_to(step): st.session_state.step=step; st.session_state.analysis_result=None
def reset_all():
    for k in list(st.session_state): del st.session_state[k]
    st.session_state.step=1
