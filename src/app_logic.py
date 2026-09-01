import streamlit as st

DEFAULT_CATEGORIES = ["Categoría A", "Categoría B"]


def initialise_state() -> None:
    defaults = {
        "step": 1,
        "categories": DEFAULT_CATEGORIES.copy(),
        "population_items": [],
        "population_df": None,
        "analysis_result": None,
        "source_text": "",
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def go_to(step: int) -> None:
    st.session_state.step = step
    st.session_state.analysis_result = None


def reset_all() -> None:
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.session_state.step = 1
