import time
from gemini_client import generate_text, parse_json_object


def extract_field(report_text, fields):
    def split_text(text, max_tokens=3000):
        # The original implementation used words as a lightweight token proxy.
        paragraphs = text.split("\n")
        chunks, current_chunk = [], []
        current_length = 0

        for para in paragraphs:
            length = len(para.split())
            if current_length + length > max_tokens and current_chunk:
                chunks.append("\n".join(current_chunk))
                current_chunk = [para]
                current_length = length
            else:
                current_chunk.append(para)
                current_length += length

        if current_chunk:
            chunks.append("\n".join(current_chunk))

        return chunks

    def build_prompt(text_chunk, requested_fields):
        prompt = (
            "Tu es un expert analyste. Lis attentivement le rapport suivant et remplis les champs demandés.\n"
            "Chaque réponse doit être détaillée, bien rédigée et autonome.\n"
            "Les champs 'Services fournis' et 'Résultats issus du projet' doivent commencer par une phrase "
            "d’introduction complète (une ou deux lignes), puis continuer avec des puces '•' bien développées.\n"
            "N'invente aucun fait, chiffre, nom, date ou résultat absent du rapport. Quand une information n'est "
            "pas identifiable avec suffisamment de confiance, renvoie une chaîne vide pour ce champ.\n\n"
            "Champs :\n"
        )

        for field in requested_fields:
            prompt += f"- {field}\n"

        prompt += (
            "\nRéponds uniquement avec un objet JSON valide. Utilise exactement les noms de champs ci-dessus "
            "comme clés et du texte (chaîne) comme valeur. Aucun commentaire avant ou après le JSON.\n\n"
            f"Rapport :\n{text_chunk}"
        )
        return prompt

    chunks = split_text(report_text)
    final_data = {field: "" for field in fields}

    for chunk in chunks:
        prompt = build_prompt(chunk, fields)
        try:
            content = generate_text(
                prompt,
                system_instruction=(
                    "Tu extrais fidèlement des informations de rapports de projet pour remplir des fiches de référence."
                ),
                max_output_tokens=5000,
            )
            chunk_data = parse_json_object(content)
            for field in fields:
                value = chunk_data.get(field)
                if not final_data[field] and isinstance(value, str) and value.strip():
                    final_data[field] = value.strip()
        except Exception as e:
            print(f"Gemini extraction error: {e}\nPrompt:\n{prompt[:1000]}...")
        time.sleep(0.5)

    return final_data


def force_field_completion(fields):
    # Keep the original fallbacks used by the application.
    if not fields["Catégorie de service"]:
        fields["Catégorie de service"] = "Études de marché"
    if not fields["Services fournis"]:
        fields["Services fournis"] = "Analyse de marché, entretiens avec les acteurs clés, recommandations"
    if not fields["Résultats issus du projet"]:
        fields["Résultats issus du projet"] = "Identification d’opportunités de financement vert et recommandations stratégiques"
    return fields
