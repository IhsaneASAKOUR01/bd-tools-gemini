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
    brand, filler, state = st.columns([2.4, 6.2, 1.4], vertical_alignment="center")
    with brand:
        logo, name = st.columns([0.32, 1.7], vertical_alignment="center")
        with logo:
            st.image(str(ROOT / "logo.png"), width=30)
        with name:
            st.markdown("**BD Tools**")
    with state:
        if st.session_state.bd_route == "home" and gemini_is_configured():
            st.caption("Gemini ready")
    st.divider()


def render_home() -> None:
    st.markdown("### Business development")
    st.title("Work on the document, not the formatting.")
    st.caption("Three focused tools for recurring bid-preparation work.")
    st.write("")

    for route, tool in TOOLS.items():
        number, content, open_col = st.columns([0.55, 6.2, 1.15], vertical_alignment="center")
        with number:
            st.caption(tool["number"])
        with content:
            st.subheader(tool["title"])
            st.caption(tool["meta"])
        with open_col:
            if st.button("Open →", key=f"open_{route}"):
                go_to(route)
        st.divider()

    if not gemini_is_configured():
        st.warning("Gemini API key is not configured for this deployment.")


def render_tool(route: str) -> None:
    tool = TOOLS[route]

    # Keep every workbench compact: the center column is intentionally narrow.
    left_gutter, workbench, right_gutter = st.columns([1.55, 6.9, 1.55])
    with workbench:
        back_col, title_col = st.columns([1.15, 5.85], vertical_alignment="center")
        with back_col:
            if st.button("← Tools", key="tool_back"):
                go_to("home")
        with title_col:
            st.markdown(f"### {tool['title']}")

        st.markdown('<div class="workbench-rule"></div>', unsafe_allow_html=True)
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
