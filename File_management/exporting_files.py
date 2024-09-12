import json
import zipfile

from docx import Document
doc = Document()
from Word_modules.Creating_docx import customize_doc_style

def export_results(structure, filename="output", export_to=['doc','html']):
    export_to = export_to or ['doc', 'html', 'md', 'json']

    # Export as HTML
    if "html" in export_to:
        with open(f"{filename}.html", "w", encoding='utf-8') as html_file:
            overarching_theme = structure.get('overarching_theme', 'No overarching theme')
            html_file.write(f"<h1>{overarching_theme}</h1>\n")

            for item in structure.get('structure', []):
                print(item)
                if isinstance(item, str):
                    item=eval(item)
                level =int(item['heading'].replace('h', '').strip())

                if isinstance(item, str):  # Check if item is a string (JSON)
                    item = json.loads(item)  # Parse the JSON string into a dictionary

                if 'heading' in item.keys() and 'paragraph_ids' in item.keys():
                    if 'topic_sentence' in item.keys():
                        quote_tag=f'h{str(level+1)}'
                        html_file.write(f"<{item['heading']}>{item['title']}</{item['heading']}\n")
                        for i in range(len(item['paragraph_ids'])):
                            topic=item['topic_sentence'][i]
                            paragraph=item['paragraph_ids'][i]

                            html_file.write(f"<{quote_tag}>{topic}</{quote_tag}>\n")
                            html_file.write(f"<p>{paragraph}</p>\n")

                else:
                        html_file.write(f"<{item['title']}>{item['title']}</{item['title']}\n")
                        for paragraph in item['paragraphs']:
                            html_file.write(f"<p>{paragraph}</p>\n")


    # Export as DOCX
    if "doc" in export_to:

        print('yes')
        customize_doc_style(doc, 'header here')

        # Add the overarching theme as a level-1 heading
        doc.add_heading(structure.get('overarching_theme', 'No overarching theme'), level=1)

        for item in structure.get('structure', []):
            if isinstance(item, str):  # Check if item is a string (JSON)
                item = json.loads(item)  # Parse the JSON string into a dictionary

            if 'heading' in item.keys() and 'title' in item.keys() :

                # Combine the heading level and title for the section
                heading_text = f"{item['title']}"
                # Add the heading to the doc with the title as level-2 heading (or the appropriate level)
                # Adjust 'level=2' if needed based on your structure
                level =int(item['heading'].replace('h', '').strip())
                doc.add_heading(heading_text, level=level)
                # Add the paragraphs
                if 'topic_sentence' in item:
                    for i in range(len(item['paragraph_ids'])):
                        topic = item['topic_sentence'][i]
                        paragraph = item['paragraph_ids'][i]

                        doc.add_heading(text=topic, level=level+1)
                        doc.add_paragraph(paragraph,style='Quote')
                else:
                    for paragraph in item['paragraphs']:
                        doc.add_paragraph(paragraph)

        # Save the document
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

from docx import Document
import json

