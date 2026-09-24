import os
import tempfile
from pathlib import Path

import streamlit as st

from .docx_generator import fill_docx_template_by_labels
from .resume_extractor import extract_full_text
from .section_mapper import gpt_fill_as_dict


def run_app():
    left, right = st.columns([1.75, 0.85], gap="large")

    with left:
        with st.container(border=True):
            st.markdown('<div class="panel-kicker">INPUTS</div>', unsafe_allow_html=True)
            st.markdown('<div class="panel-title">Source CVs + target format</div>', unsafe_allow_html=True)
            st.markdown(
                '<div class="panel-help">Upload the consultant CVs on the left and the Word template they should be reformatted into on the right.</div>',
                unsafe_allow_html=True,
            )
            cv_col, template_col = st.columns(2, gap="medium")
            with cv_col:
                uploaded_resumes = st.file_uploader(
                    "Source CVs (.docx)",
                    type=["docx"],
                    accept_multiple_files=True,
                    key="template_adapter_resumes",
                )
            with template_col:
                uploaded_template = st.file_uploader(
                    "Target template (.docx)",
                    type=["docx"],
                    key="template_adapter_template",
                )

    with right:
        st.markdown(
            """
            <div class="side-summary">
                <div class="summary-label">MAPPING</div>
                <h3>Preserve content, change structure</h3>
                <ul>
                    <li>Gemini identifies equivalent CV fields.</li>
                    <li>The target template controls the final structure.</li>
                    <li>One new Word file is created per consultant.</li>
                </ul>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.write("")
        submit = st.button("Build formatted CVs", key="submit_cv_adapter", use_container_width=True, type="primary")
        st.caption("The original CVs and template are never overwritten.")

    if submit and (not uploaded_resumes or not uploaded_template):
        st.warning("Upload at least one CV and one Word template before starting.")

    generated_files = []

    if submit and uploaded_resumes and uploaded_template:
        with st.spinner("Reading the target CV template..."):
            template_tmp = tempfile.NamedTemporaryFile(delete=False, suffix=Path(uploaded_template.name).suffix)
            template_tmp.write(uploaded_template.getbuffer())
            template_tmp.flush()
            template_path = template_tmp.name
            template_raw_text = extract_full_text(template_path)

        for uploaded_resume in uploaded_resumes:
            with st.spinner(f"Mapping {uploaded_resume.name} to the template..."):
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

    if generated_files:
        st.markdown('<div class="output-block"><div class="output-title">Formatted CVs ready</div></div>', unsafe_allow_html=True)
        cols = st.columns(min(3, len(generated_files)), gap="medium")
        for index, item in enumerate(generated_files):
            with cols[index % len(cols)]:
                with open(item["output_path"], "rb") as f:
                    st.download_button(
                        label=item["output_name"],
                        data=f,
                        file_name=item["output_name"],
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                        use_container_width=True,
                    )

        with st.expander("Technical details", expanded=False):
            st.caption("Debug information for verification. It does not affect the generated documents.")
            for item in generated_files:
                st.markdown(f"**{item['output_name']}**")
                with st.expander("Resume extracted text"):
                    st.text(item["resume_text"])
                with st.expander("Template raw text"):
                    st.text(item["template_raw_text"])
                with st.expander("Gemini mapped fields"):
                    st.json(item["filled_dict"])
