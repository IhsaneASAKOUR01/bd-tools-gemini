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
        "subtitle": "Tailor project references and consultant CVs to a tender.",
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
        "title": "Format CVs in a template",
        "subtitle": "Map source CVs into your target Word template.",
        "runner": run_cvs_adapter,
    },
}


def gemini_is_configured() -> bool:
    try:
        return bool(st.secrets.get("gemini", {}).get("api_key"))
    except Exception:
        return False


if "bd_route" not in st.session_state:
    st.session_state.bd_route = "cvs_refs"


def go_to(route: str) -> None:
    st.session_state.bd_route = route
    st.rerun()


def render_topbar() -> None:
    brand, spacer, nav1, nav2, nav3, status = st.columns(
        [1.35, 1.15, 1.25, 1.35, 1.05, 0.95],
        vertical_alignment="center",
        gap="small",
    )

    with brand:
        logo_col, name_col = st.columns([0.22, 1.78], vertical_alignment="center", gap="small")
        with logo_col:
            st.image(str(ROOT / "logo.png"), width=25)
        with name_col:
            st.markdown('<div class="brand-lockup"><strong>BD</strong> Tools</div>', unsafe_allow_html=True)

    route = st.session_state.bd_route
    for key, col in zip(["cvs_refs", "reference", "cv_template"], [nav1, nav2, nav3]):
        with col:
            active = route == key
            label = f"{TOOLS[key]['nav']}" + ("  •" if active else "")
            if st.button(label, key=f"nav_{key}", type="secondary"):
                go_to(key)

    with status:
        state = "connected" if gemini_is_configured() else "missing"
        label = "Gemini" if gemini_is_configured() else "Add Gemini key"
        st.markdown(
            f'<div class="api-state {state}"><span></span>{label}</div>',
            unsafe_allow_html=True,
        )

    st.markdown('<div class="top-rule"></div>', unsafe_allow_html=True)


def render_tool(route: str) -> None:
    tool = TOOLS[route]
    st.markdown(f'<h1 class="page-title">{tool["title"]}</h1>', unsafe_allow_html=True)
    st.markdown(f'<div class="page-subtitle">{tool["subtitle"]}</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-rule"></div>', unsafe_allow_html=True)
    tool["runner"]()


render_topbar()
render_tool(st.session_state.bd_route)
