from gemini_client import generate_text, parse_json_object


def semantic_map_sections(resume_sections, template_text):
    """Uses Gemini to understand and map sections semantically."""
    resume_blocks = "\n\n".join([f"[{i}] {s[:500]}" for i, s in enumerate(resume_sections)])

    prompt = f"""
You are a document understanding assistant. The user gives you:

1. A resume split into sections (with indices)
2. A resume template in raw text

Your task is to match sections from the resume to the appropriate part of the template, based on meaning and content (not just the title).
Return only a valid JSON object that maps template section descriptions to resume section indices.

### RESUME SECTIONS:
{resume_blocks}

### TEMPLATE:
{template_text}

Example:
{{
  "Education": 1,
  "Work Experience": 0,
  "Skills": 2
}}
"""

    return parse_json_object(generate_text(prompt))


def gpt_fill_template_as_text(template_text, resume_text):
    # Function name kept for backwards compatibility with the existing app.
    prompt = f"""
You are a document assistant. Fill a resume template using only real information from the resume.
Do not invent missing facts.
Return the full filled-in resume as plain text, replacing placeholders or gaps where information is available.

### TEMPLATE:
{template_text}

### RESUME INFO:
{resume_text}
"""
    return generate_text(prompt)


def gpt_fill_as_dict(template_text, resume_text):
    # Function name kept so the rest of the project does not need to change.
    prompt = f"""
You are a CV filling assistant.

You are given:
1. A CV template with labels and instructions (text within curly braces {{}}).
2. A resume as raw text.

Your task:
- Return a JSON object with keys exactly as they appear in the template (including instructions in curly braces {{}}), except always ignore the "Certification" section.
- Each key's value must contain only information supported by the resume.
- Do not invent dates, employers, projects, qualifications or responsibilities.
- For tables, provide arrays of arrays, with the headers included as the first array.
- Use strings for normal text fields.

### TEMPLATE:
{template_text}

### RESUME:
{resume_text}

Return only valid JSON. No Markdown fences and no additional text.
"""

    return parse_json_object(generate_text(prompt, max_output_tokens=12000))
