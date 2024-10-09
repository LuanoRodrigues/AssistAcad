import requests
from lxml import etree

def extract_citations_grobid(pdf_path,file_name):
    url = 'http://localhost:8080/api/processFulltextDocument'

    # Open the PDF file in binary mode
    with open(pdf_path, 'rb') as pdf_file:
        response = requests.post(url, files={'input': pdf_file,"includeRawCitations":1,"segmentSentences":1})

    # Check if the request was successful
    if response.status_code == 200:
        with open(file_name, 'w', encoding='utf-8') as file:
            file.write(response.text)
        return f"Data saved to {file_name}"
    else:
        return f"Failed to extract citations: {response.status_code}"
def parse_grobid_xml_to_dict(xml_path):
    try:
        tree = etree.parse(xml_path)
        root = tree.getroot()
    except etree.XMLSyntaxError as e:
        print(f"Failed to parse XML: {e}")
        return None

    ns = {'tei': 'http://www.tei-c.org/ns/1.0'}
    parsed_results = {
        "Section_titles": [],
        "Paragraphs": {},
        "Reference_processing": {}
    }

    # Process each div for text and references
    for div in root.findall('.//tei:div', namespaces=ns):
        sentences = div.findall('.//tei:s', namespaces=ns)
        section_title = div.find('.//tei:head', namespaces=ns)
        section_key = section_title.text.strip() if section_title and section_title.text else "No Title"
        paragraph_texts = [s.text.strip() for s in sentences if s.text]
        parsed_results["Paragraphs"][section_key] = paragraph_texts
        # 3. Extract Footnotes
        footnotes_dict = {}

        # Define the namespace dictionary to use with the XML
        ns = {'tei': 'http://www.tei-c.org/ns/1.0'}

        # Dictionary to hold the notes with 'n' attribute as keys and text as values
        notes_dict = {}

        # Iterate through each note element in the XML
        for note in root.findall('.//tei:note[@place="foot"]', namespaces=ns):
            # Get the 'n' attribute
            n = note.get('n')

            # Get the text content of the note
            text = ''.join(note.itertext()).strip()
            # Check if 'n' is not None and add to dictionary
            if n:
                footnotes_dict[n] = text
        for i, s in enumerate(sentences):
            refs = s.findall('.//tei:ref[@type="bibr"]', namespaces=ns)
            for ref in refs:
                ref_text = ref.text.strip() if ref.text else ""
                # Capture the whole sentence as the preceding text
                preceding_text = s.text.strip() if s.text else ""
                # Optionally, include previous sentence for more context
                if i > 0 and sentences[i-1].text:
                    preceding_text = sentences[i-1].text.strip() + " " + preceding_text
                parsed_results["Reference_processing"][ref_text] = {
                    "preceding_text": preceding_text,
                    "footnote":footnotes_dict.get(ref_text,"")
                }

    return parsed_results
