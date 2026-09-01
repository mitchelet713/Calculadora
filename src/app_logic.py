import streamlit as st

def initialise_state():
    defaults={"step":1,"categories":["Categoría A","Categoría B"],"population_items":[],"population_df":None,"analysis_result":None,"source_text":""}
    for key,value in defaults.items():
        if key not in st.session_state: st.session_state[key]=value

def go_to(step):
    st.session_state.step=step
    st.session_state.analysis_result=None

def reset_all():
    for key in list(st.session_state.keys()): del st.session_state[key]
