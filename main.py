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
        "number": "01",
        "title": "Adapt CVs & references",
        "meta": "Tailor existing bid material to a tender or AO.",
        "runner": run_cvs_refs_adapter,
    },
    "reference": {
        "number": "02",
        "title": "Create a project reference",
        "meta": "Turn a source report into French and English reference sheets.",
        "runner": run_ref_creator,
    },
    "cv_template": {
        "number": "03",
        "title": "Format CVs in a template",
        "meta": "Move source CV content into a selected Word template.",
        "runner": run_cvs_adapter,
    },
}


def gemini_is_configured() -> bool:
    try:
        return bool(st.secrets.get("gemini", {}).get("api_key"))
    except Exception:
        return False


if "bd_route" not in st.session_state:
    st.session_state.bd_route = "home"


def go_to(route: str) -> None:
    st.session_state.bd_route = route
    st.rerun()


def render_topbar() -> None:
    brand, spacer, action = st.columns([2.4, 5.4, 1.2], vertical_alignment="center")
    with brand:
        logo, name = st.columns([0.34, 1.8], vertical_alignment="center")
        with logo:
            st.image(str(ROOT / "logo.png"), width=34)
        with name:
            st.markdown("**BD Tools**")
    with action:
        if st.session_state.bd_route != "home":
            if st.button("All tools", key="top_home", use_container_width=True):
                go_to("home")
    st.divider()


def render_home() -> None:
    st.markdown("### Business development")
    st.title("Work on the document, not the formatting.")
    st.caption("Three focused tools for recurring bid-preparation work.")
    st.write("")

    for route, tool in TOOLS.items():
        number, content, open_col = st.columns([0.6, 5.5, 1.25], vertical_alignment="center")
        with number:
            st.caption(tool["number"])
        with content:
            st.subheader(tool["title"])
            st.caption(tool["meta"])
        with open_col:
            if st.button("Open  →", key=f"open_{route}", use_container_width=True):
                go_to(route)
        st.divider()

    if not gemini_is_configured():
        st.warning("Gemini API key is not configured for this deployment.")


def render_tool(route: str) -> None:
    tool = TOOLS[route]

    number, heading = st.columns([0.55, 6.5], vertical_alignment="bottom")
    with number:
        st.caption(tool["number"])
    with heading:
        st.title(tool["title"])
        st.caption(tool["meta"])

    st.write("")
    tool["runner"]()


render_topbar()

route = st.session_state.bd_route
if route == "home":
    render_home()
elif route in TOOLS:
    render_tool(route)
else:
    st.session_state.bd_route = "home"
    st.rerun()
