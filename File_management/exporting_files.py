import json
from Word_modules.Creating_docx import customize_doc_style
def export_results(structure, filename="output", export_to=None):
    export_to = export_to or ['doc', 'html', 'md', 'json']

    # Export as HTML
    if "html" in export_to:
        with open(f"{filename}.html", "w", encoding='utf-8') as html_file:
            overarching_theme = structure.get('overarching_theme', 'No overarching theme')
            html_file.write(f"<h1>{overarching_theme}</h1>\n")

            for item in structure.get('structure', []):
                if isinstance(item, str):  # Check if item is a string (JSON)
                    item = json.loads(item)  # Parse the JSON string into a dictionary

                if 'heading' in item and 'paragraphs' in item:
                    html_file.write(f"<h2>{item['heading']}</h2>\n")
                    for paragraph in item['paragraphs']:
                        html_file.write(f"<p>{paragraph}</p>\n")

    # Export as DOCX
    if "doc" in export_to:
        from docx import Document
        doc = Document()
        customize_doc_style(doc,'header here')
        doc.add_heading(structure.get('overarching_theme', 'No overarching theme'), level=1)

        for item in structure.get('structure', []):
            if isinstance(item, str):  # Check if item is a string (JSON)
                item = json.loads(item)  # Parse the JSON string into a dictionary

            if 'heading' in item and 'paragraphs' in item:
                doc.add_heading(item['heading'], level=2)
                for paragraph in item['paragraphs']:
                    doc.add_paragraph(paragraph)

        doc.save(f"{filename}.docx")

    # Export as Markdown (MD)
    if "md" in export_to:
        with open(f"{filename}.md", "w", encoding='utf-8') as md_file:
            overarching_theme = structure.get('overarching_theme', 'No overarching theme')
            md_file.write(f"# {overarching_theme}\n\n")

            for item in structure.get('structure', []):
                if isinstance(item, str):  # Check if item is a string (JSON)
                    item = json.loads(item)  # Parse the JSON string into a dictionary

                if 'heading' in item and 'paragraphs' in item:
                    md_file.write(f"## {item['heading']}\n\n")
                    for paragraph in item['paragraphs']:
                        md_file.write(f"{paragraph}\n\n")

    # Export as JSON
    if "json" in export_to:
        with open(f"{filename}.json", "w", encoding='utf-8') as json_file:
            json.dump(structure, json_file, ensure_ascii=False, indent=4)
