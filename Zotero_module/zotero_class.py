import hashlib
import json
import os
import fitz
import re
import ast
import time
import pickle
import urllib
from pathlib import Path
import math
from collections import defaultdict

from nibabel.brikhead import filepath
from openai import files
from sklearn.utils.multiclass import type_of_target
from sympy import pprint
from tests.test_conversions import test_hn_atx_headings

from Vector_Database.qdrant_handler import QdrantHandler
from qdrant_client.http.exceptions import UnexpectedResponse
from File_management.exporting_files import export_data, convert_zotero_to_md
from Vector_Database.embedding_handler import query_with_history,check_existing_query
from Vector_Database.qdrant_handler import write_and_export_sections, QdrantHandler
from NLP_module.foot_notes import extract_text_with_numbers_from_pdf,find_flexible_pattern_positions
from NLP_module.normalise_texts import normalize_text2, normalize_text, get_last_four_tokens, \
    replace_substring_and_check,update_response_with_paragraph_data, process_themes
from NLP_module.PDFs_nlp import find_phrase_in_pdf
from Reference_processing.Grobid_references import parse_grobid_xml_to_dict,extract_citations_grobid

from alive_progress import alive_bar, alive_it,config_handler

from Word_modules.md_config import convert_zotero_to_md_with_id
from Zotero_module.zotero_data import note_update,book,initial_book,note_summary_schema
from progress.bar import Bar
from Pychat_module.gpt_api import process_pdf, write_batch_requests_to_file, create_batch, upload_batch_file, \
    call_openai_api, get_batch_ids, check_save_batch_status, retrieve_batch_results, read_or_download_batch_output, \
    creating_batch_from_pdf, process_batch_output, retry_api_call
from NLP_module.Clustering_Embeddings import clustering_df
from bs4 import BeautifulSoup,NavigableString
from Pychat_module.Pychat import ChatGPT
import pyzotero
from pyzotero import zotero, zotero_errors
from Academic_databases.databses import get_document_info1,get_document_info2
from tqdm import tqdm
import requests
import re
from datetime import datetime, date

from Word_modules.Creating_docx import  Docx_creation

Dc = Docx_creation()


def create_one_note(self, content="", item_id="", collection_id="", tag="", beginning=False
                    ):
    new_note = ''

    cabecalho = generate_cabecalho(zot=self.zot, item_id=item_id)
    new_content = f'<html><head><title>{tag.strip()}</title><style>body{{font-family:"Segoe UI",Tahoma,Geneva,Verdana,sans-serif;background-color:#f0f2f5;color:#333;margin:0;padding:20px;}}.container{{max-width:800px;margin:0 auto;background-color:#fff;padding:30px;border-radius:10px;box-shadow:0 4px 8px rgba(0,0,0,0.1);line-height:1.6;}}h1{{font-size:28px;color:#2c3e50;margin-bottom:20px;border-bottom:2px solid #e67e22;padding-bottom:10px;}}.cabecalho{{font-size:16px;font-weight:bold;color:#555;margin-bottom:20px;padding:10px;background-color:#f9f9f9;border-left:4px solid #3498db;}}.content{{font-size:16px;color:#444;margin-top:20px;line-height:1.8;}}.content p{{margin-bottom:15px;}}.content ul{{list-style-type:disc;margin-left:20px;}}.content li{{margin-bottom:10px;}}.footer{{margin-top:30px;font-size:14px;color:#777;text-align:center;border-top:1px solid #e1e1e1;padding-top:10px;}}</style></head><body><div class="container"><h1>{tag}</h1><div class="cabecalho">{cabecalho}</div><div class="content">{content}</div></div></body></html>' if beginning == False else content

    # Create the new note
    if item_id:
        new_note = self.zot.create_items([{
            "itemType": "note",
            'parentItem': item_id,
            "note": new_content,
            'tags': [{"tag": tag}]

        }])
    if collection_id:
        new_note = self.zot.create_items([{
            "itemType": "note",
            'collections': [collection_id],
            "note": content,
            'tags': [{"tag": tag}]

        }])
    print(new_note)
    new_note_id = new_note['successful']['0']['data']['key']
    if new_note_id:
        note = self.zot.item(new_note_id)
        note_content = note['data']['note']

        # Update the note content with the new note ID
        updated_content = note_content.replace(f'<em>@{item_id}</em><br>',
                                               f'<em>@{item_id}</em><br><em>Note ID: {new_note_id}</em><br>')

        updated_note = {
            'key': note['data']['key'],
            'version': note['data']['version'],
            'itemType': note['data']['itemType'],
            'note': updated_content,
            'tags': [{"tag": "summary_note"}]
        }
        time.sleep(15)
        try:
            # Attempt to update the note in Zotero
            response = self.zot.update_item(updated_note)
            if response:
                print("Note updated successfully.")
                return new_note_id
            else:
                print("Failed to update the note.")
        except Exception as e:
            print(f"An error occurred during the update: {e}")
def generate_cabecalho(zot, item_id,dict_response=False,links=True):
    """
        Creates a Zotero note for a given item ID, incorporating various item details and external data sources to enrich the note content.

        Parameters:
        - item_id (str): The unique identifier of the Zotero item for which to create a note.
        - path (str): The path where the note or related resources might be stored or used in processing.

        This method performs multiple steps:
        1. Retrieves the Zotero item by its ID.
        2. Extracts and formats item details such as authors, title, publication year, and DOI.
        3. Constructs a query for external data sources to enrich the note with citations, references, and related articles.
        4. Creates and updates the Zotero note with the retrieved information and additional links.

        Note:
        - The function handles items of specific types differently and might return early for types like attachments or links.
        """

    # Fetch the item by ID
    item = zot.item(item_id)
    data = item
    # Access the attachment details directly
    attachment_info = data['links'].get('attachment')


    link1 = ""
    link2 = ""
    authors = None
    try:
        # Iterate through each author in the data.
        # Check if both 'firstName' and 'lastName' keys exist, and join them if they do.
        # If they don't exist, use the 'name' key directly.
        authors = ", ".join([
            f"{author['firstName']} {author['lastName']}" if 'firstName' in author and 'lastName' in author
            else author['name']
            for author in data['data'].get('creators', [])
        ])
    except Exception as e:
        # If there is an error, print out the error and the format that caused it.
        # Ensure authors is set to None or an empty list if there is an error
        print(f"Error when parsing authors: {e}")
    title = data['data'].get('title')
    date = data['data'].get('date')

    year_match = re.search(r'\b\d{4}\b', date)
    if year_match:
        date = year_match.group(0)
    if date:
        new_date = f'PY=("{date}")'

    else:
        new_date = ""
    doi = data['data'].get('DOI')

    query1 = (f'('
              f'TI=("{title}")'
              f' AND '
              f"({new_date}"
              f'OR '
              f'AU=("{authors}"))'

              f')')

    key = data.get('key')
    item_type = data['data'].get('itemType')
    title = data['data'].get('title')
    abstract = data['data'].get('abstractNote')
    publication_title = data['data'].get('publicationTitle')
    if item['data']['itemType'] in ['note', 'attachment', 'linkAttachment', 'fileAttachment']:
        return  # Exit the function as we cannot proceed
    citation_key = None
    extra_data = data['data'].get('extra')

    if extra_data:
        for line in extra_data.split('\n'):
            if 'Citation Key' in line:
                citation_key = line.split(': ')[1]
    # Format the current date and time
    now = datetime.now().strftime("%d-%m-%Y at %H:%M")
    link1 = link2 = ''

    if links:
        data_wos = get_document_info1(query1)
        if data_wos:
            title = data_wos.get('title')
            publication_title = data_wos.get("source")
            doi = data_wos.get('doi') if not doi else doi
            if publication_title:
                data_wos.get('source').capitalize()

            link1 = f"""<li><strong>WoS Citing Articles</strong>: <a href="{data_wos.get("citing_articles_link")}">Citation[{data_wos.get('citations')}]</a></li>
                        <li><strong>WoS Reference_processing</strong>: <a href="{data_wos.get("references_link")}">Reference_processing</a></li>
                        <li><strong>WoS Related</strong>: <a href="{data_wos.get("related_records_link")}">Related</a></li>
                  """

        serp = get_document_info2(query=title, author=authors)
        if serp:
            link2 = f"""<li><strong>Citing Articles</strong>: <a href="{serp['cited_link']}">Citation[{serp['total_cited']}]</a></li>
                        <li><strong>Related</strong>: <a href="{serp["related_pages_link"]}">Related</a></li>
                                """

    metadata = f"""<em>@{key}</em><br>
          <em>Note date: {now}</em><br>
          <h1>{title}</h1>
          <hr>
          <hr>
          <h1>Metadata</h1>
          <ul>
          <li><strong>Title</strong>: {title.title()}</li>
          <li><strong>Authors</strong>: {authors}</li>
          <li><strong>Publication date</strong>: {date}</li>
          <li><strong>Item type</strong>: {item_type}</li>
          <li><strong>Publication Title</strong>: {publication_title}</li>
          <li><strong>DOI</strong>: {doi}</li>
          <li><strong>Identifier</strong>: <a href="{item['data'].get('url')}">Online</a></li>
          {link1}
          {link2}
      </ul>
      <hr>
      <hr>
      <h1>Abstract:</h1>
      <p>"{abstract}"</p>
          """
    if dict_response:
        return {'authors': authors,
                'date': date,
                'journal': publication_title,
                'title': title,
                'abstract':abstract,
                'doi':doi,
                "item_type":item_type,
                "url":item['data'].get('url'),
                "conferenceName":item['data'].get('conferenceName'),
                "pages":item['data'].get('pages'),
                "short_title":item['data'].get('shortTitle'),
                'item_id':key,
                'citation_key':citation_key,
                'attachment':attachment_info}
    return metadata.strip()

def parse_headings_with_html_content(html_file,pdf,user_id='9047943',
                                     parentItem='123',footnote_class='circle-list__item',
                                     sup_True=True,
                                     h2_class='jumplink-heading content-section-header section-type--section',
                                     p_class='p',
                                     sup_class='sup'):
    # Reading the HTML file
    page=1
    with open(html_file, 'r', encoding='utf-8') as file:
        content = file.read()

    soup = BeautifulSoup(content, 'html.parser')

    # Dictionary to hold footnote IDs and their content
    footnotes = {}
    footnotes_list = soup.find('div', id='footnotes-list')

    # Find all footnote children within this div

    # Checking if there is a div with id "footnotes-list"
    footnotes_list = soup.find('div', id='footnotes-list')
    if footnotes_list:
        footnotes_data = footnotes_list.find_all('div', class_='circle-list__item')
        for footnote in footnotes_data:
            # Retrieve the footnote ID
            fn_id = footnote['id']  # This gets the ID like 'FN-fn-1250'

            # Retrieve the footnote content
            fn_content = footnote.find('div', class_='circle-list__item__grouped__content').get_text(strip=True)

            # Store the footnote content in the dictionary with fn_id as the key
            footnotes[fn_id] = fn_content

            # Print the page number and footnote content for debugging (if needed)


    # String to accumulate modified HTML content
    all_html_content = ""
    # Find all h2 elements for section headings
    headers = soup.find_all('h2', class_=h2_class)
    for header in headers:
        section_title = header.get_text(strip=True)
        all_html_content += f"<hr>\n<h2>{section_title}</h2>"
        element = header.next_sibling
        index=1
        # Process elements following each header until the next header
        while element and element.name != 'h2':

            if element.name == 'div':
                paragraphs = element.find_all('p', class_=p_class)
                for p in paragraphs:
                    span = generate_zotero_annotation(user_id=user_id, item_id=parentItem,

                                                      page=page)
                    if sup_True:
                        sups = p.find_all('sup')
                        tokens = get_last_four_tokens(p.get_text(strip=True))
                        page = find_phrase_in_pdf(pdf_path=pdf, phrase=tokens)


                    # Create a new span
                    new_span = soup.new_tag("span")
                    new_blockquote =soup.new_tag("blockquote")
                    new_blockquote.extend(BeautifulSoup(span['start'], 'html.parser'))
                    new_span.extend(p)
                    if sup_True:
                        for sup in sups:
                            input(p)
                            a = p.find_next('a', class_='xref footnote')  # Corrected to find the closest <a> after <sup>
                            input(a)
                            input(sup)
                            if a and 'data-open' in a.attrs and a['data-open'] in footnotes:
                                print('yesss')
                                # Set href and title to the footnote content
                                a['href'] = footnotes[a['data-open']]
                                a['title'] = footnotes[a['data-open']]
                                # Optionally, you can keep the superscript number visible and enhance accessibility
                                sup.string = f"{a.string}"  # Keep the superscript number
                                # If you wish to decompose the <a> tag, you can comment out the decompose line
                                # a.decompose()  # Optionally remove the original <a> tag if no longer needed
                    new_span.extend(p)
                    # new_h3.string=f'Paragraph {index} - insert a title'
                    new_blockquote.extend(new_span)
                    # all_html_content += f"<h3>Paragraph {index} - insert a title</h3>{str(p)}"
                    new_blockquote.extend(BeautifulSoup(span['end'], 'html.parser'))

                    all_html_content += f"<h3>Paragraph {index} - insert a title</h3>{new_blockquote}"

                    index+=1
            element = element.next_sibling

    return all_html_content
