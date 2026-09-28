import os
import tempfile
from pathlib import Path

import streamlit as st

from .docx_generator import fill_docx_template_by_labels
from .resume_extractor import extract_full_text
from .section_mapper import gpt_fill_as_dict


def run_app():
    input_pane, divider, output_pane = st.columns([1.42, 0.025, 0.78], gap="medium")

    with input_pane:
        st.markdown('<div class="pane-label">Input</div>', unsafe_allow_html=True)

        cv_col, template_col = st.columns([1.0, 1.0], gap="large")
        with cv_col:
            st.markdown('<div class="field-name">Source CVs</div>', unsafe_allow_html=True)
            uploaded_resumes = st.file_uploader(
                "Source CVs",
                type=["docx"],
                accept_multiple_files=True,
                key="template_adapter_resumes",
                label_visibility="collapsed",
            )
            if uploaded_resumes:
                st.markdown(
                    f'<div class="selection-note">{len(uploaded_resumes)} file(s) selected</div>',
                    unsafe_allow_html=True,
                )
            else:
                st.markdown('<div class="selection-note">No files selected</div>', unsafe_allow_html=True)

        with template_col:
            st.markdown('<div class="field-name">Word template</div>', unsafe_allow_html=True)
            uploaded_template = st.file_uploader(
                "Word template",
                type=["docx"],
                key="template_adapter_template",
                label_visibility="collapsed",
            )
            st.markdown(
                f'<div class="selection-note">{uploaded_template.name if uploaded_template else "No file selected"}</div>',
                unsafe_allow_html=True,
            )

        st.markdown('<div class="action-row-spacer"></div>', unsafe_allow_html=True)
        submit = st.button("Format CVs", key="submit_cv_adapter", type="primary")

    with divider:
        st.markdown('<div class="split-rule"></div>', unsafe_allow_html=True)

    if submit and (not uploaded_resumes or not uploaded_template):
        st.warning("Upload at least one CV and one Word template first.")

    generated_files = []

    if submit and uploaded_resumes and uploaded_template:
        with st.spinner("Reading template..."):
            template_tmp = tempfile.NamedTemporaryFile(delete=False, suffix=Path(uploaded_template.name).suffix)
            template_tmp.write(uploaded_template.getbuffer())
            template_tmp.flush()
            template_path = template_tmp.name
            template_raw_text = extract_full_text(template_path)

        for uploaded_resume in uploaded_resumes:
            with st.spinner(f"Formatting {uploaded_resume.name}..."):
                resume_tmp = tempfile.NamedTemporaryFile(delete=False, suffix=Path(uploaded_resume.name).suffix)
                resume_tmp.write(uploaded_resume.getbuffer())
                resume_tmp.flush()
                resume_path = resume_tmp.name

                output_name = f"UPDATED_{Path(uploaded_resume.name).stem}.docx"
                output_path = os.path.join(tempfile.gettempdir(), output_name)

                resume_text = extract_full_text(resume_path)
                filled_dict = gpt_fill_as_dict(template_raw_text, resume_text)
                fill_docx_template_by_labels(template_path, filled_dict, output_path)

                generated_files.append(
                    {
                        "output_name": output_name,
                        "output_path": output_path,
                        "resume_text": resume_text,
                        "template_raw_text": template_raw_text,
                        "filled_dict": filled_dict,
                    }
                )

    with output_pane:
        st.markdown('<div class="results-head">Output</div>', unsafe_allow_html=True)

        if not generated_files:
            st.markdown('<div class="results-empty">No generated files yet.</div>', unsafe_allow_html=True)
        else:
            for item in generated_files:
                name_col, dl_col = st.columns([3.4, 1.0], vertical_alignment="center")
                with name_col:
                    st.markdown(
                        f'<div class="result-row"><div class="result-title">{item["output_name"]}</div>'
                        f'<div class="result-meta">Word document</div></div>',
                        unsafe_allow_html=True,
                    )
                with dl_col:
                    with open(item["output_path"], "rb") as f:
                        st.download_button(
                            "Download",
                            data=f,
                            file_name=item["output_name"],
                            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                        )
