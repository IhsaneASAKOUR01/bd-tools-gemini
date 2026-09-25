from pathlib import Path

import streamlit as st

from CVs_REFs_adapter.app import run_app as run_cvs_refs_adapter
from REF_creater.app import run_app as run_ref_creator
from CVs_adapter.app import run_app as run_cvs_adapter

ROOT = Path(__file__).resolve().parent

st.set_page_config(
    page_title="BD Tools | Africa Climate Solutions",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="collapsed",
)


def load_css(path: Path) -> None:
    with open(path, encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


load_css(ROOT / "style.css")

TOOLS = {
    "cvs_refs": {
        "nav": "CVs + References",
        "title": "Adapt CVs & references",
        "subtitle": "Tailor consultant profiles and project references to a tender.",
        "runner": run_cvs_refs_adapter,
    },
    "reference": {
        "nav": "Reference Creator",
        "title": "Create a project reference",
        "subtitle": "Turn a source report into French and English reference sheets.",
        "runner": run_ref_creator,
    },
    "cv_template": {
        "nav": "CV Template",
        "title": "Format CVs",
        "subtitle": "Apply a Word template to one or more source CVs.",
        "runner": run_cvs_adapter,
    },
}

if "bd_route" not in st.session_state:
    st.session_state.bd_route = "cvs_refs"


def go_to(route: str) -> None:
    st.session_state.bd_route = route
    st.rerun()


def render_topbar() -> None:
    route = st.session_state.bd_route

    brand, nav1, nav2, nav3, flex = st.columns(
        [1.65, 1.28, 1.22, 1.0, 2.85],
        vertical_alignment="center",
        gap="small",
    )

    with brand:
        logo_col, product_col = st.columns([1.25, 0.7], vertical_alignment="center", gap="small")
        with logo_col:
            st.image(str(ROOT / "logo.png"), width=112)
        with product_col:
            st.markdown('<div class="product-name">BD Tools</div>', unsafe_allow_html=True)

    for key, col in zip(["cvs_refs", "reference", "cv_template"], [nav1, nav2, nav3]):
        with col:
            if st.button(TOOLS[key]["nav"], key=f"nav_{key}", type="secondary"):
                go_to(key)

    # Active route gets a precise underline without turning navigation into pills/tabs.
    st.markdown(
        f"""
        <style>
        .st-key-nav_{route} button {{
            color: #132f44 !important;
            font-weight: 750 !important;
            border-bottom: 2px solid #0b87a3 !important;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="app-rule"></div>', unsafe_allow_html=True)


def render_tool(route: str) -> None:
    tool = TOOLS[route]
    st.markdown(
        f"""
        <div class="tool-heading">
            <h1>{tool['title']}</h1>
            <p>{tool['subtitle']}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    tool["runner"]()


render_topbar()
render_tool(st.session_state.bd_route)
