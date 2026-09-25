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
        "hint": "Tender title · reference · consultant CVs",
        "runner": run_cvs_refs_adapter,
    },
    "reference": {
        "nav": "Reference Creator",
        "title": "Create a project reference",
        "hint": "Report in · French and English references out",
        "runner": run_ref_creator,
    },
    "cv_template": {
        "nav": "CV Template",
        "title": "Format CVs in a template",
        "hint": "Source CVs · target Word template",
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


def render_chrome() -> None:
    brand, nav1, nav2, nav3, status = st.columns(
        [2.1, 1.55, 1.55, 1.35, 2.0],
        vertical_alignment="center",
        gap="small",
    )

    with brand:
        logo_col, text_col = st.columns([0.28, 1.72], vertical_alignment="center", gap="small")
        with logo_col:
            st.image(str(ROOT / "logo.png"), width=28)
        with text_col:
            st.markdown('<div class="brand-name">BD Tools</div>', unsafe_allow_html=True)

    route = st.session_state.bd_route
    for key, col in zip(["cvs_refs", "reference", "cv_template"], [nav1, nav2, nav3]):
        with col:
            if st.button(
                TOOLS[key]["nav"],
                key=f"nav_{key}",
                type="primary" if route == key else "secondary",
                use_container_width=False,
            ):
                go_to(key)

    with status:
        if gemini_is_configured():
            st.markdown('<div class="status-ok">● Gemini connected</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="status-missing">● Gemini key missing</div>', unsafe_allow_html=True)

    st.markdown('<div class="chrome-rule"></div>', unsafe_allow_html=True)


def render_tool(route: str) -> None:
    tool = TOOLS[route]

    title_col, hint_col = st.columns([3.1, 5.9], vertical_alignment="bottom")
    with title_col:
        st.markdown(f'<div class="tool-title">{tool["title"]}</div>', unsafe_allow_html=True)
    with hint_col:
        st.markdown(f'<div class="tool-hint">{tool["hint"]}</div>', unsafe_allow_html=True)

    st.markdown('<div class="title-rule"></div>', unsafe_allow_html=True)
    tool["runner"]()


render_chrome()
render_tool(st.session_state.bd_route)