def export_structure(data, formats):
    structure = data['themes']  # Extract the themes part from the data
    document_title = data.get('theme', 'Document')  # Use a generic title if the theme is not provided

    # Function to export to DOCX
    def write_to_docx(structure, filename):
        try:
            print(f"Processing DOCX export to {filename}...")
            doc = Document()
            customize_doc_style(doc, 'Thematic review raw')

            doc.add_heading(document_title, level=1)  # Use theme as the document title

            def add_to_docx(item):
                level = item.get('level', 'h1')  # Get the level (h1, h2, etc.)
                title = item.get('title', '')
                paragraphs = item.get('paragraphs', [])

                # Add title with the correct heading level
                if level == 'h1':
                    doc.add_heading(title, level=1)
                elif level == 'h2':
                    doc.add_heading(title, level=2)
                elif level == 'h3':
                    doc.add_heading(title, level=3)

                # Add paragraphs
                for para in paragraphs:
                    topic_sentence = para.get('topic sentence', '')
                    paragraph_text = para.get('paragraph', '')
                    blockquote = para.get('blockquote', False)

                    # Add topic sentence (if available)
                    if topic_sentence:
                        doc.add_paragraph(topic_sentence, style='IntenseQuote')

                    # Add paragraph text
                    if paragraph_text:
                        if blockquote:
                            paragraph = doc.add_paragraph(paragraph_text)
                            paragraph.style = 'Quote'  # Set style to Quote if blockquote is True
                        else:
                            doc.add_paragraph(paragraph_text)

                # Recursively process subheadings
                for subheading in item.get('subheadings', []):
                    add_to_docx(subheading)

            # Loop through all themes and headings
            for current_theme in structure:
                doc.add_heading(current_theme['theme'], level=1)  # Add theme as h1
                for heading in current_theme.get('headings', []):
                    add_to_docx(heading)

            doc.save(filename)
            print(f"Successfully saved DOCX to {filename}")
        except Exception as e:
            print(f"Error in DOCX export: {e}")

    # Function to export to Markdown
    def write_to_md(structure, filename):
        try:
            print(f"Processing Markdown export to {filename}...")

            def format_md(item):
                level = item.get('level', 'h1')
                title = item.get('title', '')
                paragraphs = item.get('paragraphs', [])

                md_text = f"{'#' * int(level[-1])} {title}\n\n"

                for para in paragraphs:
                    topic_sentence = para.get('topic sentence', '')
                    paragraph_text = para.get('paragraph', '')
                    blockquote = para.get('blockquote', False)

                    if topic_sentence:
                        md_text += f"**{topic_sentence}**\n\n"

                    if paragraph_text:
                        if blockquote:
                            md_text += f"> {paragraph_text}\n\n"
                        else:
                            md_text += f"{paragraph_text}\n\n"

                # Recursively process subheadings
                for subheading in item.get('subheadings', []):
                    md_text += format_md(subheading)

                return md_text

            md_content = ""
            for current_theme in structure:
                md_content += f"# {current_theme['theme']}\n\n"
                for heading in current_theme.get('headings', []):
                    md_content += format_md(heading)

            with open(filename, 'w') as f:
                f.write(md_content)
            print(f"Successfully saved Markdown to {filename}")
        except Exception as e:
            print(f"Error in Markdown export: {e}")

    # Function to export to HTML
    def write_to_html(structure, filename):
        try:
            print(f"Processing HTML export to {filename}...")

            def format_html(item):
                level = item.get('level', 'h1')
                title = item.get('title', '')
                paragraphs = item.get('paragraphs', [])

                html_text = f"<{level}>{title}</{level}>\n"

                for para in paragraphs:
                    topic_sentence = para.get('topic sentence', '')
                    paragraph_text = para.get('paragraph', '')
                    blockquote = para.get('blockquote', False)

                    if topic_sentence:
                        html_text += f"<strong>{topic_sentence}</strong>\n"

                    if paragraph_text:
                        if blockquote:
                            html_text += f"<blockquote>{paragraph_text}</blockquote>\n"
                        else:
                            html_text += f"<p>{paragraph_text}</p>\n"

                # Recursively process subheadings
                for subheading in item.get('subheadings', []):
                    html_text += format_html(subheading)

                return html_text

            html_content = ""
            for current_theme in structure:
                html_content += f"<h1>{current_theme['theme']}</h1>\n"
                for heading in current_theme.get('headings', []):
                    html_content += format_html(heading)

            with open(filename, 'w') as f:
                f.write(f"<html>\n<body>\n{html_content}\n</body>\n</html>")
            print(f"Successfully saved HTML to {filename}")
        except Exception as e:
            print(f"Error in HTML export: {e}")

    # Function to export to JSON
    def write_to_json(structure, filename):
        try:
            print(f"Processing JSON export to {filename}...")
            with open(filename, 'w') as f:
                json.dump(structure, f, indent=4)
            print(f"Successfully saved JSON to {filename}")
        except Exception as e:
            print(f"Error in JSON export: {e}")

    # Determine which formats to export
    for fmt in formats:
        if fmt == 'docx':
            write_to_docx(structure, 'output.docx')
        elif fmt == 'md':
            write_to_md(structure, 'output.md')
        elif fmt == 'html':
            write_to_html(structure, 'output.html')
        elif fmt == 'json':
            write_to_json(structure, 'output.json')
        else:
            print(f"Format {fmt} not supported.")