def update_quote(zot, note_id, pdf,xml_path):
    contain =False
    if os.path.exists(xml_path):
        parsed_data = parse_grobid_xml_to_dict(xml_path=xml_path)
    else:
        extract_citations_grobid(pdf_path=pdf, file_name=xml_path)
        parsed_data = parse_grobid_xml_to_dict(xml_path)

    # ask in the structure section to get patters of number of page, water marks... to be cleaned after
    note = zot.item(note_id)
    note_content = note["data"]["note"]
    parentItem = note["data"]["parentItem"]
    user_id =note["library"]["id"]
    tags = note["data"]["tags"]
    if 'data' in note and 'note' in note['data'] and "updated_references" not in [tag["tag"] for tag in tags]:
        note_content = note['data']['note']
        soup = BeautifulSoup(note_content, 'html.parser')
        # Find the `h1` with the text "3. Summary"
        summary_h1 = soup.find('h1', string="3. Summary")
        if summary_h1:
            # Use a list comprehension to navigate through the siblings and collect `h2` texts
            h2_tags = [
                element for element in summary_h1.find_all_next()
                if element.name == 'h2' and element.find_previous('h1').string == "3. Summary"
            ]


        else:
            print("No 'h1' with the specified title found.")

        with tqdm(h2_tags, bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}]',
                  colour='blue') as pbar:
            for h2 in pbar:
                h3_tags = h2.find_next_siblings('h3', limit=3)

                for h3 in h3_tags:
                    print("initiating paragraph:",h3.get_text())

                    blockquote = h3.find_next_sibling('blockquote')
                    if blockquote:

                        citation_span = blockquote.find('span', class_='citation')
                        if citation_span is None:

                            original_text = blockquote.get_text()
                            input_string = get_last_four_tokens(original_text)
                            parts = []  # List to hold different parts of the new text
                            last_pos = 0  # Tracker for the last position in the original text

                            # Iterate through each reference needed
                            for ref_id, ref_info in parsed_data["Reference_processing"].items():
                                foot_note = ref_info['footnote']
                                chunk = get_last_four_tokens(ref_info["preceding_text"])
                                page = find_phrase_in_pdf(pdf_path=pdf, phrase=chunk)
                                processed_text, check = replace_substring_and_check(
                                    input_string=get_last_four_tokens(original_text),
                                    old_substring=chunk)

                                if check:
                                    print(f"foot_number {ref_id} was found in paragraph {h3.get_text().strip()}")
                                    position = original_text.find(chunk, last_pos)
                                    if position != -1:
                                        end_pos = position + len(chunk)
                                        parts.append(original_text[last_pos:end_pos])
                                        if ref_id.isdigit():

                                            # Create superscript tag with the reference link
                                            sup_tag = soup.new_tag("sup")
                                            if foot_note:

                                                a_tag = soup.new_tag("a", href=foot_note, title=foot_note)
                                                a_tag.string = str(ref_id)
                                                sup_tag.append(a_tag)
                                            else:
                                                sup_tag.string = ref_id

                                            parts.append(str(sup_tag))

                                        if not ref_id.isdigit():
                                            if foot_note:
                                                a_tag = soup.new_tag("a", href=foot_note, title=foot_note)
                                                a_tag.string = str(ref_id)
                                                parts.append(str(a_tag))
                                            else:
                                                parts.append(ref_id)
                                    last_pos = end_pos

                                    input("Press Enter to")
                                    contain = True
                                    break

                            if contain == False:

                                print(
                                    f"For the paper {pdf.replace(".pdf", "").split("/")[-1]}, no quote was not found. Please check the key phrase in the document paragraph:\n{h2.get_text()}")
                                print(
                                    f"the preceeding words was:\n{chunk}\n not matching with {input_string}")
                                continua = input("do you wanna skip it? yes or no?")
                                if continua == "no":
                                    contain = True

                            pbar.update()

                            # Append any remaining part of the text
                            parts.append(original_text[last_pos:])

                            # Replace the content of the blockquote with new content including references
                            blockquote.clear()
                            span = generate_zotero_annotation(user_id=user_id, item_id=parentItem,

                                                              page=page)
                            # Append the initial span if it contains specific attributes or content
                            blockquote.append(BeautifulSoup(span['start'], 'html.parser'))

                            # Create a new span and paragraph to hold the content
                            new_span = soup.new_tag("span")
                            p_tag = soup.new_tag("p")
                            p_tag.append(BeautifulSoup(''.join(parts), 'html.parser'))
                            new_span.append(p_tag)

                            # Append the new span to the blockquote
                            blockquote.append(new_span)

                            # Append the ending span if it contains specific attributes or content
                            blockquote.append(BeautifulSoup(span['end'], 'html.parser'))
                        tags.append({'tag': "updated_references"})

                        # Serialize the modified soup to HTML string
                        updated_note_content = str(soup)
                        updated_note = {
                            'key': note['data']['key'],
                            'version': note['data']['version'],
                            'itemType': note['data']['itemType'],
                            'note': updated_note_content,
                            'tags': tags
                        }

                        # Update the note in Zotero
                        try:
                            response = zot.update_item(updated_note)
                            if response:
                                print("Note updated successfully.")
                            else:
                                print("Failed to update the note.")
                        except Exception as e:
                            print(f"An error occurred during the update: {e}")
                        return response
def update_note_zotero(note,tags,content,zot):
    updated_note = {
        'key': note['data']['key'],
        'version': note['data']['version'],
        'itemType': note['data']['itemType'],
        'note': content,
        'tags': tags
    }

    # Update the note in Zotero
    try:
        response = zot.update_item(updated_note)
        if response:
            print("Note updated successfully.")
        else:
            print("Failed to update the note.")
    except Exception as e:
        print(f"An error occurred during the update: {e}")
    return response

def get_content_after_heading(zot, note_id, main_heading, sub_heading):
        """
            Extracts all text content from specified sub_headings within a section defined by a main_heading.

            Args:
            note_content (str): HTML content to be parsed.
            main_heading (str): Specific heading tag and title to identify the section, e.g., '<h1>1. Summary</h1>'.
            sub_heading (str): Sub heading tag to find within the main heading section, e.g., 'h3'.

            Returns:
            list: A list of texts from all sub_heading tags within the specified main heading section.
            """

        note = zot.item(note_id)
        tags = note['data'].get('tags', [])
        if "note_complete" in tags:
            return

        if 'data' in note and 'note' in note['data']:
            note_content = note['data']['note']
        else:
            print(f"No note content found for item ID {note_id}")
            return []

        main_tag_name, title = re.match(r'<(h\d+)>(.*?)</\1>', main_heading).groups()

        # Adjust the pattern to capture all content following the specified main heading until the next main heading of the same or higher level
        pattern = re.compile(rf'{re.escape(main_heading)}(.*?)(?=<{main_tag_name} |$)', re.DOTALL | re.IGNORECASE)
        matches = pattern.search(note_content)
        if not matches:
            print(f"No matching section found for the heading {main_heading}.")
            print(note_content)
            return []

        section_content = matches.group(1)
        soup = BeautifulSoup(section_content, 'html.parser')
        results = []

        sub_heading_tags = soup.find_all(sub_heading)
        for tag in sub_heading_tags:
            sibling = tag.find_next_sibling()
            # Check if the next sibling is a blockquote and belongs to the current sub-heading
            if sibling and sibling.name == 'blockquote':
                results.append({
                    'code': tag.get_text().strip(),  # title of the h3
                    'content': sibling.get_text().strip(),  # text of the blockquote
                    'quotes': str(sibling)  # HTML content of the blockquote
                })

        return results

def generate_zotero_annotation(user_id, item_id, page):
    if page is None:
        page = 1

    # Create the annotation data
    annotation_data = {
        "attachmentURI": f"http://zotero.org/users/{user_id}/items/{item_id}",
        "pageLabel": str(page),
        "position": {
            "pageIndex": page - 1,
            "rects": [[0, 0, 100, 100]]  # Placeholder for the rectangle coordinates
        },
        "citationItem": {
            "uris": [f"http://zotero.org/users/{user_id}/items/{item_id}"],
            "locator": str(page)
        }
    }

    # URL encode the annotation data
    encoded_annotation = urllib.parse.quote(str(annotation_data).replace("'", '"'))

    # Create the citation data for the end span
    citation_data = {
        "citationItems": [{
            "uris": [f"http://zotero.org/users/{user_id}/items/{item_id}"],
            "locator": str(page)
        }],
        "properties": {}
    }

    encoded_citation = urllib.parse.quote(str(citation_data).replace("'", '"'))


    # HTML structure
    start_tag = f'<span class="highlight" data-annotation="{encoded_annotation}">'
    end_tag = f'</span><span class="citation" data-citation="{encoded_citation}"><span class="citation-item"></span></span>'
    print('generating annotation')

    return {"start": start_tag, "end": end_tag}


