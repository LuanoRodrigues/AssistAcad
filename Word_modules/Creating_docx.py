import json
import os

from docx.enum.style import WD_STYLE_TYPE
from docx.opc.oxml import qn
from docx.oxml import OxmlElement
from tqdm import tqdm

from word_data import  metadata
from datetime import datetime
from docx import Document
from docx.shared import Pt, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_PARAGRAPH_ALIGNMENT, WD_LINE_SPACING
from openai import OpenAI
from collections import defaultdict
# Uncomment if on Windows and docx2pdf is installed
from docx2pdf import convert

class Docx_creation():
    def __init__(self):
        pass

    def save_docx(self, directory_path,output_path):
        # Append ".json" to create the complete file path
        with open(output_path, "r",encoding="utf-8") as dt:
                data = json.load(dt)
        output_path = os.path.split(output_path)[-1]
        file_path = f"{directory_path}.docx"
        doc = Document()
        self.set_document_metadata(doc)
        self.add_cover_page(doc)
        # doc.add_heading("Introduction", level=1)
        # intro = doc.add_paragraph(introduction_content["Introduction"])
        # intro.alignment = WD_PARAGRAPH_ALIGNMENT.JUSTIFY
        # doc.add_paragraph()  # Optionally add extra spacing between sections
        # doc.add_page_break()

        self.customize_doc_style(doc)  # Apply the custom styles to the document

        chapter_name = list(data.keys())[0]
        chapter_title = data[chapter_name]["title"]

        for chapter_section in data[chapter_name]["Sections"]:


            section_title = chapter_section["title"]
            section_intro =  chapter_section["introduction"]
            section_keywords = chapter_section["keywords"]
            subsections = chapter_section["Subsections"]

            # Use 'Heading 1' for main headings
            doc.add_heading(chapter_title.strip().title(), level=1).style = 'Heading 1'
            doc.add_heading(section_title.strip().title(), level=2).style = 'Heading 2'

            intro_text = doc.add_paragraph(section_intro)
            intro_text.alignment = WD_PARAGRAPH_ALIGNMENT.JUSTIFY

            with tqdm(chapter_section["Subsections"], desc=f'Processing {section_title}') as pbar:
                for n, subsection in enumerate(pbar):
                    subsection_title = subsection["title"].strip().title()
                    sub_text = subsection.get("bodyText").strip() if subsection.get("bodyText") else ""
                    doc.add_heading(subsection_title, level=3).style = 'Heading 3'

                    subsection_ref = "\n".join(subsection["references"])
                    print("subsection ref:", subsection_ref)



                    body_text = doc.add_paragraph(sub_text)
                    body_text.alignment = WD_PARAGRAPH_ALIGNMENT.JUSTIFY
                    doc.add_heading("References", level=2).style = 'Heading 3'
                    ref_text = doc.add_paragraph(subsection_ref)
                    ref_text.alignment = WD_PARAGRAPH_ALIGNMENT.JUSTIFY





            doc.add_page_break()

        doc.save(file_path)
        print("the docx file has been saved at {}\n".format(file_path))
        convert(file_path, file_path.replace(".docx", ".pdf"))
        print("the pdf file has been saved at {}\n".format(file_path.replace(".docx", ".pdf")))


    def create_scientific_template(self, doc):
        # Set up document styles (fonts, sizes, line spacing)
        styles = doc.styles
        normal = styles['Normal']
        normal.font.name = 'Times New Roman'
        normal.font.size = Pt(12)

        for i in range(1, 4):  # Create Heading styles
            heading_style = styles.add_style(f'Heading {i}', WD_STYLE_TYPE.PARAGRAPH)
            heading_style.font.name = 'Times New Roman'
            heading_style.font.size = Pt(12 + 2 * (3 - i))
            heading_style.font.bold = True
            heading_style.paragraph_format.space_after = Pt(6)

        # Create a title page
        doc.add_heading('Research Title', 0)
        doc.add_paragraph('Author Name\nInstitution\nDate').alignment = WD_ALIGN_PARAGRAPH.CENTER
        doc.add_page_break()

        # Add an abstract
        doc.add_heading('Abstract', level=1)
        doc.add_paragraph('This is a placeholder for the abstract.')

        # Add keywords
        doc.add_paragraph('Keywords: keyword1, keyword2, keyword3')

        # Introduction
        doc.add_heading('Introduction', level=1)
        doc.add_paragraph('This is a placeholder for the introduction.')

        # Methodology
        doc.add_heading('Methodology', level=1)
        doc.add_paragraph('This is a placeholder for the methodology.')

        # Results
        doc.add_heading('Results', level=1)
        doc.add_paragraph('This is a placeholder for the results.')

        # Discussion
        doc.add_heading('Discussion', level=1)
        doc.add_paragraph('This is a placeholder for the discussion.')

        # References
        doc.add_heading('References', level=1)
        doc.add_paragraph('This is a placeholder for the references.')

        # Appendices
        doc.add_heading('Appendices', level=1)
        doc.add_paragraph('This is a placeholder for the appendices.')

    def set_document_metadata(self, doc):
        """
        Set the document's core properties (metadata).
        :param doc: The Document object.
        :param metadata: A dictionary containing metadata fields.
        """
        core_properties = doc.core_properties
        core_properties.author = metadata.get('author', 'Unknown Author')
        core_properties.title = metadata.get('title', 'Untitled Document')
        core_properties.subject = metadata.get('subject', '')
        core_properties.keywords = metadata.get('keywords', '')
        core_properties.comments = metadata.get('comments', '')
        core_properties.category = metadata.get('category', 'General')
        core_properties.version = metadata.get('version', '1.0')
        core_properties.language = metadata.get('language', 'en-US')
        core_properties.created = metadata.get('created', datetime.now())
        core_properties.modified = metadata.get('modified', datetime.now())
        # Add any additional metadata as needed


    def add_cover_page(self, doc):
        """
        Add a cover page to the document.
        :param doc: The Document object.
        :param metadata: A dictionary containing metadata fields.
        """
        doc.add_paragraph(metadata['title'], style='Title').alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
        doc.add_paragraph('\n' * 5)  # Adjust spacing as needed
        doc.add_paragraph(metadata['author'], style='Subtitle').alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
        # Ensure date is a datetime object for formatting
        date_str = metadata['created'].strftime('%B %d, %Y') if isinstance(metadata['created'], datetime) else metadata[
            'created']
        doc.add_paragraph('\n' * 13)  # Move date & city to bottom
        doc.add_paragraph(f"{date_str}, {metadata['city']}", style='BodyText').alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
        doc.add_page_break()


    def customize_doc_style(self, doc):

        # Customize 'Normal' style
        normal_style = doc.styles['Normal']
        normal_style.font.name = 'Arial'
        normal_style.font.size = Pt(12)
        normal_style.paragraph_format.line_spacing = Pt(18)  # Set 1.5 line spacing
        normal_style.paragraph_format.space_after = Pt(6)


        # Customize 'Heading 1'
        h1_style = doc.styles['Heading 1']
        h1_style.font.name = 'Times New Roman'
        h1_style.font.size = Pt(14)  # Slightly larger than body text
        h1_style.font.bold = True
        h1_style.paragraph_format.space_after = Pt(12)  # Space after heading
        h1_style.paragraph_format.space_before = Pt(12)  # Space before heading
        h1_style.paragraph_format.line_spacing = Pt(18) #Pt(24)  # Double spacing

        # Customize 'Heading 2'
        h2_style = doc.styles['Heading 2']
        h2_style.font.name = 'Times New Roman'
        h2_style.font.size = Pt(14)
        h2_style.font.bold = True
        h2_style.paragraph_format.space_after = Pt(8)
        normal_style.paragraph_format.line_spacing = Pt(18)  # Set 1.5 line spacing


        # Customize 'Heading 3'
        h3_style = doc.styles['Heading 3']
        h3_style.font.name = 'Times New Roman'
        h3_style.font.size = Pt(12)
        h3_style.font.bold = True
        h3_style.paragraph_format.space_after = Pt(6)
        normal_style.paragraph_format.line_spacing = Pt(18)  # Set 1.5 line spacing

        # Customize 'Heading 4'
        if 'Heading 4' not in doc.styles:
            h4_style = doc.styles.add_style('Heading 4', WD_STYLE_TYPE.PARAGRAPH)
        else:
            h4_style = doc.styles['Heading 4']
        h4_style.font.name = 'Times New Roman'
        h4_style.font.size = Pt(12)
        h4_style.font.bold = True
        h4_style.paragraph_format.space_after = Pt(6)
        normal_style.paragraph_format.line_spacing = Pt(18)  # Set 1.5 line spacing


        # Customize 'Abstract' style for abstract sections
        if 'Abstract' not in doc.styles:
            abstract_style = doc.styles.add_style('Abstract', WD_STYLE_TYPE.PARAGRAPH)
        else:
            abstract_style = doc.styles['Abstract']
        abstract_style.font.name = 'Arial'
        abstract_style.font.size = Pt(12)
        abstract_style.font.italic = True
        abstract_style.paragraph_format.space_after = Pt(12)
        abstract_style.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY

        # Customize 'Title' style
        title_style = doc.styles['Title']
        title_style.font.name = 'Arial'
        title_style.font.size = Pt(24)
        title_style.font.bold = True
        title_style.paragraph_format.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER

        # Customize 'Subtitle' style
        subtitle_style = doc.styles['Subtitle']
        subtitle_style.font.name = 'Arial'
        subtitle_style.font.size = Pt(18)
        subtitle_style.font.bold = False
        subtitle_style.paragraph_format.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
        # Customize 'List Bullet' style
        list_bullet_style = doc.styles['List Bullet']
        list_bullet_style.font.name = 'Arial'
        list_bullet_style.font.size = Pt(12)

        # Customize 'List Number' style
        list_number_style = doc.styles['List Number']
        list_number_style.font.name = 'Arial'
        list_number_style.font.size = Pt(12)

        # Customize 'Caption' style for figures and tables
        caption_style = doc.styles['Caption']
        caption_style.font.name = 'Arial'
        caption_style.font.size = Pt(12)
        caption_style.font.bold = True
        caption_style.font.italic = True
        caption_style.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
        # Customize Header style
        header = doc.sections[0].header
        paragraph = header.paragraphs[0]
        paragraph.text = "Your Header Text Here"
        paragraph.style = doc.styles['Header']
        paragraph.style.font.size = Pt(12)
        paragraph.style.font.name = 'Arial'
        paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER

        # Customize Footer style
        footer = doc.sections[0].footer
        paragraph = footer.paragraphs[0]
        paragraph.text = "Your Footer Text Here - Page "  # Page number added next
        paragraph.style = doc.styles['Footer']
        paragraph.style.font.size = Pt(12)
        paragraph.style.font.name = 'Arial'
        paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER

        # # Add page number to the footer
        # fldSimple = OxmlElement('w:fldSimple')
        # fldSimple.set(qn('w:instr'), 'PAGE')
        # run = paragraph.add_run()
        # run._r.append(fldSimple)


