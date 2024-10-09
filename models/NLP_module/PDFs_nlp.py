import fitz
from models.NLP_module.normalise_texts import normalize_text2,normalize_text
from models.NLP_module.foot_notes import find_flexible_pattern_positions


def extract_text_by_page( pdf_path):
    # Open the PDF file
    doc = fitz.open(pdf_path)
    from models.NLP_module.normalise_texts import basic_normalization
    # List to hold text of every two pages
    # Open the PDF file
    doc = fitz.open(pdf_path)

    # List to hold text of each page
    text_by_page = []

    # Iterate over each page
    for page_num in range(len(doc)):
        # Get the page
        page = doc.load_page(page_num)

        # Extract text
        text = basic_normalization(page.get_text())

        # Append the text to the list
        text_by_page.append(text)

    # Return the list of text by page
    return text_by_page
def extract_sections_from_pdf(pdf_path, sections):
    # Open the PDF
    doc = fitz.open(pdf_path)

    # Extract all the text from the PDF
    text = ""
    for page_num in range(doc.page_count):
        page = doc[page_num]
        text += page.get_text()

    # Normalize the extracted text
    normalized_text = normalize_text2(text)

    # Find the positions of the section titles in the normalized text
    positions = find_flexible_pattern_positions(normalized_text, sections)

    # Filter out sections that weren't found
    positions = {k: v for k, v in positions.items() if v != -1}

    # Sort the sections by their positions in the text
    sorted_sections = sorted(positions, key=lambda x: positions[x])

    # Initialize the dictionary to hold section texts
    section_texts = {}

    # Extract the text for each section
    for i, section in enumerate(sorted_sections):
        start_pos = positions[section]
        if i < len(sorted_sections) - 1:
            end_pos = positions[sorted_sections[i + 1]]
        else:
            end_pos = len(normalized_text)

        section_text = normalized_text[start_pos:end_pos].strip()

        # Check if the section has text
        if not section_text or section_text == section:
            user_input = input(
                f"The section '{section}' was found but has no text associated with it. Do you want to include it? (yes/no): ")
            if user_input.lower() != 'yes':
                continue

        section_texts[section] = section_text

    return section_texts

def find_phrase_in_pdf(pdf_path, phrase):
    normalized_phrase = normalize_text(phrase)

    with fitz.open(pdf_path) as doc:
        for i, page in enumerate(doc):
            text = page.get_text("text")
            normalized_text = normalize_text(text)
            if normalized_phrase in normalized_text:

                return i + 1  # Page numbers are 1-based



    return None