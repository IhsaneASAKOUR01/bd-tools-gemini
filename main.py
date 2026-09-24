from pathlib import Path

import streamlit as st

from CVs_REFs_adapter.app import run_app as run_cvs_refs_adapter
from REF_creater.app import run_app as run_ref_creator
from CVs_adapter.app import run_app as run_cvs_adapter


ROOT = Path(__file__).resolve().parent

st.set_page_config(
    page_title="BD Workspace | Africa Climate Solutions",
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
        "label": "Tender tailoring",
        "title": "Adapt CVs & references",
        "description": "Tailor existing consultant CVs and project references to a specific opportunity.",
        "detail": "Word in · Gemini-assisted tailoring · Word out",
        "runner": run_cvs_refs_adapter,
    },
    "reference": {
        "number": "02",
        "label": "Reference production",
        "title": "Create a project reference",
        "description": "Turn a report into a structured ACS project reference in French and English.",
        "detail": "PDF / Word / PPT in · structured extraction · bilingual Word out",
        "runner": run_ref_creator,
    },
    "cv_template": {
        "number": "03",
        "label": "CV formatting",
        "title": "Move CVs into a template",
        "description": "Map one or more source CVs into a target Word CV template automatically.",
        "detail": "CVs + template in · field mapping · formatted CVs out",
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
    status_class = "ok" if gemini_is_configured() else "warn"
    status_text = "Gemini ready" if gemini_is_configured() else "Gemini key missing"

    left, right = st.columns([5, 1.25], vertical_alignment="center")
    with left:
        brand_a, brand_b = st.columns([0.42, 4.58], vertical_alignment="center")
        with brand_a:
            st.image(str(ROOT / "logo.png"), width=42)
        with brand_b:
            st.markdown(
                """
                <div class="brand-lockup">
                    <div class="brand-name">BD Workspace</div>
                    <div class="brand-org">Africa Climate Solutions</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
    with right:
        st.markdown(
            f'<div class="api-chip {status_class}"><span></span>{status_text}</div>',
            unsafe_allow_html=True,
        )

    st.markdown('<div class="top-rule"></div>', unsafe_allow_html=True)


def render_home() -> None:
    st.markdown(
        """
        <section class="home-intro">
            <div class="home-kicker">BUSINESS DEVELOPMENT</div>
            <h1>What do you want to produce?</h1>
            <p>Choose a workflow. Each tool opens in its own workspace — no tabs, no side menu.</p>
        </section>
        """,
        unsafe_allow_html=True,
    )

    cols = st.columns(3, gap="large")
    for col, (route, tool) in zip(cols, TOOLS.items()):
        with col:
            st.markdown(
                f"""
                <article class="launch-card">
                    <div class="launch-topline">
                        <span class="launch-number">{tool['number']}</span>
                        <span class="launch-label">{tool['label']}</span>
                    </div>
                    <h2>{tool['title']}</h2>
                    <p>{tool['description']}</p>
                    <div class="launch-detail">{tool['detail']}</div>
                </article>
                """,
                unsafe_allow_html=True,
            )
            if st.button("Open workspace  →", key=f"open_{route}", use_container_width=True):
                go_to(route)

    st.markdown(
        """
        <div class="home-note">
            <strong>How it works:</strong> source documents stay unchanged. Each workflow generates new Word files for download.
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_tool(route: str) -> None:
    tool = TOOLS[route]
    nav_col, blank_col = st.columns([1.25, 5])
    with nav_col:
        if st.button("←  Workspace", key="back_home", use_container_width=True):
            go_to("home")

    st.markdown(
        f"""
        <section class="workbench-head">
            <div class="workbench-index">{tool['number']}</div>
            <div>
                <div class="workbench-kicker">{tool['label'].upper()}</div>
                <h1>{tool['title']}</h1>
                <p>{tool['description']}</p>
            </div>
        </section>
        """,
        unsafe_allow_html=True,
    )

    tool["runner"]()


render_topbar()

if st.session_state.bd_route == "home":
    render_home()
elif st.session_state.bd_route in TOOLS:
    render_tool(st.session_state.bd_route)
else:
    st.session_state.bd_route = "home"
    st.rerun()