# docx = Docx_creation()
# docx.save_docx(directory_path="Cyber Evidence", output_path="books_data/Cyber Evidence/Cyber evidence.json")
from docx import Document
from bs4 import BeautifulSoup
def create_word_document_from_html(html_content, output_path):
    # Initialize a new Word document
    doc = Document()

    # Parse HTML content
    soup = BeautifulSoup(html_content, 'html.parser')

    # Extract headings and paragraphs
    headings = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
    paragraphs = soup.find_all('p')

    # Add headings to the document
    for heading in headings:
        text = heading.get_text()
        level = int(heading.name[1])  # Extract heading level from tag name (e.g., 'h1' -> level 1)
        doc.add_heading(text, level=level)

    # Add paragraphs to the document
    for paragraph in paragraphs:
        text = paragraph.get_text()
        doc.add_paragraph(text)

    # Save the document
    doc.save(output_path)

#
# output_path = "output.docx"
# create_word_document_from_html(html_content, output_path)

def add_texts_to_html(html_path, headings_texts_dict, start_from=None):
    with open(html_path, 'r') as file:
        html_content = file.readlines()

    updated_html_content = []
    processing = not start_from  # If start_from is None, start processing immediately

    for line in html_content:
        if not processing:
            if start_from in line:
                processing = True
            else:
                updated_html_content.append(line.strip() + '\n')
                continue

        for heading, text in headings_texts_dict.items():
            if heading in line:
                updated_html_content.append(line.strip() + '\n')
                updated_html_content.append(text.strip() + '\n')
                break
        else:
            updated_html_content.append(line.strip() + '\n')

    with open(html_path, 'w') as file:
        file.writelines(updated_html_content)

# Define headings and texts
headings_texts = {
    "<h2>Chapter 1: Introduction</h2>": "<p>This is the detailed introduction to our sample document.</p>",
    "<h2>Chapter 3: Conclusion</h2>": "<p>This section summarizes the key points of our document.</p>"
}

# Update the HTML file
html_file_path = 'books_data/example.html'
add_texts_to_html(html_file_path, headings_texts, start_from="<h2>Chapter 2:")

# Read and display the updated HTML file
with open(html_file_path, 'r') as file:
    updated_html_content = file.read()

print(updated_html_content)
