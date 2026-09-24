from pathlib import Path
import tempfile

import streamlit as st
from docx import Document
from deep_translator import GoogleTranslator

from .template_filler import fill_reference_table, fill_template_with_debug
from .utils import load_report_text


def run_app():
    if "field_values" not in st.session_state:
        st.session_state["field_values"] = None
    if "output_path_fr" not in st.session_state:
        st.session_state["output_path_fr"] = None
    if "output_path_en" not in st.session_state:
        st.session_state["output_path_en"] = None

    left, right = st.columns([1.75, 0.85], gap="large")

    with left:
        with st.container(border=True):
            st.markdown('<div class="panel-kicker">SOURCE REPORT</div>', unsafe_allow_html=True)
            st.markdown('<div class="panel-title">Drop in the project document</div>', unsafe_allow_html=True)
            st.markdown(
                '<div class="panel-help">Gemini extracts the relevant project information and maps it to the existing ACS reference template.</div>',
                unsafe_allow_html=True,
            )
            uploaded_report = st.file_uploader(
                "Project report",
                type=["docx", "pdf", "pptx", "txt"],
                key="ref_creator_report",
                label_visibility="collapsed",
            )

    with right:
        st.markdown(
            """
            <div class="side-summary">
                <div class="summary-label">DELIVERABLE</div>
                <h3>One reference, two languages</h3>
                <ul>
                    <li>French ACS reference sheet (VF)</li>
                    <li>English ACS reference sheet (VA)</li>
                    <li>Both delivered as editable Word files</li>
                </ul>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.write("")
        submit = st.button("Create reference", use_container_width=True, key="ref_creator_submit", type="primary")
        st.caption("Supported inputs: Word, PDF, PowerPoint and TXT.")

    if uploaded_report and "last_uploaded" in st.session_state:
        if uploaded_report.name != st.session_state["last_uploaded"]:
            st.session_state["generated"] = False

    st.session_state["last_uploaded"] = uploaded_report.name if uploaded_report else None

    TEMPLATE_PATH = "REF_creater/Référence Template.docx"

    def translate_docx(input_path, output_path, target_lang="en"):
        doc = Document(input_path)

        def translate_paragraph(para):
            text = para.text.strip()
            if text:
                try:
                    translated = GoogleTranslator(source="auto", target=target_lang).translate(text)
                    if para.runs:
                        para.runs[0].text = translated
                        for i in range(1, len(para.runs)):
                            para.runs[i].text = ""
                except Exception as e:
                    print("[Translation Error]", e)

        for para in doc.paragraphs:
            translate_paragraph(para)

        for table in doc.tables:
            for row in table.rows:
                for cell in row.cells:
                    for para in cell.paragraphs:
                        translate_paragraph(para)

        doc.save(output_path)

    if submit and not uploaded_report:
        st.warning("Upload a project report before creating the reference.")

    if submit and uploaded_report:
        report_text = load_report_text(uploaded_report)

        with st.spinner("Extracting project information with Gemini..."):
            st.session_state["field_values"] = fill_template_with_debug(TEMPLATE_PATH, report_text)

        with st.spinner("Generating the French reference..."):
            filled_doc = fill_reference_table(TEMPLATE_PATH, st.session_state["field_values"])

            mission_name = st.session_state["field_values"].get("Nom de la mission", "output").strip()
            mission_name_safe = "".join(c for c in mission_name if c.isalnum() or c in (" ", "_", "-")).rstrip()

            fr_name = f"{mission_name_safe}_ref_VF.docx"
            path_fr = Path(tempfile.gettempdir()) / fr_name
            filled_doc.save(path_fr)
            st.session_state["output_path_fr"] = path_fr

        with st.spinner("Creating the English version..."):
            en_name = f"{mission_name_safe}_ref_VA.docx"
            path_en = Path(tempfile.gettempdir()) / en_name
            translate_docx(path_fr, path_en, target_lang="en")
            st.session_state["output_path_en"] = path_en

        st.session_state["generated"] = True

    if st.session_state["output_path_fr"] or st.session_state["output_path_en"]:
        st.markdown('<div class="output-block"><div class="output-title">Reference files ready</div></div>', unsafe_allow_html=True)
        out_fr, out_en = st.columns(2, gap="medium")

        if st.session_state["output_path_fr"]:
            with out_fr:
                with open(st.session_state["output_path_fr"], "rb") as f:
                    st.download_button(
                        label="Download French version (VF)",
                        data=f,
                        file_name=st.session_state["output_path_fr"].name,
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                        use_container_width=True,
                    )

        if st.session_state["output_path_en"]:
            with out_en:
                with open(st.session_state["output_path_en"], "rb") as f:
                    st.download_button(
                        label="Download English version (VA)",
                        data=f,
                        file_name=st.session_state["output_path_en"].name,
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                        use_container_width=True,
                    )
