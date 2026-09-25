import os
import tempfile
from pathlib import Path

import streamlit as st

from .docx_generator import fill_docx_template_by_labels
from .resume_extractor import extract_full_text
from .section_mapper import gpt_fill_as_dict


def run_app():
    cv_col, template_col, action_col = st.columns([2.35, 2.35, 1.3], gap="medium", vertical_alignment="bottom")

    with cv_col:
        uploaded_resumes = st.file_uploader(
            "Source CVs",
            type=["docx"],
            accept_multiple_files=True,
            key="template_adapter_resumes",
        )

    with template_col:
        uploaded_template = st.file_uploader(
            "Target Word template",
            type=["docx"],
            key="template_adapter_template",
        )

    with action_col:
        submit = st.button(
            "Format CVs",
            key="submit_cv_adapter",
            use_container_width=True,
            type="primary",
        )

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

    if generated_files:
        st.caption("Generated files")
        for item in generated_files:
            name_col, dl_col = st.columns([4.8, 1.2], vertical_alignment="center")
            with name_col:
                st.markdown(f"**{item['output_name']}**")
            with dl_col:
                with open(item["output_path"], "rb") as f:
                    st.download_button(
                        "Download",
                        data=f,
                        file_name=item["output_name"],
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                        use_container_width=True,
                    )