class Zotero:
    def __init__(self,
                 library_id="<Library ID>",
                 library_type='user',
                 api_key="<API KEY>",
                 chat_args = { "chat_id": "pdf"},
                 os = "mac",
                 sleep =10
                 ):
        """
            Initialize a new instance of the class, setting up the necessary configurations for accessing and interacting with a Zotero library.

            Parameters:
            - library_id (str): The ID of the Zotero library to connect to.
            - library_type (str): The type of the Zotero library (e.g., 'user' or 'group').
            - api_key (str): The API key used for authenticating with the Zotero API.
            - chat_args: Additional arguments or configurations related to chat functionalities (the exact type and structure need to be specified based on usage).

            This method also establishes a connection to the Zotero library, sets the directory path for Zotero storage based on the operating system, and initializes a schema attribute.
            """
        self.library_id = library_id
        self.library_type = library_type
        self.api_key = api_key
        self.zot = self.connect()
        self.sleep = sleep

        self.chat_args = chat_args
        self.zotero_directory = "/Users/pantera/Zotero/storage/" if os=="mac" else "C:\\Users\\luano\\Zotero\\storage\\"
        self.schema = ""

    def connect(self):
        """
           Establishes and returns a connection to the Zotero API using the Zotero library credentials stored in the instance.

           Returns:
           - An instance of the Zotero object configured with the specified library ID, library type, and API key. This object can be used to perform various operations with the Zotero API.
           """

        return zotero.Zotero(self.library_id, self.library_type, self.api_key)

    def get_or_update_collection(self, collection_name=None, update=False, tag=None,pdf=True):
        """
        Fetches or updates a specified collection's data from Zotero.

        If the collection data already exists locally and update is False, the data is loaded from a local file.
        If the local data does not exist or update is True, the method fetches the data from the Zotero API and updates
        the local file. If the provided collection name does not match any collections in Zotero, the user is prompted
        to enter a new name until a valid one is provided.

        Args:
            collection_name (str): The name of the collection to fetch or update.
            update (bool): If True, forces the method to update the local data with data from Zotero.
            tag (str): replace, append or delete as options

        Returns:
            dict: A dictionary containing the collection's data.
        """
        while True:
            if not collection_name:
                collection_name = input("Please enter the collection name you want to get data from: ")

            file_name = f'Zotero_module/Data/collections_data/{collection_name.replace(" ", "_").lower()}_collection.pkl'
            target_collection = {}

            print(f'Update mode is {"on" if update else "off"}.')

            # Check if update is required
            if not update:
                try:
                    with open(file_name, 'rb') as pickle_file:
                        target_collection = pickle.load(pickle_file)
                        print(f'Loaded data for "{collection_name}" from local file.')
                        return target_collection
                except FileNotFoundError:
                    print(f"No existing file found for {collection_name}. Switching to update mode.")
                    update = True

            # Fetch all collections from Zotero
            all_collections = self.zot.collections()
            print(f'Fetched {len(all_collections)} collections from Zotero.')

            collection_found = False
            # Check if we found the right collection
            pdf_path = None
            for collection in all_collections:
                if collection['data']['name'].lower() == collection_name.lower():
                    print(f'Found the collection "{collection_name}".')
                    collection_key = collection['data']['key']
                    target_collection = {
                        'collection_name': collection_name,
                        'collection_key': collection_key,
                        'items': {

                            'papers': {}
                        }
                    }
                    collection_found = True

                    # Initialize variables for pagination
                    items_per_request = 100  # Max items per request (set by Zotero's API limits)
                    start = 0  # Start at the beginning of the collection
                    total_items_fetched = 0  # Keep track of the total number of items fetched

                    # Fetch all items for this specific collection, handling pagination
                    while True:
                        collection_items = self.zot.collection_items(collection_key, start=start,
                                                                     limit=items_per_request)
                        if not collection_items:
                            break  # Exit loop if no more items are returned
                        note_info = None
                        collection_items = [papers for papers in collection_items if
                                            papers['data']['itemType'] not in ['note', 'attachment', 'linkAttachment',
                                                                               'fileAttachment',
                                                                               'annotation']]

                        # Process each item in this batch
                        with (tqdm(collection_items, bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}]',
                                   colour='green') as pbar):

                            for item in pbar:
                                item_data = item['data']
                                item_tags = item_data["tags"]

                                paper_title = item_data.get('title', 'No Title')
                                pbar.set_description(f"processing {paper_title}")
                                item_id = item_data['key']

                                # Process attachments if present Big change
                                try:

                                    authors = [
                                        f"{author['firstName']} {author['lastName']}" if 'firstName' in author and 'lastName' in author
                                        else author['name']
                                        for author in item['data'].get('creators', [])
                                    ]
                                    if len(authors) > 3:
                                        authors = authors[1] + "et al"
                                    else:
                                        authors = ", ".join(authors)
                                except Exception as e:
                                    authors = "author"
                                    # If there is an error, print out the error and the format that caused it.
                                    # Ensure authors is set to None or an empty list if there is an error
                                    print(f"Error when parsing authors: {e}")

                                date = item['data'].get('date')
                                date = "date" if date is None else date
                                year_match = re.search(r'\b\d{4}\b', date)
                                if year_match:
                                    date = year_match.group(0)

                                reference = f"({authors}, {date})"
                                note_info = self.get_children_notes(item_id, new_filename=reference,pdf=pdf)
                                paper_data = {'item_id': item_id, "item_tags": item_tags, "reference": reference,
                                              "note": note_info}
                                target_collection['items']['papers'][paper_title] = paper_data
                            # pbar.update()
                        total_items_fetched += len(collection_items)
                        start += items_per_request  # Move start up by the number of items per request

                    print(f'Found a total of {total_items_fetched} items in the collection "{collection_name}".')

                    # Save the updated collection dictionary to a pickle file
                    with open(file_name, 'wb') as pickle_file:
                        pickle.dump(target_collection, pickle_file)
                        print(f'Saved updated data for "{collection_name}" to local file.')

                    return target_collection

            if not collection_found:
                print(f'Collection "{collection_name}" not found in Zotero. Please try again.')
                collection_name = None  # Reset collection_name to prompt again

    def get_pdf_path(self, attachment_item, new_filename, convert=False):
        if attachment_item is None:
            return None
        attachment_id = attachment_item['key']
        dir_path = self.zotero_directory + attachment_id

        """
        Renames the first encountered PDF file in the specified directory to a new filename,
        if the current filename does not match the new filename. It assumes there's only one
        PDF file within the entire directory structure starting from 'dir_path'.

        Parameters:
        - dir_path (str): The root directory path to start searching for the PDF file. The search
          will include all subdirectories under this path.
        - new_filename (str): The new filename to assign to the found PDF file. This should include
          the '.pdf' extension but should not include any directory path components.

        Returns:
        - str: The full path of the PDF file after renaming. If the PDF file's name already matched
          'new_filename', the original path is returned. If no PDF file is found, returns None.

        Raises:
        - ValueError: If 'new_filename' does not end with '.pdf'.

        Example usage:
            renamer = FileRenamer()
            pdf_path = renamer.get_pdf_path("/path/to/directory", "new_document_name.pdf")
            if pdf_path:
                print(f"PDF path: {pdf_path}")
            else:
                print("No PDF file found in the directory.")

        Note:
        This method assumes that there is only one PDF file in the given directory and its
        subdirectories. If there are multiple PDF files, only the first encountered PDF file will be
        renamed, and the method will stop searching further.
        """

        for root, dirs, files in os.walk(dir_path):

            for file in files:
                if file.endswith(".pdf") or file.endswith(".md"):
                    current_pdf_path = os.path.join(root, file)
                    new_pdf_path = os.path.join(root, new_filename)
                    if current_pdf_path != new_pdf_path:
                        attachment_item['data']['filename'] = new_filename  # Set new filename
                        print(self.zot.update_item(attachment_item))

                        print(f"Renaming file: current_pdf_path:{current_pdf_path} to new_pdf_path: {new_pdf_path}")
                    if os.path.exists(new_pdf_path):
                        print(new_pdf_path)
                        return new_pdf_path
                    else:
                        print(current_pdf_path)
                        return current_pdf_path

    def update_note(self, note,content,tag=None):
        if tag is None:tag=note['data'].get('tags', [])
        updated_note = {
            'key': note['data']['key'],
            'version': note['data']['version'],
            'itemType': note['data']['itemType'],
            'note': content,
            'tags': tag
        }
        response=None
        # Update the note in Zotero
        try:
            response = self.zot.update_item(updated_note)
            if response:
                print("Note updated successfully.")
            else:
                print("Failed to update the note.")
        except Exception as e:
            print(f"An error occurred during the update: {e}")
        return response
    def processing_collection_paragraphs(self, collection_name,item_start=False,
                              rewrite=False,
                              insert_database=False,
                              create_md_file=False,
                              update_paragraph_notes=False,
                              batch=False,
                              store_only=True,
                              update=True,
                                         processing_batch=False,
                                         database_name='',
                                         overwrite_payload=False):

        collection_data = self.get_or_update_collection(collection_name=collection_name, update=update)
        loop=True
        if item_start:
            loop=False
        data = [(t, i) for t, i in collection_data[("items")]["papers"].items()]
        batch_requests =[]
        note_complete = len(collection_data["items"]["papers"].items())

        # Setting up the tqdm iterator
        pbar = tqdm(data,
                    bar_format="{l_bar}{bar:30}{r_bar}{bar:-30b}",
                    colour='green')
        for keys, values in pbar:

            # Dynamically update the description with the current key being processed
            index1 = [i for i in collection_data["items"]["papers"]].index(keys)
            pbar.set_description(f"Processing index:{index1},paper:{keys} missing:{note_complete} ")

            note = values["note"]
            id = values['item_id']
            pdf = note['pdf']
            file_name = r"C:\Users\luano\Downloads\AcAssitant\Files\Batching_files\\"  + collection_name+ ".jsonl"
            if item_start:
                if item_start==id or index1==21:
                    loop=True
            note_id = None
            try:
                note_id = " ".join([i['note_id'] for i in note['note_info'] if
                                    "Paragraphs" in i['tag']])
            except Exception as e:
                print('err with note_id: ', e)
                print(note_id)
                print(note['note_info'])
                print(keys)
                pass


            if note_id and loop:

                self.insert_title_paragraphs(zotero_collection=collection_name,
                                             item_id=id,
                                             note_id=note_id,
                                             insert_database=insert_database,
                                             create_md_file=create_md_file,
                                             update_paragraph_notes=update_paragraph_notes,
                                             batch=batch,
                                             store_only=store_only,
                                             processing_batch=processing_batch,
                                             rewrite=rewrite,
                                             database_name=database_name,
                                             overwrite_payload=overwrite_payload
                                             )

        if batch:
            batch_input_file_id = upload_batch_file(file_name)

            batch_id = create_batch(batch_input_file_id)
            check_save_batch_status(batch_id)

    def insert_title_paragraphs(self,zotero_collection,database_name,item_id=None,insert_database=False,overwrite_payload=False,create_md_file=False, update_paragraph_notes=False,batch=False,store_only=False,processing_batch=False,note_id=None,rewrite=False):
        metadata = generate_cabecalho(zot=self.zot, item_id=item_id, dict_response=True, links=False)
        tags_md=[]
        keywords= None
        if note_id is None:

            note_id =self.get_children_notes(item_id=item_id,get_note='Paragraphs')
        proceed=True
        batch_requests=[]
        handller=""
        note = self.zot.item(note_id)
        note_content = note["data"]["note"]
        parentItem = note["data"]["parentItem"]
        collection_name = parentItem+"_"+database_name
        tags = note["data"]["tags"].extend([{"tag": "indexed"}])
        if 'data' in note and 'note' in note['data'] :

            note_content = note['data']['note']
            soup = BeautifulSoup(note_content, 'html.parser')
            # Process each h2 section
            results = []
            h1_tags = soup.find_all('h1')
            title = ''
            file_name = r"C:\Users\luano\Downloads\AcAssitant\Files\Batching_files\\"  + zotero_collection+ ".jsonl"
            handler = QdrantHandler(qdrant_url="http://localhost:6333")
            # processed_batches = process_batch_output(
            #    processing_batch)
            # handler.qdrant_handler.qdrant_client.delete_collection(collection_name=parentItem)
            stop_sections=['notes','references']
            if insert_database:
                # handler.qdrant_client.delete_collection(collection_name=f'paper_{parentItem}')
                time.sleep(4)
                if rewrite:
                    handler.qdrant_client.delete_collection(collection_name=collection_name)
                    time.sleep(4)
                collection_created = handler.create_collection(collection_name=collection_name)
                proceed= collection_created

            # duplicate =handler.qdrant_handler.qdrant_collections(col_name=parentItem)


            # Check if there are at least two <h1> tags
            if len(h1_tags) > 1:
                # Get the second <h1> tag
                title = h1_tags[1]
            else:
                print("Less than two <h1> tags found.")

            markdown_content = ""

            markdown_content += f"# {title}\n\n"
            if proceed:


                for n,h2 in enumerate(soup.find_all('h2')):
                    section_title = h2.get_text()
                    markdown_content += f"## {section_title}\n\n"
                    if section_title.lower() not in stop_sections:
                        section_data = {'title':title,'h2': section_title, 'paragraphs': []}
                        paragraphs = []
                        next_elem = h2.find_next_sibling()

                        while next_elem and next_elem.name != 'h2':
                            if next_elem.name == 'h3':
                                blockquote = next_elem.find_next_sibling('blockquote')
                                text = next_elem.get_text()
                                import re
                                # Check if the pattern exists before attempting to split
                                if re.search(r'\d\s*-\s*', text):
                                    h3_title = re.split(r'\d\s*-\s*', text)[-1]
                                else:
                                    # Fallback: just use the original text if no match is found
                                    h3_title = text
                                if blockquote:
                                    paragraphs.append({
                                        'old_h3': h3_title,
                                        'blockquote': str(blockquote),
                                        'paragraph':blockquote.get_text().strip()
                                    })
                            next_elem = next_elem.find_next_sibling()

                        if paragraphs:
                            new_titles = {'titles': [
                                {"h3_title": paragraphs[i]['old_h3'], 'paragraph_number': i + 1} for i in
                                range(len(paragraphs))
                            ]}
                            # import re
                            #
                            # paragraph_incomplete = [paragraph['old_h3']
                            #
                            #     for paragraph in paragraphs
                            #     if
                            #     "insert" in paragraph['old_h3'] or len(paragraph['old_h3'].split()) < 6
                            # ]
                            # if paragraph_incomplete:
                            #     print('incomplete title found: ', paragraph_incomplete)
                            #     time.sleep(4)
                            #
                            #     update_paragraph_notes=True

                            if processing_batch and update_paragraph_notes:
                                processed_batches = process_batch_output(file_path=processing_batch,
                                                                         item_id_filter=parentItem)
                                new_titles= processed_batches[n]
                            if update_paragraph_notes and not processing_batch:
                                para_lenght = f"Analyse the following paragraph" if len(paragraphs) ==1 else f"Analyse these {len(paragraphs)} paragraphs:"

                                new_titles = eval(
                                    call_openai_api(function='find_title',id=parentItem,batch=batch, data=f'title={title}\nsection/subsections={section_title}\n{para_lenght}:{paragraphs}'))
                                for new_title in new_titles:
                                    print(new_title)
                            if store_only or batch:
                                para_lenght = f"Analyse the following paragraph" if len(paragraphs) ==1 else f"Analyse these {len(paragraphs)} paragraphs:"

                                batch_request= call_openai_api(function='find_title', id=parentItem, batch=True,
                                                    text=f'title={title}\nsection/subsections={section_title}\n{para_lenght}:{paragraphs}')

                                write_batch_requests_to_file(batch_request=batch_request,file_name=file_name)
                                batch_requests.append(batch_request)


                            # Initialize the first h3 element
                            h3_elem = h2.find_next_sibling('h3')

                            for i, paragraph in enumerate(paragraphs):
                                # Find the corresponding title by paragraph_number
                                matching_title = next(
                                    (title for title in new_titles['titles'] if title['paragraph_number'] == i + 1), None)

                                if matching_title:

                                    section_data['paragraphs'].append({
                                        'old_h3': paragraph['old_h3'],
                                        'new_h3': matching_title['h3_title'],
                                        'blockquote': paragraph['blockquote']
                                    })
                                    if h3_elem:

                                        h3_elem.string = f'Paragraph {i + 1} - {matching_title["h3_title"]}'
                                        # Move to the next h3 element for the next iteration
                                        h3_elem = h3_elem.find_next_sibling('h3')
                                        if overwrite_payload:

                                            context = f'\ncontext:section title:{section_title} paragraph title:{matching_title['h3_title']}\nnote: do not include {metadata['authors']} in entities'

                                            keywords = call_openai_api(function='getting_keywords', data=paragraph['paragraph']+ context,
                                                                       id='')


                                            hash_object = hashlib.sha256(matching_title['h3_title'].encode('utf-8'))

                                            # Convert the hash to an integer and limit it to 8 digits
                                            paragraph_id = int(hash_object.hexdigest(), 16) % (10 ** 8)

                                            new_payload=  {
                                               "paragraph_count ": str(i + 1),
                                               "article_title":title.get_text(),
                                               "section_title":section_title,
                                               "paragraph_title":matching_title['h3_title'],
                                               "paragraph_blockquote":paragraph['blockquote'],
                                               "paragraph_text":paragraph['paragraph'],
                                               "metadata":metadata,
                                               "keywords":keywords
                                            }
                                            handler.clear_and_set_payload(collection_name=collection_name, new_payload=new_payload,
                                                                   point_id=paragraph_id)


                                        if insert_database:
                                            context = f'\ncontext:section title:{section_title} paragraph title:{matching_title['h3_title']}'

                                            keywords = call_openai_api(function='getting_keywords',
                                                                       data=paragraph['paragraph'] + context,
                                                                       id='')
                                            time.sleep(4)
                                            handler.process_and_append(
                                                                       collection_name=collection_name,
                                                                       paragraph_count=str(i+1),
                                                                       article_title=title.get_text(),
                                                                       section_title=section_title,
                                                                       paragraph_title=matching_title['h3_title'],
                                                                       paragraph_blockquote=paragraph['blockquote'],
                                                                       paragraph_text=paragraph['paragraph'],
                                                                       metadata=metadata,
                                                                       keywords=keywords,

                                                                       )
                                        if create_md_file:
                                            hash_object = hashlib.sha256(matching_title['h3_title'].encode('utf-8'))
                                            paragraph_id = int(hash_object.hexdigest(), 16) % (10 ** 8)

                                            # Append to markdown content

                                            markdown_content += f">[!important] > ### {matching_title['h3_title']}\n\n"
                                            markdown_content += f"> {convert_zotero_to_md_with_id(html_paragraph=paragraph['blockquote'],item_id=item_id,paragraph_id=str(paragraph_id),keywords=" ".join(self.convert_to_obsidian_tags(keywords)))}\n\n"


                    results.append(section_data)

                if store_only or batch:
                    return batch_requests

                if create_md_file:

                    filepath= r"C:\Users\luano\OneDrive - University College London\Obsidian\Thesis\Paragraphs"+"\\"+metadata['citation_key']+".md"
                    with open(filepath, "w",encoding='utf-8') as md_file:
                        if tags_md:
                            markdown_content = markdown_content + "\n\n" +" ".join(tags_md)
                        md_file.write(markdown_content)
                        self.attach_file_to_item(parent_item_id=parentItem,file_path=filepath,tag_name='md_paragraphs')

                if update_paragraph_notes:
                    # After the loop, update the note content
                    updated_note_content = str(soup)
                    self.update_note(note, updated_note_content,)
                # After the loop, update the note content
                # updated_note_content = str(soup)
                # self.update_note(note, updated_note_content,tag=tags)

    # Convert keywords into Obsidian tag format
    def convert_to_obsidian_tags(self,keywords_dict):
        tags = []

        # Loop through the categories (topics, entities, academic_features)
        for category, words in keywords_dict['keywords'].items():
            for word in words:
                # Convert each keyword into a tag with a hash (#) and replace spaces with underscores
                tag = f"#{word.replace(' ', '_').replace(".","").replace("'","").replace(",","")}"
                tags.append(tag)

        return tags
    def create_citation_from_pdf1(self, collection_name, article_title="", update=True,batch=False,store_only=True):

        collection_data = self.get_or_update_collection(collection_name=collection_name, update=update)

        data = [(t, i) for t, i in collection_data[("items")]["papers"].items()][::-1]
        if article_title != "":
            index1 = [i for i in collection_data["items"]["papers"]].index(article_title)
            data = [(t, i) for t, i in collection_data[("items")]["papers"].items()][index1:index1 + 1]

        note_complete = len(collection_data["items"]["papers"].items())
        # Setting up the tqdm iterator
        pbar = tqdm(data,
                    bar_format="{l_bar}{bar:30}{r_bar}{bar:-30b}",
                    colour='green')
        batch_requests =[]

        for keys, values in pbar:
            # Dynamically update the description with the current key being processed
            index1 = [i for i in collection_data["items"]["papers"]].index(keys)
            pbar.set_description(f"Processing index:{index1},paper:{keys} missing:{note_complete} ")

            note = values["note"]
            id = values['item_id']
            pdf = note['pdf']
            sections =note['sections']

            note_id = " ".join([i['note_id'] for i in note['note_info'] if "summary_note" in i['tag']  ])

            if note_id:
                self.extract_insert_article_schema(note_id=note_id,save=True)
        #
        #
        #     # if note_id and sections is not None:
        #     if note_id and pdf is not None:
        #         print(pdf)
        #
        #         reference = values['reference'] if values['reference'] else ""
        #         file_name =r"C:\Users\luano\Downloads\AcAssitant\Batching_files"+"_"+reference +"_"+id+".jsonl"
        #         prompt=f"""You are tasked with extracting references from a text containing both in-text and footnote citations in numerical and author-year styles. Perform the following steps:
        #                     1. Identify citations in the text, which could be numbers or numbers in brackets/parentheses (e.g., 'mainstream theories such as realism and neoliberalism are mainstream¹' or 'mainstream theories such as realism and neoliberalism are mainstream (1)').
        #                     2. Match each citation number to its corresponding footnote if the footnote starts with the same number (e.g., '1. John S Davis II and others, Stateless Attribution: Toward International Accountability in Cyberspace (RAND Corporation 2017) 21.'). A preceeding_text citation and footnote suggest a complete reference.
        #                     3. Output a list of dictionaries, where each dictionary contains 'ref' for reference number, 'preceding_text' for the text before the citation, and 'footnote' for the corresponding footnote text. Do not provide additional information information just the format the output as: [{{'ref': <ref number>, 'preceding': <preceding_text>, 'footnote': <footnote>}}]. If no references are found, return None. If a footnote is missing, set 'footnote' to an empty string.
        #                     4. do not modify any information from the text, just assign the correspond information to its keys.
        #                     5. Ensure the output is a valid python list with valid dicts"""
        #         results =creating_batch_from_pdf(file_path=pdf,batch=batch,reference=reference,store_only=store_only,prompt=prompt,tag='refs',id=id,file_name=file_name)
        #         batch_requests.extend(results)
        # if batch and batch_requests and not store_only:
        #     file_name = write_batch_requests_to_file(batch_requests,
        #                                              file_name=file_name)
        #     batch_input_file_id = upload_batch_file(file_name)
        #     batch_id = create_batch(batch_input_file_id)
        #     check_save_batch_status(batch_id)
        #
        # else:
        #     print("[DEBUG] Batch processing failed or no results returned.")


    def get_section_citations(self, file_name, texts,api_results=None ):
        if api_results is None:
            api = ChatGPT(**self.chat_args)

        """
            Append a list of dictionaries to a JSONL file, creating the file if it does not exist.

            Parameters:
            - file_path (str): Path to the JSONL file.
            - data_list (list): List of dictionaries to be appended to the file.
            """
        # Check if the file exists
        file_exists = os.path.isfile(file_name)

        # Open the file in append mode if it exists, otherwise it will create it
        with open(file_name, 'a') as file:
            # If the file did not exist and is newly created, we don't need to prepend a newline
            if file_exists:
                # Add a newline before appending if the file already existed
                file.write('\n')
                for text in texts:
                    prompt =f"""You are tasked with extracting references from a text containing both in-text and footnote citations in numerical and author-year styles. Perform the following steps:
                            1. Identify citations in the text, which could be numbers or numbers in brackets/parentheses (e.g., 'mainstream theories such as realism and neoliberalism are mainstream¹' or 'mainstream theories such as realism and neoliberalism are mainstream (1)').
                            2. Match each citation number to its corresponding footnote if the footnote starts with the same number (e.g., '1. John S Davis II and others, Stateless Attribution: Toward International Accountability in Cyberspace (RAND Corporation 2017) 21.'). A preceeding_text citation and footnote suggest a complete reference.
                            3. Output a list of dictionaries, where each dictionary contains 'ref' for reference number, 'preceding_text' for the text before the citation, and 'footnote' for the corresponding footnote text. Do not provide additional information information just the format the output as: [{{'ref': <ref number>, 'preceding': <preceding_text>, 'footnote': <footnote>}}]. If no references are found, return None. If a footnote is missing, set 'footnote' to an empty string.
                            4. do not modify any information from the text, just assign the correspond information to its keys.
                            5. Ensure the output is a valid python list with valid dicts
                            
                            text: {text}"""

                    try:
                        # data = eval(api.interact_with_page(path=pdf, prompt=prompt, copy=True))
                        data = eval(api.send_message(message=prompt,sleep_duration=self.sleep))
                        if data:
                            [file.write(json.dumps(dici) + '\n') for dici in
                             data]  # Append line to file with a newline character
                    except Exception as err:
                        print(err)

    def get_section_citations_api(self, file_name, texts):

        # Check if the file exists
        file_exists = os.path.isfile(file_name)

        # Open the file in append mode if it exists, otherwise it will create it
        with open(file_name, 'a') as file:
            # If the file did not exist and is newly created, we don't need to prepend a newline
            if file_exists:
                # Add a newline before appending if the file already existed
                file.write('\n')
                for text in texts:
                    prompt = f"""You are tasked with extracting references from a text containing numerical references. Perform the following steps:
                            1. Identify citations in the text, which could be numbers or numbers in brackets/parentheses (e.g., 'mainstream theories such as realism and neoliberalism are mainstream¹' or 'mainstream theories such as realism and neoliberalism are mainstream (1)').
                            2. identify footnotes  which come starting by a number and then a statement such as :1. Military and Paramilitary Activities in and Against Nicaragua(smith,2015)
                            2. Match each citation number to its corresponding footnote if the footnote starts with the same number, in our example, ref:1 preceeding_text:realism and neoliberalism are mainstream and footnote:1. Military and Paramilitary Activities in and Against Nicaragua(smith,2015)
                            3. Output a list of dictionaries, where each dictionary contains 'ref' for reference number; 'preceding_text' containing a short phrase immediately before the ref number; and 'footnote' for the corresponding footnote text.  format the output as: [{{'ref': <ref number>, 'preceding': <preceding_text>, 'footnote': <footnote>}}]. If no references are found, return None. If a footnote is missing, set 'footnote' to an empty string.
                            


                            text: {text}"""

                    try:
                        response_content, chat_id = call_openai_api(prompt)
                        from pprint import pprint
                        data = eval(response_content)
                        pprint(data)
                        if data:
                            [file.write(json.dumps(dici) + '\n') for dici in
                             data]  # Append line to file with a newline character
                    except Exception as err:
                        print(err)

    def validate_references(self,file_name,dict_list,pdf):



        api = ChatGPT(**self.chat_args)

        """
            Append a list of dictionaries to a JSONL file, creating the file if it does not exist.

            Parameters:
            - file_path (str): Path to the JSONL file.
            - data_list (list): List of dictionaries to be appended to the file.
            """
        # Check if the file exists
        file_exists = os.path.isfile(file_name)

        # Open the file in append mode if it exists, otherwise it will create it
        with open(file_name, 'a') as file:
            # If the file did not exist and is newly created, we don't need to prepend a newline
            if file_exists:
                # Add a newline before appending if the file already existed
                file.write('\n')
                twentie =[dict_list[i:i + 10] for i in range(0, len(dict_list), 20)]
                for index in range(len(twentie)):

                    prompt = f"Read the document carefully and find references found in the list of dictionaries where each dictionary contains a reference number (ref) and preceeding_text  and footnote. 1. read the first dict and get the ref number. with the ref number, search the preceeding text and the footnote, verifying if they match. if they dont, correct them and return the correct dict. do this with all the dicts, returning only dicts found and matched in the document. the dict list format is: ´´´python [{{'ref': <ref number>, 'preceeding': <preceeding>, 'footnote': <footnote>}}]. here is the list:{twentie[index]}\nnote: you should return only dicts with corrected values derived directly from the pdf in a code block without additional information. note 2. Return a list of {len(twentie[index])} dicts whose content matched with the pdf"

                    try:
                        data = eval(api.interact_with_page(path=pdf, prompt=prompt,copy=True))
                        # data = eval(api.send_message(message=prompt,sleep_duration=self.sleep))
                        if data:
                            [file.write(json.dumps(dici) + '\n') for dici in
                             data]  # Append line to file with a newline character
                    except Exception as err:
                        print(err)


    #
    # def update_all(self, collection_name, article_title="", tag=None, update=True, specific_section=None, delete=False,
    #                index=0):
    #     """
    #         Iterates over a Zotero collection, updating notes for each item based on predefined rules and external data.
    #
    #         Parameters:
    #         - collection_name (str): The name of the Zotero collection to process.
    #         - index (int, optional): The starting index within the collection to begin processing. Defaults to 0.
    #         - tag (str, optional): A specific tag to filter items by within the collection. If None, no tag filter is applied. Defaults to None.
    #         - update (bool, optional): Whether to actually perform updates on the notes. Defaults to True.
    #
    #         The method applies a sequence of updates to each note in the collection, including extracting and inserting article schemas, cleaning titles, and potentially updating note sections based on external data sources. The updates can be configured via the parameters, and the method tracks the progress and handles exceptions accordingly.
    #
    #         Note:
    #         - The method provides feedback via print statements regarding the progress and success of note updates.
    #         """
    #     collection_data = self.get_or_update_collection(collection_name=collection_name, update=update, convert=False)
    #
    #     data = [(t, i) for t, i in collection_data[("items")]["papers"].items()][::-1]
    #     if article_title != "":
    #         index1 = [i for i in collection_data["items"]["papers"]].index(article_title)
    #         data = [(t, i) for t, i in collection_data[("items")]["papers"].items()][index1:index1 + 1]
    #
    #     note_complete = len(collection_data["items"]["papers"].items())
    #     # Setting up the tqdm iterator
    #     pbar = tqdm(data,
    #                 bar_format="{l_bar}{bar:30}{r_bar}{bar:-30b}",
    #                 colour='green')
    #     if type(specific_section) == str:
    #         print("len ==1")
    #         api = ChatGPT(**self.chat_args)
    #
    #     for keys, values in pbar:
    #
    #         # Dynamically update the description with the current key being processed
    #         index1 = [i for i in collection_data["items"]["papers"]].index(keys)
    #         pbar.set_description(f"Processing index:{index1},paper:{keys} missing:{note_complete} ")
    #
    #         note = values["note"]
    #         id = values['item_id']
    #         pdf = values['pdf']
    #
    #         if note["note_info"] is not None and pdf is not None:
    #             if note["headings"]:
    #                 note_id = [i["note_info"]['note_id'] for i in values['note_info'] if
    #                            i['note_info']["note_info"]['tags'] == "summary_note"]
    #                 # self.schema = self.extract_insert_article_schema(note_id=note_id, save=False)
    #                 # if self.schema:
    #                 #     pdf_title = "PDF_TITLE ATTACHED=" + os.path.split(pdf)[-1] + "\n"
    #                 #     section_dict = {
    #                 #         k: (
    #                 #             f"{pdf_title}Read the provided PDF carefully, paragraph by paragraph, and perform an in-depth section analysis of the section: '{self.clean_h2_title(k)}' in the attached PDF document. Carefully count each paragraph starting from the beginning of this section. For each key finding/idea, reference the specific paragraph numbers (e.g., 'Paragraph 1,' 'Paragraphs 2,3') accompanied by direct quotes from the respective paragraphs to illustrate or support the key points identified. Follow this structure: ```html <h3>Paragraph 1 - [key finding in one short sentence]</h3> <blockquote>'[Direct quote from the first paragraph in the form of a full sentence. The full sentence should be exactly as it is in the PDF, strictly unmodified. Before using it, check for a full match between the sentence and the PDF text]'</blockquote> <h3>Paragraphs 2,3 - [Next Key finding or idea in one short sentence]</h3> <blockquote>'[Direct quote from paragraph 2 in the form of a full sentence. The full sentence should be exactly as it is in the PDF, strictly unmodified. Before using it, check for a full match between the sentence and the PDF text.]'</blockquote> <blockquote>'[Direct quote from paragraph 3.]'</blockquote> [Continue this structure for additional paragraphs or groups of paragraphs, correlating each with its key findings or ideas until the end of the section]``` This methodical approach ensures a structured and precise examination of the section: '{self.clean_h2_title(k)}', organized by the specific paragraphs and their associated key findings or ideas, all supported by direct quotations from the document for a comprehensive and insightful analysis until the end of the provided section. Take your time, and review the final output for accuracy and consistency in HTML formatting and citation-context alignment.\n\nnote1: Direct quotes format must be in the form of one full sentence. The full sentence must be exactly as it is in the PDF, strictly unmodified. Before using it, check for a full match between the sentence and the PDF text. After getting the exact quote that supports your analysis, reference with the author name between ()\nnote2: if numerical references found, create a a href with the footnote inside a sup whose number is the reference. Output format: HTML in a code block.")
    #                 #         for k in self.schema if k not in ["Abstract", "table pf"]
    #                 #     }
    #                 #
    #                 #     note_update.update(section_dict)
    #                 if specific_section and "note_complete" not in note["tags"]:
    #                     note_id = note["note_id"]
    #                     note_update1 = {k: v for k, v in specific_section if k in note["headings"]}
    #                     if type(specific_section) == str:
    #                         if specific_section in note_update1.keys():
    #                             self.specific_section(specific_section=specific_section, pdf=pdf, note_id=note_id,
    #                                                   delete=delete, api=api)
    #                     if type(specific_section) == list:
    #                         specific_section = [k for k in specific_section if k in note["headings"]]
    #                         if specific_section:
    #                             self.specific_section(specific_section=specific_section, pdf=pdf, note_id=note_id,
    #                                                   delete=delete, api=api)
    #                 else:
    #                     print("note headings:", note["headings"])
    #
    #                     note_update1 = {k: v for k, v in note_update.items() if k in note["headings"]}
    #                     print("note_update1:", note_update1)
    #                     print(list(note_update1.keys()))
    #                     if list(note_update1.keys()):
    #                         self.update_multiple_notes(section_prompts=note_update1, pdf=pdf, note_id=note_id)
    #                     if not note_update1.keys():
    #                         note_complete -= 1
    #
    #             elif note["headings"] == []:
    #                 note_complete -= 1
    #         if note["note_info"] is None and pdf is not None:
    #             print("note is None and pdf is None")
    #             note_id = self.create_note(id, pdf)
    #             if note_id:
    #                 if specific_section:
    #
    #                     self.specific_section(specific_section=specific_section, pdf=pdf, note_id=note_id,
    #                                           delete=delete, api=api)
    #                 else:
    #
    #                     self.update_multiple_notes(section_prompts=note_update, note_id=note_id, pdf=pdf)
    #
    #     if note_complete > 0:
    #         return True
    #     if note_complete == 0:
    #         return False



    def update_note_section_fromHtml(self,note_id, updates):



        """
        Update specific sections of a Zotero note by item ID. Sections will only be updated if they currently have no content,
        except for 'Thematic Review', which will append new content to the end.
        """
        # Retrieve the current note content
        note = self.zot.item(note_id)
        if 'data' in note and 'note' in note['data']:
            note_content = note['data']['note']
        else:
            print(f"No note content found for item ID {note_id}")
            return

        updated_content = note_content  # Initialize with the current note content

        # Process the updates
        for section, new_content in updates.items():
            # Regular expression to find the section and its content
            pattern = re.compile(f"({re.escape(section)})(.*?)(<hr>)", re.DOTALL | re.IGNORECASE)
            matches = pattern.findall(updated_content)

            if matches:
                updated_section = f"""{matches[0][0]}{new_content}<hr>"""
                # else:
                #     # If there is existing content and it's not 'Thematic Review', do not update
                #     print(f"Existing content found in section {section}, no update made.")
                #     continue  # Skip to the next section

                # Update the note content with the new section content
                updated_content = updated_content.replace(matches[0][0] + matches[0][1] , updated_section)
            else:
                print(f"Section title '{section}' not found in the note content.")


        # Prepare the updated note for submission to Zotero
        updated_note = {
            'key': note['data']['key'],
            'version': note['data']['version'],
            'itemType': note['data']['itemType'],
            'note': updated_content,
            'tags': note['data'].get('tags', [])
        }
        try:
            # Attempt to update the note in Zotero
            response = self.zot.update_item(updated_note)
            if response:
                print("Note updated successfully.")
            else:
                print("Failed to update the note.")
        except Exception as e:
            print(f"An error occurred during the update: {e}")

    def specific_section(self,specific_section,pdf,api,note_id,delete=False):

        if type(specific_section) == str:
            specific_section = {specific_section: note_update[specific_section]}
        if type(specific_section) == list:
            specific_section = {i: note_update[i] for i in specific_section}

        if not delete:
            if len(specific_section) == 1:
                api.interact_with_page(path=pdf, copy=False)

                self.update_zotero_note_section(pdf_title=pdf,note_id=note_id, api=api, updates=specific_section)
            else:

                self.update_multiple_notes(section_prompts=specific_section, note_id=note_id, pdf=pdf
                                           )
        if delete:
            if type(specific_section) is list:
                for section in specific_section:
                    self.update_zotero_note_section(note_id=note_id, api="api", updates=section,delete=True)
            else:

                self.update_zotero_note_section(note_id=note_id, api="api", updates=specific_section, delete=True)

    def update_all(self,collection_name,article_title="",tag=None,update=True,specific_section=None,delete=False,index=0,pdf=True):
        """
            Iterates over a Zotero collection, updating notes for each item based on predefined rules and external data.

            Parameters:
            - collection_name (str): The name of the Zotero collection to process.
            - index (int, optional): The starting index within the collection to begin processing. Defaults to 0.
            - tag (str, optional): A specific tag to filter items by within the collection. If None, no tag filter is applied. Defaults to None.
            - update (bool, optional): Whether to actually perform updates on the notes. Defaults to True.

            The method applies a sequence of updates to each note in the collection, including extracting and inserting article schemas, cleaning titles, and potentially updating note sections based on external data sources. The updates can be configured via the parameters, and the method tracks the progress and handles exceptions accordingly.

            Note:
            - The method provides feedback via print statements regarding the progress and success of note updates.
            """
        collection_data = self.get_or_update_collection(collection_name=collection_name,update=update,pdf=pdf)

        data =[ (t,i) for t,i in collection_data[("items")]["papers"].items()][::-1]
        if article_title != "":
            index1 = [i for i in collection_data["items"]["papers"]].index(article_title)
            data = [(t, i) for t, i in collection_data[("items")]["papers"].items()][index1:index1+1]

        note_complete = len(collection_data["items"]["papers"].items())
        # Setting up the tqdm iterator
        pbar = tqdm(data,
                    bar_format="{l_bar}{bar:30}{r_bar}{bar:-30b}",
                    colour='green')
        if type(specific_section) == str:
            print("len ==1")
            api = ChatGPT(**self.chat_args)
        for keys, values in pbar:

            # Dynamically update the description with the current key being processed
            index1 = [i for i in collection_data["items"]["papers"]].index(keys)
            pbar.set_description(f"Processing index:{index1},paper:{keys} missing:{note_complete} ")
            note=values["note"]
            id = values['item_id']
            pdf = note['pdf']
            print(note['note_info'] )
            note_id = None
            try:
                note_id = " ".join([i['note_id'] for i in note['note_info'] if
                           "summary_note" in i['tag'] ])
                note_id= None if note_id=="" else note_id
            except Exception as e:
                print('err with note_id: ',e)
                print(note_id)
            # print(pdf)
            print(note_id)
            sections_titles = note["sections"]
            if note_id and pdf:
                print("note_id:", note_id, "pdf:", pdf,sep='\n')
                if note["headings"] :

                    if sections_titles:
                        pass
                        # pdf_title = "PDF_TITLE ATTACHED=" + os.path.split(pdf)[-1] + "\n"
                        # section_dict = {
                        #     k: (
                        #         f"{pdf_title} Read the PDF, especially the section titled '{self.clean_h2_title(k)}'. Number each paragraph from the start, focusing on formatting cues like indentation and spacing. Summarize the main idea of each paragraph in a succint declarative sentence in h3. Reference the paragraph number and include the full paragraph text, highlighting the key statement with <strong> tags in blockquote. Use HTML for structured output: <h3>Paragraph 1 - [Main idea in a form of a short declarative statement here without []]</h3><blockquote>'[Full paragraph with highlighted key statement not enclosed by []]'</blockquote><h3>Paragraphs 2,3 - [Main idea in a form of a short declarative statement here without []]</h3><blockquote>'[Full paragraph with highlighted key statement not enclosed by []]'</blockquote><blockquote>'[Full paragraph with highlighted key statement not enclosed by []]'</blockquote> <!-- Continue for additional paragraphs --> Ensure accuracy by verifying logical flow and formatting consistency.\n\nnote1: follow the instructions between [] \nnote 2: blockquote paragraphs are provided in full, as whole, exactly as it found in the document.\nnote 3:output format: code block html div, I repeat, CODE BLOCK HTML```")
                        #     for k in sections_titles if k not in ["Abstract", "table pf"]
                        # }
                        #
                        # note_update.update(section_dict)

                    if specific_section:

                    # if specific_section and "note_complete" not in note["tags"]:
                        # note_update1 = {k: v for k, v in specific_section if k in note["headings"]}
                        note_update1 = {k: v for k, v in note_update.items() if k==specific_section and k  in note["headings"]}

                        if type(specific_section) == str:
                            print('yes')
                            if specific_section in note_update1.keys():
                                self.specific_section(specific_section=specific_section, pdf=pdf, note_id=note_id,
                                                      delete=delete, api=api)
                        if type(specific_section) == list:
                            specific_section= [k for k in specific_section if k in note["headings"]]
                            if specific_section:
                                self.specific_section(specific_section=specific_section, pdf=pdf, note_id=note_id,
                                                      delete=delete, api=api)
                    if not specific_section:

                        note_update1 = {k: v for k, v in note_update.items() if k in note["headings"]}
                        print("note_update1:",note_update1.keys())

                        if note_update1.keys():
                            self.update_multiple_notes(section_prompts=note_update1,pdf=pdf, note_id=note_id)
                        if not note_update1.keys():
                            note_complete -= 1

                elif  note["headings"] == []:
                    note_complete -=1
            if note_id is None and pdf is not None:

                print("note is None and pdf is None")
                note_id = self.create_one_note(content=note_summary_schema,item_id=id,tag='summary_note')
                if note_id:
                    if specific_section:

                        self.specific_section(specific_section=specific_section, pdf=pdf, note_id=note_id,
                                              delete=delete, api=api)
                    else:

                        self.update_multiple_notes(section_prompts=note_update, note_id=note_id, pdf=pdf)

        if note_complete>0:
            return True
        if note_complete ==0:
            return False


    def update_zotero_note_section(self,pdf_title, note_id="JFHPQ8IX", updates=note_update, api=None,delete=False):
        if api == None:
            api = ChatGPT(**self.chat_args)
        """
    Updates specific sections of a Zotero note by item ID. The content within the specified sections will be replaced with new content.

    Parameters:
    - note_id (str): The unique identifier of the Zotero note to update.
    - updates (dict): A dictionary where keys are section headings and values are the new content to update those sections with.
    - api: An external API object used to generate new content based on the updates.

    This method also handles adding new tags and updating the 'Structure and Keywords' section with unique keywords extracted from the updated content. If the content is successfully updated, it attempts to post the changes back to Zotero.

    Note:
    - The function prints out the result of the operation, indicating success or failure of the update.
    """
        # Retrieve the current note content
        note = self.zot.item(note_id)
        tags = note['data'].get('tags', [])
        if "note_complete" in tags:
            return
        if 'data' in note and 'note' in note['data']:
            note_content = note['data']['note']
        else:
            print(f"No note content found for item ID {note_id}")
            return
        author= self.get_html_info(note_content)
        updated_content = note_content  # Initialize with the current note content
        # Process updates for each section
        for section, new_prompt in updates.items():
            # This pattern looks for the section, captures content until it finds the next <h2>, <h1>, or <hr>
            pattern = re.compile(f'({re.escape(section)})(.*?)(?=<h2>|<h1>|<hr>|$)', re.DOTALL | re.IGNORECASE)
            matches = pattern.search(updated_content)
            new_content =""
            if matches:
                if delete:
                    if "note_complete"  in tags:
                        return
                    else:
                        updated_section = f""

                else:
                    # Generate new content using the API based on the provided prompt
                    if type(new_prompt) == str:

                        new_content = api.send_message(pdf_title+f"\nauthor name ={author}\n"+new_prompt,sleep_duration=self.sleep).strip()
                        while new_content==new_prompt:
                            print("content is equal")
                            if api.os =="win":
                                api.bring_browser_to_foreground()
                            time.sleep(2)
                            new_content =api.copy_message()
                    if type(new_prompt) == list:
                        item_list=[]
                        for item in new_prompt:

                            item_list.append(api.send_message(pdf_title+" "+item,sleep_duration=self.sleep).strip())
                            if item_list[-1]== item:
                                time.sleep(4)
                                item_list[-1] = api.copy_message()
                                print("content is equal")
                        new_content = " ".join(item_list)
                    # self.append_training_data(prompt=new_prompt,expected_response=new_content)

                # Replace the old section content with the new one
                    updated_section = f"{matches.group(1)}{new_content}"
                updated_content = updated_content[:matches.start()] + updated_section + updated_content[matches.end():]
            else:
                print(f"Section title '{section}' not found in the note content.")
        # Check if the content has been updated
        if updated_content != note_content:
            updated_note = {
                'key': note['data']['key'],
                'version': note['data']['version'],
                'itemType': note['data']['itemType'],
                'note': updated_content,
                'tags': tags
            }
            try:
                # Attempt to update the note in Zotero
                response = self.zot.update_item(updated_note)
                if response:
                    print("Note updated successfully.")
                else:
                    print("Failed to update the note.")
            except Exception as e:
                print(f"An error occurred during the update: {e}")
        else:
            print("No changes were made to the note content.")
    def update_multiple_notes(self,section_prompts,note_id,pdf):

        api = ChatGPT(**self.chat_args)
        # if self.chat_args.get("chat_id"):
        if len(section_prompts.keys())>5:
            index=math.ceil(len(section_prompts.keys()) / 2)
            section_to =  list(section_prompts.keys())[index]

            print("section:",section_to)

        api.interact_with_page(path=pdf, copy=False)
        # Assuming thematic_section is a dictionary
        with tqdm(section_prompts.items(), bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}]',
                  colour='blue') as pbar:
            for key, value in pbar:
                if len(section_prompts.keys())>5:
                    if key==section_to:
                        api.interact_with_page(path=pdf, copy=False)

                pbar.set_description(f"Processing section {key}",
                                     )
                pdf_title ="PDF_TITLE ATTACHED="+os.path.split(pdf)[-1]+"\n"

                self.update_zotero_note_section(note_id=note_id, updates={key:value},api=api,pdf_title=pdf_title)
                pbar.update()
                if key=="<h2>1.5 Structure and Keywords</h2>":
                    self.extract_insert_article_schema(note_id=note_id,save=True)
            api.__del__()


    def extract_relevant_h2_blocks(self,note_id):
        """
        Extracts <h2> elements from HTML content, including their opening and closing tags, based on specific conditions
        related to the text immediately following these headings.

        This function iterates over all <h2> elements in the provided HTML content. It checks the text immediately following each <h2>.
        If there is no text immediately following or if the text starts with a specific guideline phrase,
        the <h2> element itself (including its opening and closing tags but excluding any following text)
        is appended to a list.

        Args:
            html_content (str): The HTML content to be processed.

        Returns:
            list: A list of <h2> elements (with opening and closing tags) that meet the specified conditions.
        """
        note = self.zot.item(note_id)
        if 'data' in note and 'note' in note['data']:
            tags = note['data'].get('tags', [])
            note_content = note['data']['note']
        soup = BeautifulSoup(note_content, 'html.parser')

        relevant_h2_blocks = []
        h2_elements = soup.find_all('h2')
        for h2_element in h2_elements:
            # Initialize a variable to iterate through siblings
            next_sibling = h2_element.next_sibling

            # Iterate through siblings until you find a non-empty text or a tag that's not <hr>
            while next_sibling and isinstance(next_sibling, NavigableString) and not next_sibling.strip():
                next_sibling = next_sibling.next_sibling

            # Check if the next_sibling is an <hr> or if there is no significant text following
            if not next_sibling or next_sibling.name == 'hr' or (
                    isinstance(next_sibling, NavigableString) and not next_sibling.strip()):
                relevant_h2_blocks.append(str(h2_element))

        return [i for i in relevant_h2_blocks if i!='<h2>Loose notes</h2>']

    def _get_md_attachment(self, item_id):

        attachments = self.zot.children(item_id, itemType='attachment')
        # Assuming 'attachments' is a list of attachments data similar to what you've shown previously
        attachment_item= [
            attachment
            for attachment in attachments
            if attachment['data'].get('filename', '').endswith('.md')
        ]
        return attachment_item

    def get_children_notes(self, item_id,get_note=None, new_filename='',pdf=True):
        """
        Retrieves and processes child notes for a specified item from the Zotero library.

        This function filters through child notes associated with a specified item. It performs several checks:
        - If more than one note exists, it prints the first two notes.
        - If a note is marked as complete ('note_complete'), it returns immediately with the note's ID and an empty list of headings.
        - If no sections are remaining to be updated and the note is not marked as complete, it updates the note with the 'note_complete' tag.
        - Otherwise, it returns the note ID and the headings of the sections that need to be updated.

        Args:
            item_id (str): The unique identifier of the Zotero library item whose child notes are to be fetched.

        Returns:
            dict or None: A dictionary containing the 'note_id' and 'headings' if there are incomplete notes, otherwise None.
        """
        children=''
        sections_titles = ""
        attachment_item=None
        note_info = []
        # Fetch all children of the specified item
        children = self.zot.children(item_id)
        if pdf:
            new_filename=new_filename + ".pdf"

            attachment_item= [
                child for child in children
                if child['data']['itemType'] == 'attachment' and 'application/pdf' in child['data'].get('contentType', '')]
            attachment_item = attachment_item[0] if attachment_item else None

        if not pdf:
            new_filename=new_filename + ".md"

            attachments = self.zot.children(item_id, itemType='attachment')
            # Assuming 'attachments' is a list of attachments data similar to what you've shown previously
            attachment_item= [
                attachment
                for attachment in attachments
                if attachment['data'].get('filename', '').endswith('.md')
            ]
            print(attachment_item)
            attachment_item = attachment_item[0] if attachment_item else None

        # Define the list of valid tags to check
        valid_tags = ["statements_note", "cited_note", "cited_note_name", "summary", "summary_note","Paragraphs"]
        if get_note:
            valid_tags=[get_note]
        remaining_h2 = None
        notes = [
            child for child in children
            if child['data']['itemType'] == 'note' and any(
                tag in valid_tags for tag in (v for p in child['data']['tags'] for v in p.values())
            )
        ]
        # input([
        #     child for child in children
        #     if child['data']['itemType'] == 'note' and any(
        #         tag in ["Paragraphs"]for tag in (v for p in child['data']['tags'] for v in p.values())
        #     )
        # ])
        # Check the number of notes and print them if more than one
        tags = [tag["tag"] for note in notes for tag in note['data']['tags']]
        pdf = self.get_pdf_path(attachment_item=attachment_item, new_filename=new_filename)
        if notes:
            if get_note:
                return notes[0]['data']["key"]
            # Process each note
            for note in notes:
                note_id = note['data']["key"]
                note_content = note['data']["note"]
                tags_note = [i['tag'] for i in note['data']['tags']]
                note_info.append({"note_id": note_id, "note_content": note_content, "tag": tags_note})
                if "summary_note" in tags_note:
                    remaining_h2 = self.extract_relevant_h2_blocks(note_id=note_id)
                    sections_titles = self.extract_insert_article_schema(note_id=note_id,save=False,html=False)

                # Check if there are no remaining sections and the note is not marked complete
                if not remaining_h2 and "note_complete" not in tags:
                    note['data']['tags'].append({"tag": "note_complete"})
                    self.zot.update_item(note)
                # If there are remaining sections, return them with the note ID
            # If no notes meet the criteria, return None

            return {"note_info": note_info, "pdf": pdf, "headings": remaining_h2, "tags": tags,"sections":sections_titles}
        else:
            return {"note_info": None, "pdf": pdf, "headings": None, "tags": None,"sections":None}

    def extract_unique_keywords_from_html(self, html_text):
        """
        Extracts unique keywords enclosed in <li> tags from the provided HTML text and returns them as a list.
        For the "Affiliations, Countries, and Regions" section, only the countries are extracted, without the context.

        Args:
        - html_text (str): A string containing HTML content.

        Returns:
        - list: A list of unique keywords extracted from the HTML text.
        """

        # Extract the content between <h2>2.4 Structure and Keywords</h2> and the next <h2>
        section_match = re.search(r"<h2>2\.4 Structure and Keywords</h2>(.*?)<h2>", html_text, re.DOTALL)

        if section_match:
            section_content = section_match.group(1)

            # Use regular expression to find all keywords within <li> tags within the section
            keywords = re.findall(r"<li>(.*?)</li>", section_content)

            # Process keywords to extract only the country for the "Affiliations, Countries, and Regions" section
            processed_keywords = []
            for keyword in keywords:
                processed_keywords.append(keyword.strip())

            # Remove duplicates by converting the list to a set, then back to a list
            unique_keywords = list(set(processed_keywords))

            # Generate a list of dictionaries with tags
            tags = [{"tag": tag.lower()} for tag in unique_keywords]

            return tags

        return []



    def extract_insert_article_schema(self,note_id,save=False,html=True):
        """
            Extracts article schema information from the given HTML content and formats it into a list of <h2> tags.

            Parameters:
            - html_content (str): HTML content from which to extract the article schema.

            Returns:
            - A list of strings, each representing an article schema item formatted as an <h2> tag. If the 'Article Schema:' section is not found, returns an empty list.
            """
        # Retrieve the current note content
        note = self.zot.item(note_id)

        if 'data' in note and 'note' in note['data']:
            tags = note['data'].get('tags', [])
            note_content = note['data']['note']
            tags.extend(self.extract_unique_keywords_from_html(note_content))
            soup = BeautifulSoup(note_content, 'html.parser')
            schema_list = []

            article_schema = soup.find('h3', string='TOC:')

            if article_schema:
                # Find the next sibling that is a <ul> tag
                schema_ul = article_schema.find_next_sibling(lambda tag: tag.name == 'ul' and tag.find('li'))

                # Check if a <ul> tag was found
                if schema_ul:
                    schema_items = schema_ul.find_all('li')
                    for item in schema_items:
                        if html:
                            schema_list.append(f'<h2>{item.text.strip()}</h2>')
                        if not html:
                            schema_list.append(f'{item.text.strip()}')

            sections=""
            for section in schema_list:
                section_text = ""
                for i in range(1, 10):  # Assuming you meant from 1 to 7
                    h3_text = f'<h3>Paragraph Number {i} - insert a title</h3>\n'
                    paragraph_text = '<blockquote>Praesentium voluptatum deleniti atque corrupti, quos dolores et quas molestias excepturi sint, qui ratione voluptatem sequi nesciunt. Neque porro quisquam est, qui dolorem ipsum, quia dolor sit, amet, consectetur, adipisci velit, sed quia non numquam eius modi tempora incidunt. Ut enim ad minima veniam, quis nostrum exercitationem ullam corporis suscipit laboriosam, nisi ut aliquid ex ea commodi consequatur.</blockquote>\n'
                    section_text += h3_text + paragraph_text
                sections += section + section_text + "<hr>\n"

            if not save:
                return schema_list
            else:

                item_id = note["data"]["parentItem"]
                cabecalho = generate_cabecalho(zot=self.zot,item_id=item_id)
                content = cabecalho+"<hr>\n<hr>\n"+sections

                self.create_one_note(content=content,item_id=item_id,tag="Paragraphs")
    def process_headings(self, title,update=False):

        headings_dict_file = f"Zotero_module/Data/book_data/{title}_dict.pickle"
        def create_prompts_dict(headings, prompts_list):
            prompts_dict = {}
            for heading in headings:
                for prompt_item in prompts_list:
                    if heading.startswith(prompt_item["type"].capitalize()):
                        identifier = heading.split()[1].replace(':', '')
                        prompt = prompt_item["prompt"].format(identifier, identifier)
                        prompts_dict[heading] = prompt
                        break
            return prompts_dict
        headings = self.extract_headings(update=update,title=title)
        # Check if headings_dict.pickle exists or update is required
        if update or not os.path.exists(headings_dict_file):
            dici = create_prompts_dict(headings=headings, prompts_list=book)
            with open(headings_dict_file, 'wb') as f:
                pickle.dump(dici, f)
        else:
            with open(headings_dict_file, 'rb') as f:
                dici = pickle.load(f)

        self.generate_book_content(dici=dici,title=title)

        return dici

    def extract_headings(self,title,update=False):
        headings_file = f"Zotero_module/Data/book_data/{title}_list.pickle"
        html_content = ""
        # Check if headings.pickle exists or update is required
        if update or not os.path.exists(headings_file):
            api = ChatGPT(**self.chat_args)

            book_info = ", ".join([f"'{str(k)}': '{str(v)}'" for k, v in title.items()])
            bar = Bar('Generating Chapters',
                      max=5,
                      suffix='%(percent)d%% - %(elapsed_td)s',  # Shows percentage and elapsed time
                      fill='█',
                      empty='-',
                      bar_prefix=' [',
                      bar_suffix='] ',
                      color='green')


            for n in range(5):
                message = f"{book_info}\n {initial_book}\nPlease provide Chapter {n + 1}"
                bar.message="generating chapter " + str(n + 1)
                html_content += api.send_message(message=message, sleep=self.sleep) + "\n"
            soup = BeautifulSoup(html_content, 'html.parser')
            headings = [heading.text.strip() for heading in soup.find_all(['h2', 'h3', 'h4', 'h5'])]
            api.delete_quit()
            with open(headings_file, 'wb') as f:
                pickle.dump(headings, f)
            return headings
        else:

            with open(headings_file, 'rb') as f:
                headings = pickle.load(f)
                return headings

    def generate_book_content(self,dici,title):
        book_file =f"Zotero_module/Data/book_data/book_{title}.html"
        api = ChatGPT(**self.chat_args)
        with (tqdm(total=len(dici.keys()), bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}]',
                   colour='green') as pbar):
            for key, value in dici.items():
                pbar.set_description("processing " + key)
                prompt = key.replace(":", " =") + "\n" + value
                # Assuming api is a pre-initialized ChatGPT API client instance within the class
                html_content= api.send_message(message=prompt,sleep_duration=self.sleep)  # Simulated API call


                # Append the resulting HTML content to the file
                with open(book_file, "a+", encoding="utf-8") as fp:
                    fp.write(html_content + "\n\n")  # Adding a newline for separation between entries
    def creating_training_data_from_statements(self,collection_name,update=True):
        collection_data = self.get_or_update_collection(collection_name=collection_name, update=update)
        data = [(t, i) for t, i in collection_data["items"]["papers"].items()]
        # Setting up the tqdm iterator
        pbar = tqdm(data,
                    bar_format="{l_bar}{bar:30}{r_bar}{bar:-30b}",
                    colour='green')

        for keys, values in pbar:
            # Dynamically update the description with the current key being processed
            index1 = [i for i in collection_data["items"]["papers"]].index(keys)
            pbar.set_description(f"Processing index:{index1},paper:{keys}  ")

            id = values['item_id']
            pdf = values['pdf']
            tags = values['note']["tags"] or []
            reference = "Author=" + (values["reference"] or "")
            note = values["note"]["note_info"]
            note_info = [ note_content.note_content for note_content in note if note_content["tag"]=="statement" ]

    def multilple_prompts(self,api,sections,pdf="",content="", prompt=None, tag="",reference=None, follow_up=True,training_instructions=""):
        if api == "":
            self.chat_args["chat_id"] = tag
            api = ChatGPT(**self.chat_args)

        if pdf:
            api.interact_with_page(path=pdf, copy=False)

        if prompt is not None:
            if type(prompt) == list:
                print("this is a list")

                for prompts in prompt:
                    message = api.send_message(message=prompts + "\n" + reference, sleep_duration=self.sleep)
                    # self.creating_training_data(filepath="Trainining_summary",system_content=training_instructions,assistant_response=message,user_content=prompts)
                    content += message
            if type(prompt) == str:
                if sections is None:
                    content = api.send_message(message=prompt, sleep_duration=self.sleep)
                if sections:
                    for section in sections:
                        content += api.send_message(message=f"section ={section} {reference}\n {prompt}", sleep_duration=self.sleep)

        time.sleep(5)
        api.open_new_tab(open_new=False, close=True)
        return content
    def create_one_note(self,content="", item_id="", collection_id="", tag="",beginning=False
                        ):

        new_note=''

        cabecalho = generate_cabecalho(zot=self.zot,item_id=item_id)
        new_content =  f'<html><head><title>{tag.strip()}</title><style>body{{font-family:"Segoe UI",Tahoma,Geneva,Verdana,sans-serif;background-color:#f0f2f5;color:#333;margin:0;padding:20px;}}.container{{max-width:800px;margin:0 auto;background-color:#fff;padding:30px;border-radius:10px;box-shadow:0 4px 8px rgba(0,0,0,0.1);line-height:1.6;}}h1{{font-size:28px;color:#2c3e50;margin-bottom:20px;border-bottom:2px solid #e67e22;padding-bottom:10px;}}.cabecalho{{font-size:16px;font-weight:bold;color:#555;margin-bottom:20px;padding:10px;background-color:#f9f9f9;border-left:4px solid #3498db;}}.content{{font-size:16px;color:#444;margin-top:20px;line-height:1.8;}}.content p{{margin-bottom:15px;}}.content ul{{list-style-type:disc;margin-left:20px;}}.content li{{margin-bottom:10px;}}.footer{{margin-top:30px;font-size:14px;color:#777;text-align:center;border-top:1px solid #e1e1e1;padding-top:10px;}}</style></head><body><div class="container"><h1>{tag}</h1><div class="cabecalho">{cabecalho}</div><div class="content">{content}</div></div></body></html>' if beginning==False else content

        # Create the new note
        if item_id:
            new_note = self.zot.create_items([{
                "itemType": "note",
                'parentItem': item_id,
                "note": new_content,
                'tags': [ {"tag": tag}]

            }])
        if collection_id:
            new_note = self.zot.create_items([{
                "itemType": "note",
                'collections': [collection_id],
                "note": content,
                'tags': [ {"tag": tag}]

            }])

        print(new_note)
        new_note_id = new_note['successful']['0']['data']['key']
        if new_note_id:
            note = self.zot.item(new_note_id)
            note_content = note['data']['note']

            # Update the note content with the new note ID
            updated_content = note_content.replace(f'<em>@{item_id}</em><br>',
                                                   f'<em>@{item_id}</em><br><em>Note ID: {new_note_id}</em><br>')

            updated_note = {
                'key': note['data']['key'],
                'version': note['data']['version'],
                'itemType': note['data']['itemType'],
                'note': updated_content,
                'tags': [{"tag": "summary_note"}]
            }
            time.sleep(15)
            try:
                # Attempt to update the note in Zotero
                response = self.zot.update_item(updated_note)
                if response:
                    print("Note updated successfully.")
                    return new_note_id
                else:
                    print("Failed to update the note.")
            except Exception as e:
                print(f"An error occurred during the update: {e}")

    def creating_note_from_batch(self):
        batch_id = get_batch_ids()['id']
        results = read_or_download_batch_output(batch_id=batch_id)
        if results is None:
            print("No results available.")
            return

            # Read the content of the downloaded batch output file
        with open(results, 'r', encoding='utf-8') as file:
            messages_by_id_tag = defaultdict(str)
            for line in file:
                # Parse the JSON line
                result = json.loads(line)

                # Extract the custom_id and split it
                custom_id = result['custom_id']
                item_id, tag,page = custom_id.split('-')[0], custom_id.split('-')[1], custom_id.split('-')[-1]
                # Extract the message
                messages = result['response']['body']['choices'][0]['message']['content'].replace("</blockquote>",
                                                            f"(p.{int(page) + 1})</blockquote>")
                # Accumulate the message content in the dictionary
                messages_by_id_tag[f"{item_id}-{tag}"] += messages
            for id_tag, message in messages_by_id_tag.items():
                item_id, tag = id_tag.split('-')

                # Call the create_one_note method with the extracted variables
                self.create_one_note(content=message, item_id=item_id, tag=tag)
    def statements_citations(self,section,collection_name,update=True,chat=False,batch=False,store_only=True,training_instructions="",follow_up=False):
        if chat:
            tag =list(section.keys())[0]
            prompt=section[tag]
            self.chat_args["chat_id"] = tag
            api = ChatGPT(**self.chat_args)


        # # api=""

        """
            Iterates over a Zotero collection, updating notes for each item based on predefined rules and external data.

            Parameters:
            - collection_name (str): The name of the Zotero collection to process.
            - index (int, optional): The starting index within the collection to begin processing. Defaults to 0.
            - tag (str, optional): A specific tag to filter items by within the collection. If None, no tag filter is applied. Defaults to None.
            - update (bool, optional): Whether to actually perform updates on the notes. Defaults to True.

            The method applies a sequence of updates to each note in the collection, including extracting and inserting article schemas, cleaning titles, and potentially updating note sections based on external data sources. The updates can be configured via the parameters, and the method tracks the progress and handles exceptions accordingly.

            Note:
            - The method provides feedback via print statements regarding the progress and success of note updates.
            """
        collection_data = self.get_or_update_collection(collection_name=collection_name,update=update)
        data =[ (t,i) for t,i in collection_data["items"]["papers"].items() ]
        batch_requests = []
        # Setting up the tqdm iterator
        pbar = tqdm(data,
                    bar_format="{l_bar}{bar:30}{r_bar}{bar:-30b}",
                    colour='green')

        for keys, values in pbar:
            # Dynamically update the description with the current key being processed
            index1 = [i for i in collection_data["items"]["papers"]].index(keys)
            pbar.set_description(f"Processing index:{index1},paper:{keys}  ")

            id = values['item_id']
            pdf = values['pdf']
            tags =values['note']["tags"] or []
            reference ="Author=" +  (values["reference"] or "")

            section_titles = values['note']["sections"]

            if tag not in tags and  pdf is not None and section_titles is not None and section_titles!="[]":
                if chat:
                    if tag=="Author Cited":
                        reference = ""

                    content = self.multilple_prompts(prompt=prompt, api=api,reference=reference, follow_up=True,tag=tag,
                                                     pdf=pdf,sections=section_titles)

                    self.create_one_note(content=content,item_id=id,tag=tag)

                else:
                    result = process_pdf(file_path=pdf, prompt=prompt, id=id, tag=tag, reference=reference,
                                         batch=batch,store_only=store_only)
                    if batch and result:
                        batch_requests.extend(result)
                    elif result:
                        self.create_one_note(item_id=id, tag=tag, content=result, reference=reference,follow_up=follow_up)

        if batch and batch_requests and not store_only:
            file_name = write_batch_requests_to_file(batch_requests,
                                                     file_name=rf"/Files/Batching_files\{collection_name}_batch.jsonl")
            batch_input_file_id = upload_batch_file(file_name)
            batch_id = create_batch(batch_input_file_id)
            check_save_batch_status(batch_id)

        else:
            print("[DEBUG] Batch processing failed or no results returned.")


    def delete_duplicates(self):
        # Initialize Zotero library

        # Retrieve items tagged with 'duplicates'
        tagged_items = self.zot.everything(self.zot.items(tag='duplicates'))
        print(f"Total items retrieved with 'duplicates' tag: {len(tagged_items)}")

        # Group items by normalized title
        grouped_items = {}
        for item in tagged_items:
            if 'title' in item['data']:
                norm_title = self.normalize_title(item['data']['title'])
                if norm_title in grouped_items:
                    grouped_items[norm_title].append(item)
                else:
                    grouped_items[norm_title] = [item]

        # Identify duplicates and delete all but the oldest
        for title, duplicates in grouped_items.items():
            if len(duplicates) > 1:
                print(f"Found {len(duplicates)} duplicates for title '{title}'")
                # Determine the oldest item by 'dateAdded'
                oldest = min(duplicates, key=lambda x: self.parse_date(x['data']['dateAdded']))
                # Delete all items except the oldest
                for duplicate in duplicates:
                    if duplicate != oldest:

                        self.zot.delete_item(duplicate)
                        print(f"Deleted item: {duplicate['data']['title']} - Added on {duplicate['data']['dateAdded']}")
                    else:
                        print(
                            f"Keeping oldest item: {oldest['data']['title']} - Added on {oldest['data']['dateAdded']}")

    def fetch_details(self, main_collection_name, update=False, fetch_type='items'):
        filename = f'Zotero_module/Data/collections_data/{main_collection_name}_{fetch_type}.json'
        if os.path.exists(filename) and not update:
            with open(filename, 'r') as file:
                return json.load(file)

        # Fetch all collections and find the main collection by its name
        collections = self.zot.everything(self.zot.collections())
        main_collection = next(
            (coll for coll in collections if coll['data']['name'].lower() == main_collection_name.lower()), None)
        if not main_collection:
            print(f"No collection found with the name '{main_collection_name}'.")
            return []

        all_details = []
        self.fetch_recursively(main_collection['key'], all_details, fetch_type)

        # Store the results in a file
        with open(filename, 'w') as file:
            json.dump(all_details, file, indent=4)
            print("all details=",all_details)
        return all_details

    def fetch_recursively(self, collection_key, details_list, fetch_type):
        if fetch_type == 'items':
            items = self.zot.everything(self.zot.collection_items(collection_key))
            filtered_items = [{'title': item['data']['title'], 'key': item['data']['key']}
                              for item in items if
                              'title' in item['data'] and item['data']['itemType'] not in ['attachment', 'note']]
            details_list.extend(filtered_items)
        elif fetch_type == 'collections':
            subcollections = self.zot.everything(self.zot.collections_sub(collection_key))
            collection_details = [{'title': sub['data']['name'], 'key': sub['key']}
                                  for sub in subcollections]
            details_list.extend(collection_details)

        # Recursively process subcollections for both items and collections
        subcollections = self.zot.everything(self.zot.collections_sub(collection_key))
        for subcol in subcollections:
            self.fetch_recursively(subcol['key'], details_list, fetch_type)

    def process_collections_file(self, main_collection,update=False,fetch_type='items'):
        data = self.fetch_details(main_collection, update=update, fetch_type=fetch_type)

        # data = [k for k in json.load(file) if k["items"]!=[]]
        pbar = tqdm(data,
                    bar_format="{l_bar}{bar:30}{r_bar}{bar:-30b}",
                    colour='green')

        for collection_info in pbar:
            collection_name = collection_info['collection_name']
            collection_key = collection_info.get('collection_key', '')
            pbar.set_description(f"Processing collection {collection_name}  ")


            if not collection_key:
                collection_data = {'name': collection_name}
                new_collection = self.zot.create_collections([collection_data])
                if new_collection and 'successful' in new_collection and '0' in new_collection['successful']:
                    collection_key = new_collection['successful']['0']['key']
                    print(f"Created collection '{collection_name}' with key '{collection_key}'")
                else:
                    print(f"Failed to create collection '{collection_name}', API response: {new_collection}")
                    continue
            collection_items = [item['data']['key'] for item in self.zot.everything(self.zot.collection_items(collection_key))]
            item_keys = [item['item_key'] for item in collection_info['items'] if item['item_key'] not in collection_items]

            if item_keys:
                item_dicts = [self.zot.item(key) for key in item_keys]

                try:
                    config_handler.set_global(spinner='dots_waves2', bar='bubbles', theme='smooth')

                    # Determine the maximum width for the progress bar to ensure it fits in the display area
                    max_bar_width = 30  # You can adjust this value based on your terminal size or preferences

                    # Initialize the alive_progress bar with enhanced style, force_tty=True, and a constrained width
                    with alive_bar(len(item_dicts), force_tty=True, title="Sleeping...", bar="blocks",
                                   spinner="dots_waves2",
                                   length=max_bar_width) as bar:
                        for item_dict in item_dicts:
                            time.sleep(2)
                            success = self.zot.addto_collection(collection=collection_key, payload= item_dict)
                            bar.text(f"Added items to collection '{collection_name}' with key '{collection_key}'.")
                        if not success:
                            print(f"Failed to add items to collection '{collection_name}' with key '{collection_key}'.")

                except Exception as e:
                    print(f"Exception when adding items to '{collection_name}': {e}")


    def getting_infoFromJson(self,filename):

        with open(filename, 'r') as file:
            data =json.load(file)
        api = ChatGPT(**self.chat_args)
        for key,value in data.items():
            prompt =(f"I am extracting my style to be replicable. Read the document and concerning {key}, meaning {value}. Provide me a paragraph example which illustrates the writing style, which should be always unique from the previous ones."
                     f"Your logic will be:read the word document carefully,extract the style concerning {key} , check example uniqueness and provide me a dict file in the format of {key}:example directly extracted from the word document.\nno additional information, provide me only the dict in block code")
            response =ast.literal_eval(
                                                    api.interact_with_page(prompt=prompt,
                                                                           path=r"C:\Users\luano\OneDrive - University College London\Research\Literature Review\word\Luano_Rodrigues_MC feedback Feb 2023.docx",
                                                                           copy=True))
            file2 ="writing_style.json"
            # Check if the file exists
            if Path(file2).is_file():
                # If the file exists, read its contents
                with open(file2, 'r') as file:
                    data = json.load(file)
            else:
                # If the file doesn't exist, start with an empty dictionary
                data = {}

            # Append the new data to the existing dictionary
            data.update(response)

            # Write the updated dictionary back to the JSON file
            with open(file2, 'w') as file:
                json.dump(data, file, indent=4)
            print(key,value)
    def getting_infoFromJson(self,filename):

        with open(filename, 'r') as file:
            data =json.load(file)
        api = ChatGPT(**self.chat_args)
        for key,value in data.items():
            prompt =(f"I am extracting my style to be replicable. Read the document and concerning {key}, meaning {value}. Provide me a paragraph example which illustrates the writing style, which should be always unique from the previous ones."
                     f"Your logic will be:read the word document carefully,extract the style concerning {key} , check example uniqueness and provide me a dict file in the format of {key}:example directly extracted from the word document.\nno additional information, provide me only the dict in block code")
            response =ast.literal_eval(
                                                    api.interact_with_page(prompt=prompt,
                                                                           path=r"C:\Users\luano\OneDrive - University College London\Research\Literature Review\word\Luano_Rodrigues_MC feedback Feb 2023.docx",
                                                                           copy=True))
            file2 ="writing_style.json"
            # Check if the file exists
            if Path(file2).is_file():
                # If the file exists, read its contents
                with open(file2, 'r') as file:
                    data = json.load(file)
            else:
                # If the file doesn't exist, start with an empty dictionary
                data = {}

            # Append the new data to the existing dictionary
            data.update(response)

            # Write the updated dictionary back to the JSON file
            with open(file2, 'w') as file:
                json.dump(data, file, indent=4)
            print(key,value)

    def update_quotes(self, note_id, pdf, author, stop_words):
        # ask in the structure section to get patters of number of page, water marks... to be cleaned after
        note = self.zot.item(note_id)
        if 'data' in note and 'note' in note['data']:
            note_content = note['data']['note']
            soup = BeautifulSoup(note_content, 'html.parser')

            # Locate the <h1> section entitled "3. Summary"
            section_h1 = soup.find('h1', string='3. Summary')
            if not section_h1:
                raise ValueError("There is no section titled '3. Summary'")

            # Directly modifying blockquotes following this section
            blockquotes = section_h1.find_all_next('blockquote')
            for blockquote in blockquotes:
                original_text = blockquote.get_text(strip=True)
                processed_text = Dc.extract_paragraphs_and_footnotes(pdf_path=pdf, quote=original_text, author=author,
                                                                     stop_words=stop_words)
                blockquote.clear()  # Clear existing content
                blockquote.append(processed_text if processed_text else original_text)  # Append the new processed text
                print(f"Updated blockquote: {blockquote}")

            # Serialize the modified soup to HTML string
            updated_note_content = str(soup)
            updated_note = {
                'key': note['data']['key'],
                'version': note['data']['version'],
                'itemType': note['data']['itemType'],
                'note': updated_note_content,
                'tags': note['data'].get('tags', [])
            }

            # Update the note in Zotero
            try:
                response = self.zot.update_item(updated_note)
                if response:
                    print("Note updated successfully.")
                else:
                    print("Failed to update the note.")
            except Exception as e:
                print(f"An error occurred during the update: {e}")
            return response

    def find_or_create_collection_by_name(self, collection_name):
        """
        Finds or creates the collection key by the collection name in Zotero.

        Args:
            collection_name (str): The name of the collection to find or create.

        Returns:
            str: The key of the collection.
        """
        collections = self.zot.collections()
        for collection in collections:
            if collection['data']['name'].lower() == collection_name.lower():
                return collection['key']

        # Create a new collection if it does not exist
        collection_data = {'name': collection_name}
        new_collection = self.zot.create_collections([collection_data])
        if new_collection and 'successful' in new_collection and '0' in new_collection['successful']:
            collection_key = new_collection['successful']['0']['key']
            print(f"Created collection '{collection_name}' with key '{collection_key}'")
            return collection_key
        else:
            raise Exception(f"Failed to create collection '{collection_name}', API response: {new_collection}")

    def attach_file_to_item(self, parent_item_id, file_path,tag_name):
        """
        Attaches a file to an existing Zotero item and prints the attachment's ID.

        Args:
            parent_item_id (str): The ID of the item to attach the file to.
            file_path (str): The path to the file to attach.

        Returns:
            None
        """
        attch= self._get_md_attachment(item_id=parent_item_id)
        if not attch:
            file_name = os.path.basename(file_path)
            file_title, file_ext = os.path.splitext(file_name)

            # Only proceed if the file is a Word or PDF document
            try:
                # Attach the file to the specified item and capture the response
                response = self.zot.attachment_simple([file_path], parentid=parent_item_id)

                # Check if the attachment was successful or unchanged but still present
                attachment_key = None
                if 'successful' in response and len(response['successful']) > 0:
                    attachment_key = next(iter(response['successful'].values()))['key']
                    print(f"File {file_name} attached successfully. Attachment ID: {attachment_key}")
                elif 'unchanged' in response and len(response['unchanged']) > 0:
                    attachment_key = response['unchanged'][0]['key']
                    print(f"File {file_name} was already attached. Attachment ID: {attachment_key}")

                if attachment_key:
                    # Fetch the existing attachment item
                    attachment_item = self.zot.item(attachment_key)
                    # Append or update the tag
                    existing_tags = {tag['tag'] for tag in attachment_item['data']['tags']}
                    if tag_name not in existing_tags:
                        attachment_item['data']['tags'].append({'tag': tag_name})
                        self.zot.update_item(attachment_item)
                        print(f"Tag '{tag_name}' added to attachment ID: {attachment_key}")
                    else:
                        print(f"Tag '{tag_name}' already exists for this attachment.")

            except zotero_errors.HTTPError as e:
                print(f"Error uploading attachment or adding tag for file '{file_name}': {e}")
            except Exception as e:
                print(f"Unexpected error for file '{file_name}': {e}")
        else:
            print(f"Skipped non-document file: {parent_item_id}")

    def create_item_with_attachment(self, file_path, collection_key):
        """
        Creates a Zotero item with an attachment and adds it to a collection.

        Args:
            file_path (str): The path to the file to attach.
            collection_key (str): The key of the collection to add the item to.

        Returns:
            None
        """
        # Get file name and extension
        file_name = os.path.basename(file_path)
        file_title, file_ext = os.path.splitext(file_name)

        # Only proceed if the file is a Word or PDF document
        if file_ext.lower() in ['.pdf', '.doc', '.docx']:
            # Create a basic item (e.g., document)
            item_template = self.zot.item_template('document')
            item_template['title'] = file_title
            item_template['creators'] = [{'creatorType': 'author', 'firstName': 'Anonymous', 'lastName': ''}]
            item_template['tags'] = [{'tag': 'attachment'}]  # You can customize tags if needed
            item_template['collections'] = [collection_key]

            try:
                # Add the item to Zotero
                created_item = self.zot.create_items([item_template])
                print(f"Created item response: {created_item}")

                if 'successful' in created_item and '0' in created_item['successful']:
                    item_id = created_item['successful']['0']['key']
                    # Attach the file to the item
                    self.zot.attachment_simple([file_path], parentid=item_id)
                    print(f"Item with attachment created: {file_name} and added to collection {collection_key}")
                else:
                    print(f"Failed to create item for file '{file_name}': {created_item}")
            except zotero_errors.HTTPError as e:
                print(f"Error uploading attachment for file '{file_name}': {e}")
            except Exception as e:
                print(f"Unexpected error for file '{file_name}': {e}")
        else:
            print(f"Skipped non-document file: {file_name}")

    def process_files_in_directory(self, directory_path, collection_name):
        """
        Processes files in a directory, creating Zotero items with attachments
        and adding them to a specified collection.

        Args:
            directory_path (str): The path to the directory containing files.
            collection_name (str): The name of the collection to add items to.

        Returns:
            None
        """
        try:
            collection_key = self.find_or_create_collection_by_name(collection_name)

            for root, dirs, files in os.walk(directory_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    self.create_item_with_attachment(file_path, collection_key)
        except Exception as e:
            print(f"Failed to process directory '{directory_path}': {e}")
    def summary_gpt(self,collection_name='Law and evidence',update=False):
        api = ChatGPT(**self.chat_args)
        dir=r"C:\Users\luano\OneDrive - University College London\Obsidian\Thesis\Paragraphs"
        collection_data = self.get_or_update_collection(collection_name=collection_name, update=update)
        dir_path = Path(dir)
        md_files = list(dir_path.rglob("*.md"))
        md_files = [str(file) for file in md_files]
        data=None
        filepath=None
        item_ids = [i['item_id'] for t, i in collection_data[("items")]["papers"].items()]
        for item_id in item_ids:

            metadata = generate_cabecalho(zot=self.zot, item_id=item_id, dict_response=True, links=False)
            print([os.path.split(i)[-1].replace('.md','') for i in md_files])
            print(metadata['citation_key'] + ".md")

            if metadata['citation_key'] in [os.path.split(i)[-1].replace('.md','') for i in md_files]:
                filepath = r"C:\Users\luano\OneDrive - University College London\Obsidian\Thesis\Paragraphs" + "\\" + \
                           "summary_"+metadata['citation_key'] + ".md"

                # Write each dictionary as a new line in the file
                for prompt in note_update.values():
                    file=filepath = r"C:\Users\luano\OneDrive - University College London\Obsidian\Thesis\Paragraphs" + "\\"+metadata['citation_key'] + ".md"
                    data=""
                    data += api.interact_with_page(path=file,prompt=prompt)
            if data and filepath:
                with open(filepath, "w", encoding='utf-8') as md_file:
                    md_file.write(data)
                    self.attach_file_to_item(parent_item_id=item_id, file_path=filepath, tag_name='md_summaries')
    def creating_training_data_gpt(self,file_path,data_list):
        api = ChatGPT(**self.chat_args)
        """
            Append a list of dictionaries to a JSONL file, creating the file if it does not exist.

            Parameters:
            - file_path (str): Path to the JSONL file.
            - data_list (list): List of dictionaries to be appended to the file.
            """
        # Check if the file exists
        file_exists = os.path.isfile(file_path)

        # Open the file in append mode if it exists, otherwise it will create it
        with open(file_path, 'a') as file:
            # If the file did not exist and is newly created, we don't need to prepend a newline
            if file_exists:
                # Add a newline before appending if the file already existed
                file.write('\n')

            # Write each dictionary as a new line in the file
            for entry in data_list:
                numerical =False
                style =entry.get('objective')
                description = str(entry.get('examples'))
                if style =="To demonstrate a variety of numerical citation styles across different academic disciplines":
                    numerical =True

                for i in range(13):

                    more = "Great. provide me with more entries in the same format. " if i>0 else ""
                    note=f"note:2 the notes and comments can range from {(i*20)+1} to {20*(i+1)} if no foonotes, ignore this range. do not output only the first 20 foonotes." if numerical else "note 2:Provide a great and different range of examples"
                    message=f"""    
                    {more}I need your help to create 20 dictionary entries formatted specifically for a JSONL file to {style} .\n Each entry should include a unique reference identifier, numerical or author year,exactly as found in a simulated paper example (smith,2018) or [1]; the preceeding short text indicating how one might introduce the source in an academic paper, and a full bibliographic citation formatted according to the Chicago style or a comment or " ". This is to simulate real papers, you can search on the internet. These entries should cover a variety of subjects including history, literature, and the arts to reflect a broad range of topics.
                    For small example:```python {description}```
                    ensure the output is in a code block python list with dicts in one line appropriate for jsonl file. \n note 1: the academic papers subject is international relations and cyberspace\n {note} \nnote:3 verify if it is a valid python list before outputting.
                    """
                    data = eval(api.send_message(message=message))
                    [file.write(json.dumps(dici) + '\n') for dici in data]  # Append line to file with a newline character
    def paragraphs_reports(self,collection_name,type_collection,n_clusters=None,report='raw', update=False):
        # note = values["note"]
        # #         id = values['item_id']
        # #         pdf = values['pdf']


        def clean_headings(heading):
            stop_words = [
                'introduction', 'conclusion', 'abstract', 'summary', 'notes', 'references', 'bibliography',
                'background', 'discussion', 'methodology', 'results', 'analysis', 'findings', 'acknowledgments',
                'appendix', 'introduction to', 'overview', 'related work', 'literature review', 'further research',
                'future work', 'case study', 'preface', 'contents', 'scope', 'limitations', 'problems',
                'recommendations',
                'introduction and background', 'concluding remarks', 'general discussion', 'discussion and conclusion',
                'part i', 'part ii', 'part iii', 'concluding thoughts'
            ]

            # Remove Roman numerals or numbered listings like "I.", "1.", "part i", etc.
            cleaned_heading = re.sub(r'^(part\s*\w+|\d+\.\s*|[IVXLCDM]+\.\s*)', '', heading,
                                     flags=re.IGNORECASE).strip()

            # Skip headings that contain more than two colons
            if cleaned_heading.count(':') > 2:
                return None

            # Convert heading to lowercase and check for stop words
            cleaned_heading = cleaned_heading.lower()

            # Skip if cleaned heading starts with or contains a stop word
            if any(cleaned_heading.startswith(word) for word in stop_words) or any(
                    f":{word}" in cleaned_heading for word in stop_words):
                return None

            return cleaned_heading

        dquadrant_handler = QdrantHandler()
        collection_data = self.get_or_update_collection(collection_name=collection_name, update=update)


        if report=='raw':
            # search_handler = QdrantHandler(qdrant_url="http://localhost:6333")


            data = [i['item_id'] for t, i in collection_data[("items")]["papers"].items()]
            collection_list = [f'paper_{collection_name}' for collection_name in data]
            clusters = dquadrant_handler.cluster_paragraphs(collection_names=collection_list, n_clusters=n_clusters)

            write_and_export_sections(clusters=clusters)

        if report=='report 1':
        #
            # sections=[]
            # data = [i['note']['note_info'] for  t, i in collection_data[("items")]["papers"].items() ]
            #
            # for notes in data:
            #     if notes:
            #         for notes_info in notes:
            #             if notes_info:
            #                 soup = BeautifulSoup(notes_info['note_content'], 'html.parser')
            #                 h2_tags =[ clean_headings(h2.get_text()) for h2 in soup.find_all('h2') if clean_headings(h2.get_text()) ]
            #                 sections.extend(h2_tags)
            #
            # # grouping_themes =call_openai_api(function='grouping_sections',
            # #                                  data=sections,
            # #                                  id='',
            # #                                  model='gpt-4o-2024-08-06'
            # #                                  )
            # # Grouping collection sections
            # grouping_themes = {'themes': [{'theme': 'Cyber Attribution Frameworks and Processes', 'outline': [{'title': 'Deconstructing Cyber Attribution: A Proposed Framework and Lexicon', 'level': 'H1'}, {'title': 'Cyber Attribution in Scholarly and Policy Debate', 'level': 'H1'}, {'title': 'Deconstructing (and Reconstructing) Cyber Attribution', 'level': 'H1'}, {'title': 'Attribution Processes Today', 'level': 'H1'}, {'title': 'New Developments in Advancing Attribution', 'level': 'H1'}, {'title': 'Institutionalizing Transnational Attribution', 'level': 'H1'}, {'title': 'The Practice and Purposes of Attribution', 'level': 'H1'}, {'title': 'Designing Attribution', 'level': 'H1'}, {'title': 'A New Model for Attribution', 'level': 'H1'}, {'title': 'Technical Cyber Attribution', 'level': 'H1'}]}, {'theme': 'Legal Aspects of Cyber Attribution', 'outline': [{'title': 'The Role of Cyber Attribution in Deterrence and Accountability', 'level': 'H1'}, {'title': 'Legal Deficiencies That Encourage Ill-Substantiated Public Attribution', 'level': 'H1'}, {'title': 'The Law of Attribution', 'level': 'H1'}, {'title': 'Legal Challenges in Attributing an Unlawful Cyber Intrusion', 'level': 'H1'}, {'title': 'Prospects for International Legal Regulation', 'level': 'H1'}, {'title': 'Cyber Armed Attacks and Self-Defense', 'level': 'H1'}, {'title': 'Attribution of State Responsibility in Cyberspace', 'level': 'H1'}, {'title': 'The Tallinn Manual and State Responsibility', 'level': 'H1'}, {'title': 'Complying with International Law on Attribution: The Russia DNC Hack', 'level': 'H1'}, {'title': 'The International Law Problems with Countermeasures in Cyber', 'level': 'H1'}, {'title': 'Assessing the State of Attribution Law', 'level': 'H1'}, {'title': 'The National Security Implications of the International Law on Attribution', 'level': 'H1'}]}, {'theme': 'Evidentiary Standards and Challenges', 'outline': [{'title': 'Advantages and Difficulties of Regulating Evidentiary Requirements', 'level': 'H1'}, {'title': 'Establishment of Evidentiary Rules via Customary International Law', 'level': 'H1'}, {'title': 'Three Lenses to Interrogate Public Attribution', 'level': 'H1'}, {'title': 'Burden of Proof', 'level': 'H1'}, {'title': 'The Standard of Proof', 'level': 'H1'}, {'title': 'Means of Proof of Evidence', 'level': 'H1'}, {'title': 'Evidentiary Issues in the Context of Cyber Operations', 'level': 'H1'}, {'title': 'Cyber-Attacks and Evidentiary Difficulties: Estonia and Georgia', 'level': 'H1'}, {'title': 'Evidentiary Standards Before the International Court of Justice', 'level': 'H1'}, {'title': 'Possible Means to Address the Evidentiary Dilemma in Cyberspace', 'level': 'H1'}, {'title': 'The International Law of Evidence', 'level': 'H1'}, {'title': 'Burden of Proof and Cyber Operations', 'level': 'H1'}, {'title': 'Standard of Proof and Cyber Operations', 'level': 'H1'}, {'title': 'Methods of Proof and Cyber Operations', 'level': 'H1'}, {'title': 'Presumptions and Inferences in the Cyber Context', 'level': 'H1'}, {'title': 'Inadmissible Evidence', 'level': 'H1'}]}, {'theme': 'Cyber Conflict and State Responsibility', 'outline': [{'title': 'Cyber-Attacks and the Russian-Georgian Conflict', 'level': 'H1'}, {'title': 'Cyber-Attacks as Internationally Wrongful Acts', 'level': 'H1'}, {'title': 'Adverse Cyber Operations and Possible Responses', 'level': 'H1'}, {'title': 'Causality and Attribution', 'level': 'H1'}, {'title': 'The Present State of Cyber Attribution', 'level': 'H1'}, {'title': 'Proposals for International Attribution Mechanisms', 'level': 'H1'}, {'title': 'Developing Evidence for Attribution and Victim State Responses', 'level': 'H1'}, {'title': 'Assessment of Russian Cyberspace Activities', 'level': 'H1'}, {'title': 'Current International Law Has Limited Utility to Counter Russian Cyber Proxies', 'level': 'H1'}]}, {'theme': 'Policy and Strategic Implications of Attribution', 'outline': [{'title': 'Deciding How and When a “Victim” State May Respond', 'level': 'H1'}, {'title': 'Retorsion and Other Lawful Responses', 'level': 'H1'}, {'title': 'Countermeasures', 'level': 'H1'}, {'title': 'Actions Taken Out of Necessity', 'level': 'H1'}, {'title': 'Resort to Sanctions from a Legal Perspective', 'level': 'H1'}, {'title': 'The US, the EU and the UK Counter-Cyber Sanction Regimes and Their Implementation', 'level': 'H1'}, {'title': 'How to Measure the Effectiveness of Sanctions', 'level': 'H1'}, {'title': 'Consequential Coercive Diplomacy Through Economic Sanctions', 'level': 'H1'}, {'title': 'Implement a Rapid Attribution Strategy', 'level': 'H1'}]}, {'theme': 'Cyber Attribution: Challenges and Solutions', 'outline': [{'title': 'The Challenge of Attribution to Nation-State Actors', 'level': 'H1'}, {'title': 'Technical and Practical Challenges', 'level': 'H1'}, {'title': 'The Attribution Problem', 'level': 'H1'}, {'title': 'On the Problem of Cyber Attribution', 'level': 'H1'}, {'title': 'What is Attribution About?', 'level': 'H1'}, {'title': 'The Design of the Internet and the Difficulty of Attribution', 'level': 'H1'}, {'title': 'How Attribution Judgments Are Made', 'level': 'H1'}, {'title': 'Attribution from the Standpoint of the Adversary', 'level': 'H1'}, {'title': 'Identifying Cybercrime, Cyberterrorism, and Cyberwarfare: Taxonomy', 'level': 'H1'}]}, {'theme': 'Case Studies and Empirical Analysis', 'outline': [{'title': "NotPetya, Merck, Mondelez and Lloyd's of London - An Overview", 'level': 'H1'}, {'title': 'Case Studies', 'level': 'H1'}, {'title': 'Cyber Proxies: What We Know', 'level': 'H1'}, {'title': 'The Illogic of Plausible Deniability', 'level': 'H1'}, {'title': 'Empirical Strategy', 'level': 'H1'}, {'title': 'The Park Jin Hyok Case: Salient Features', 'level': 'H1'}]}, {'theme': 'Conceptual and Theoretical Frameworks', 'outline': [{'title': 'Conceptual Framework', 'level': 'H1'}, {'title': 'Criminal Charges as Policy: Considerations', 'level': 'H1'}, {'title': 'Theory of Criminal Justice', 'level': 'H1'}, {'title': 'The Nature of Cyber-Attack', 'level': 'H1'}, {'title': 'Existing Principles of Jus ad Bellum', 'level': 'H1'}]}]}
            # # print('grouping')
            # #
            # print(grouping_themes)
            # # Step 1: Create a mapping of numbers to themes
            # themes_list = {n + 1: theme['theme'] for n, theme in enumerate(grouping_themes['themes'])}
            # # Step 2: Display the available themes
            # for n,theme in enumerate(grouping_themes['themes']):
            #
            #     print(f"{n+1}. {theme['theme']}")
            # # Step 3: Loop to get valid user input for theme selection
            # # Step 3: Loop to get valid user input for theme selection
            # loop = True
            # while loop:
            #     # Get user input for theme selection (multiple choices allowed)
            #     choice = input("What theme(s) would you pick? (Enter numbers separated by spaces): ")
            #
            #     # Check if the input is empty
            #     if not choice.strip():
            #         print("Input cannot be empty. Please enter valid numbers.")
            #         continue
            #
            #     # Convert user input to a list of integers
            #     try:
            #         selected_numbers = [int(num) for num in choice.split()]
            #     except ValueError:
            #         print("Invalid input. Please enter numbers only.")
            #         continue
            #
            #     # Check if all selected numbers are valid (i.e., in the available themes list)
            #     if all(num in themes_list for num in selected_numbers):
            #         loop = False
            #         print("You've selected the following themes:")
            #         for num in selected_numbers:
            #             print(f"- {themes_list[num]}")
            #     else:
            #         print("Invalid selection. Please enter valid theme numbers.")
            #
            # # Step 4: Split the input into individual choices and filter the selected themes
            # chosen_themes = [theme for n, theme in enumerate(grouping_themes['themes']) if str(n+1) in choice.split()]
            # # Themes={'themes':[theme for theme in grouping_themes['themes'] if theme['theme'] in chosen_themes]}
            # # Step 5: Display the selected themes
            # if chosen_themes:
            #     print(f"You selected: chosen_theme")
            # else:
            #     print("No valid theme selected.")
            # print(chosen_themes)

            # themes = process_themes(themes=chosen_themes,more_subsection_get=self.search_paragraphs_by_query,type_collection=type_collection,collection_name=collection_name)
            # print('new themes')
            # print(themes)
            # input('is that right')
            # Themes=''
            # Iterate over the Themes recursively to add paragraphs

            # Recursively add paragraphs to each title and child title in the Themes

            #
            # with open('textfinal.txt', 'w', encoding='utf-8') as f:
            #     f.write(str(themes))
            with open('textfinal.txt', 'r', encoding='utf-8') as f:
                themes = ast.literal_eval(f.read())
            # print(themes['themes'][0]['theme'])
                        # response= call_openai_api(data=str(data_to)+'\nthe data is inside the h1:Responses and Consequences of Cyber Attribution', function='cleaning_headings',id='')





            export_data(themes=themes,
                        export_to=['md'],
                        filename=r'C:\Users\luano\Downloads\AcAssitant\Files\bib_files\cyber evidence')

    def search_paragraphs_by_query(self,
                                   collection_name,  # Now we should have a valid collection name
                                   query,  # The embedding for the query
                                   update=False,
                                   keyword=None,
                                   type_collection='paragraph_title',
                                   ai=False,
                                   # top_k=10,  # Retrieve top 10 similar paragraphs
                                   filter_conditions=None,  # No specific filter, searching across all data
                                   with_payload=True,  # Return payload (paragraph text)
                                   with_vectors=False,  # No need to return vectors
                                   score_threshold=0.75,  # Only return results with a score >= 0.75 (optional)
                                   # offset=0,  # Starting from the first result
                                   # limit=10  # Limit to 10 results
    ):

        search_results=None
        query_open_ai=''
        if ai:
            query_open_ai=query

            query=query['title']

        """
        Perform `advanced_search` across multiple collections and aggregate results into a dictionary.

        Args:
            collections (list): List of collections to search through.
            query_vector (list): The query vector to use in the search.

        Returns:
            dict: Aggregated results by keys ('section_title', 'paragraph_title', 'paragraph_text', 'blockquote_text').
        """

        # Initialize aggregated results with empty lists for each key
        aggregated_results = {
            'section_title': [],
            'paragraph_title': [],
            'paragraph_text': [],
            'paragraph_blockquote':[],
            'paragraph_id': [],
            'metadata': []
        }

        dquadrant_handler = QdrantHandler()
        collection_data = self.get_or_update_collection(collection_name=collection_name, update=update)
        data = [ i['item_id'] for t, i in collection_data[("items")]["papers"].items() ][:15]
        # Setting up the tqdm iterator
        for collection_name in data:


            collection_name = f'{collection_name}_{type_collection}'

            try:
                search_results = dquadrant_handler.advanced_search(collection_name=collection_name, keywords=keyword,query=query)

            except UnexpectedResponse as e:
                print(e)
                print('error with',collection_name)
            # Append values to corresponding keys in final_data
            aggregated_results['section_title'].extend(search_results['section_title'])
            aggregated_results['paragraph_title'].extend(search_results['paragraph_title'])
            aggregated_results['paragraph_text'].extend(search_results['paragraph_text'])
            aggregated_results['paragraph_blockquote'].extend(search_results['paragraph_blockquote'])
            aggregated_results['paragraph_id'].extend(search_results['paragraph_id'])
            aggregated_results['metadata'].extend(search_results['metadata'])



        data_to_send = [{'id': aggregated_results['paragraph_id'][data_index],
                         'topic sentence': aggregated_results['paragraph_title'][data_index]} for data_index in
                        range(len(aggregated_results['paragraph_text']))]
        with open('aggregate.txt', 'w') as f:
            f.write(json.dumps(aggregated_results))

        print('aggregated results size:',len(aggregated_results['paragraph_title']))
        size_results= len(aggregated_results['paragraph_title'])
        if ai:

            response = retry_api_call(
                data=str(data_to_send) + f'\n as context, the data is inside the {query_open_ai}',
                function='cleaning_headings',
                model='gpt-4o-2024-08-06'
            )

            data =update_response_with_paragraph_data(response=response,aggregated_paragraph_data=aggregated_results)

            return data
        else:

            return aggregated_results



