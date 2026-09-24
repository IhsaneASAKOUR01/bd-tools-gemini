# Adapt content to align with an AO without changing the original project framing.
from gemini_client import generate_text


def adapt_section(section_name, original_text, ao_title):
    if not original_text.strip():
        return original_text

    bullet_hint = ""
    if section_name.lower() in ["services fournis", "résultats issus du projet"]:
        bullet_hint = (
            "You may use bullet points if it helps clarify the structure of the content, "
            "but only when it makes sense — do not force them.\n"
        )

    prompt = (
        f"You are adapting the following section from a past project titled '{section_name}'.\n"
        f"{bullet_hint}"
        "The adaptation should preserve the original project identity and narrative.\n"
        "Do not mention the new AO explicitly inside the content.\n"
        "Ensure the result is standalone, natural, and aligned with the AO without naming it.\n"
        f"\nHere is the original content:\n{original_text}\n\n"
        "Adapt it as instructed and return only the rewritten content — no headers, no tags, no extra markers.\n"
        "Keep a neutral tone — do not use marketing or promotional language.\n"
        f"Your goal is to rephrase the text very slightly to subtly highlight its relevance to calls like: '{ao_title}', without changing the substance.\n"
        "Do not add new content or invent ideas. Preserve the original project identity, structure, and facts.\n"
        "Return only the adapted version — no headers, no commentary, no formatting instructions."
    )

    return generate_text(
        prompt,
        system_instruction=(
            "You are a proposal writer adapting past project descriptions to highlight their "
            "relevance to a new AO without altering the original framing."
        ),
    )


def adapt_all_sections(sections_list, ao_title):
    adapted_refs = []
    for sections in sections_list:
        adapted = {}
        for key, value in sections.items():
            adapted[key] = adapt_section(key, value, ao_title)
        adapted_refs.append(adapted)
    return adapted_refs
