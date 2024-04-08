import os
import ast
import time
import pickle
from progress.bar import Bar
from Pychat_module.gpt_api import chat_response
from bs4 import BeautifulSoup,NavigableString
from Pychat_module.Pychat import ChatGPT
import pyzotero
from pyzotero import zotero
from Zotero_module.zotero_data import note_update, tags_prompt, book,initial_book, sections_prompt
from tqdm import tqdm
import requests
import re
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()  # loads the variables from .env
api_key = os.environ.get("wos_api_key")
ser_api_key = os.environ.get("ser_api_key")
class Zotero:
    def __init__(self,
                 library_id="<Library ID>",
                 library_type='user',
                 api_key="<API KEY>",
                 chat_args = { "chat_id": "pdf"},
                 os = "mac"
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
    def get_document_info1(self,query):
        """
           Retrieves document information from the Clarivate Web of Science Starter API based on a specified query.

           Parameters:
           - query (str): The search query to fetch document information for.

           Returns:
           - A dictionary containing details about the first document matching the query, including title, authors, source, publication year, volume, issue, pages range, DOI, keywords, record link, citing articles link, references link, related records link, and citations count.
           - Returns None if no records are found or if the request fails.

           Note:
           - This method prints the response data, citations count, and detailed result for debugging purposes.
           """
        # Set the URL for the API endpoint
        url = "https://api.clarivate.com/apis/wos-starter/v1/documents"
        # Set the query parameters
        params = {
            "q": query,
            # Limit to 1 result
        }
        # Set the headers including the API key
        headers = {
            "X-ApiKey": api_key
        }
        # Send the GET request
        response = requests.get(url, headers=headers, params=params)
    
        # Initialize the result dictionary
        result = {}
        # Check if the request was successful
        if response.status_code == 200:
            # Parse the response JSON
            data = response.json()
            print(data)
            if data["metadata"]["total"] > 0:
    
                if 'hits' in data and data['hits']:
                    hit = data['hits'][0]  # Assuming only one hit is returned
                    result['title'] = hit.get('title')
                    result['authors'] = [author['displayName'] for author in hit.get('names', {}).get('authors', [])]
                    result['source'] = hit.get('source').get('sourceTitle')
                    result['year'] = hit.get('source').get('publishYear')
                    result['volume'] = hit.get('source').get('volume')
                    result['issue'] = hit.get('source').get('issue')
                    result['pages'] = hit.get('source').get('pages').get('range')
                    result['doi'] = hit.get('identifiers').get('doi')
                    result['keywords'] = hit.get('keywords').get('authorKeywords',)
    
                    result['record_link'] = hit.get('links').get('record')
                    result['citing_articles_link']  = hit.get('links').get('citingArticles')
                    result['references_link'] = hit.get('links').get('reference')
                    result['related_records_link'] = hit.get('links').get('related')
                    result['citations'] =  hit.get('citations')[0].get("count")
                    print(result['citations'])
                    print(hit['citations'][0]['count'])
                    print(result)
                    return result
    
            else:
                print("No records found")
                return None
    
        else:
            # Print the status code and error message if the request failed
            print(f"Request failed with status code {response.status_code}: {response.text}")
            return None

    def get_document_info2(self,query,author):
        """
            Retrieves document information from the Google Scholar search engine via the SERP API based on a specified query and author name.

            Parameters:
            - query (str): The search query to fetch document information for.
            - author (str): The name of the author to specifically look for in the search results.

            Returns:
            - A dictionary containing details about the first document matching the query and author, including title, author name, snippet, link to the document, total citations count, link to the cited by page, and link to related pages.
            - Returns None if no records are found, the specified author does not match, or if the request fails.

            Note:
            - The method performs a single result search on Google Scholar, filtered by the provided author name, to find a relevant document.
            """
        # Set the URL for the API endpoint
        url = "https://serpapi.com/search"
        # Set the query parameters
        params = {
            "engine": "google_scholar",
            "q": query,
            "api_key": ser_api_key,
            "num": 10  # Limit to 1 result
        }
        # Send the GET request
        response = requests.get(url, params=params)
        # Initialize the result dictionary
        result = {}
        # Check if the request was successful
        if response.status_code == 200:
            # Parse the response JSON
            data = response.json()
            # Check for organic results
            if 'organic_results' in data and data['organic_results']:
                hit = data['organic_results'][0]  # Assuming only one hit is returned
                # Extracting the information
                result['title'] = hit.get('title')

                # Assuming there may be multiple authors, but we only extract the first one for simplicity
                authors = hit.get('publication_info', {}).get('authors', [])
                result['author'] = authors[0]['name'] if authors else 'Unknown'
                if not result['author'].find(author):
                    return None

                result['snippet'] = hit.get('snippet')
                result['link'] = hit.get('link')

                # Extracting citation information
                cited_by = hit.get('inline_links', {}).get('cited_by', {})
                result['total_cited'] = cited_by.get('total', 0)
                result['cited_link'] = cited_by.get('link')

                # Extracting related pages link
                result['related_pages_link'] = hit.get('inline_links', {}).get('related_pages_link')

                return result
            else:
                print("No records found")
                return None
        else:
            # Print the status code and error message if the request failed
            print(f"Request failed with status code {response.status_code}: {response.text}")
            return None
    def get_or_update_collection(self, collection_name=None, update=False,tag=None):
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
        if tag== "replace" or tag == "append":
            api = ChatGPT(**self.chat_args)
        else:
            api = ""
        # Loop until a valid collection name is provided
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
                        note_data = None
                        collection_items= [papers for papers in collection_items if papers['data']['itemType'] not in ['note', 'attachment', 'linkAttachment', 'fileAttachment',
                                                       'annotation']]

                        # Process each item in this batch
                        with (tqdm(total=len(collection_items), bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}]',
                                  colour='green') as pbar):

                            for item in collection_items:
                                item_data = item['data']
                                paper_title = item_data.get('title', 'No Title')
                                pbar.set_description(f"processing {paper_title}")
                                paper_key = item_data['key']
                                note_data = self.get_children_notes(paper_key)

                                # paper_data = {'id': paper_key, 'pdf': None, "note":note_data}
                                # Process attachments if present
                                if 'attachment' in item['links']:
                                    attachment_link = item['links']['attachment']['href'].split("/")[-1]
                                    directory = self.zotero_directory + attachment_link
                                    try:
                                        # Iterate through each author in the data.
                                        # Check if both 'firstName' and 'lastName' keys exist, and join them if they do.
                                        # If they don't exist, use the 'name' key directly.
                                        authors = ", ".join([
                                            f"{author['firstName']} {author['lastName']}" if 'firstName' in author and 'lastName' in author
                                            else author['name']
                                            for author in item['data'].get('creators', [])
                                        ])
                                    except Exception as e:
                                        authors= "author"
                                        # If there is an error, print out the error and the format that caused it.
                                        # Ensure authors is set to None or an empty list if there is an error
                                        print(f"Error when parsing authors: {e}")

                                    date = item['data'].get('date')
                                    date =  "date" if date is None else date
                                    year_match = re.search(r'\b\d{4}\b', date)
                                    if year_match:
                                        date = year_match.group(0)
                                    new_path = f"({authors}, {date}).pdf"
                                    pdf_path=self.get_pdf_path(directory,new_path)
                                    paper_data = {'id': paper_key,"reference":new_path.replace(".pdf",""), 'pdf': pdf_path, "note": note_data,}

                                    if pdf_path is not None and tag:
                                        if tag == "replace" or tag == "append":
                                            if api:  # Check if API is set for non-delete aims
                                                new_tags = ast.literal_eval(
                                                    api.interact_with_page(prompt=tags_prompt,
                                                                           path=pdf_path, copy=True))
                                                new_tags = [{"tag": tag.strip().lower()} for tag in new_tags]

                                                if tag == "append":
                                                    item['data']['tags'].extend(
                                                        new_tags)  # Extend existing tags with new ones
                                                elif tag == "replace":
                                                    item['data'][
                                                        'tags'] = new_tags  # Replace existing tags with new ones

                                        if tag == "delete":
                                            item['data']['tags'] = []  # Remove all tags

                                        # Update the item on the server
                                        try:
                                            updated_item = self.zot.update_item(item)

                                            print(f"Item updated: {item['data']['title']}")
                                        except pyzotero.zotero_errors.PreConditionFailed as e:
                                            print(
                                                f"Item version conflict detected for '{item['data']['title']}'. Retrieving the latest version and retrying.",
                                                e)
                                            latest_item = self.zot.item(item['key'])
                                            updated_item = self.zot.update_item(latest_item)
                                             # Add the updated item to the list
                                target_collection['items']['papers'][paper_title] = paper_data
                                pbar.update()



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


    def get_pdf_path(self, dir_path, new_filename):
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
        if not new_filename.endswith(".pdf"):
            raise ValueError("The new filename must end with '.pdf'.")

        for root, dirs, files in os.walk(dir_path):
            for file in files:
                if file.endswith(".pdf"):
                    current_pdf_path = os.path.join(root, file)
                    new_pdf_path = os.path.join(root, new_filename)
                    if current_pdf_path != new_pdf_path:
                        os.rename(current_pdf_path, new_pdf_path)
                        print(f"Renaming file: current_pdf_path:{current_pdf_path} to new_pdf_path: {new_pdf_path}")
                        return new_pdf_path
                    return current_pdf_path


    def create_note(self,item_id,path):
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
        item = self.zot.item(item_id)
        # tags = ["tag1", "tag2", "tag3", "tag4"]
    
        # Fetch the item by ID
        item = self.zot.item(item_id)
        data = item
        link1 = ""
        link2 = ""
        date = data['data'].get('date')
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
        doi = "3457788"  # data['data'].get('DOI',"165432")
        publication_title = data['data'].get('publicationTitle', "journal")
    
        query1 = (f'('
                 f'TI=("{title}")'
                 f') AND'
                 f' ('
                 f'PY=("{date}") OR '
                 f'AU=("{authors}") OR '
                 f'DO=("{doi}")'
                 f')')
    
        key = data.get('key')
        item_type = data['data'].get('itemType')
        title = data['data'].get('title')
        abstract = data['data'].get('abstractNote')
        publication_title = data['data'].get('publicationTitle')
        doi = data['data'].get('DOI')
        if item['data']['itemType'] in ['note', 'attachment', 'linkAttachment', 'fileAttachment']:
            return  # Exit the function as we cannot proceed
        # Format the current date and time
        now = datetime.now().strftime("%d-%m-%Y at %H:%M")
        data_wos = self.get_document_info1(query1)
        if data_wos:
            title = data_wos.get('title')
            publication_title = data_wos.get("source")
            doi = data_wos.get('doi') if not doi else doi
            if publication_title:
                data_wos.get('source').capitalize()



            link1 = f"""
    
                    <li><strong>WoS Citing Articles</strong>: <a href="{data_wos.get("citing_articles_link")}">Citation[{data_wos.get('citations')}]</a></li>
                    <li><strong>WoS References</strong>: <a href="{data_wos.get("references_link")}">References</a></li>
                    <li><strong>WoS Related</strong>: <a href="{data_wos.get("related_records_link")}">Related</a></li>
                """

        serp =self.get_document_info2(query=title,author=authors)
        if serp:
                link2 = f"""
    
                                  <li><strong>Citing Articles</strong>: <a href="{serp['cited_link']}">Citation[{serp['total_cited']}]</a></li>
                                  <li><strong>Related</strong>: <a href="{serp["related_pages_link"]}">Related</a></li>
                              """

        # Construct the note content using the item details
        note_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>@{key}</title>
    </head>
    <body>
            <div>
            <em>@{key}</em><br>
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
            <li><strong>PDF</strong>: <a href="{path}">Zotero</a></li>
            {link1}
            {link2}

    
        </ul>
        <hr>
        <hr>
        <h1>Abstract:</h1>
        <p>"{item['data'].get('abstractNote')}"</p>
        <hr>
        <hr>
        <h1>1. Introduction:</h1>
            <h2>1.1 Research Framework</h2>
            <hr>
            <h2>1.2 Key Terms Definitions</h2>
            <hr>
            <h2>1.3 Key Findings</h2>
            <hr>
            <h2>1.4 Shortcomings Limitations</h2>
            <hr>
            <h2>1.5 Research Gap and Future Research Directions</h2>
            <hr>
            <hr>
        <h1>2. Methodology and Methods:</h1>
            <h2>2.1 Data, Analysis and Epistemologies</h2>
            <hr>
            <h2>2.2 Theoretical Framework or Models</h2>
            <hr>
            <h2>2.3 Implications and Policy</h2>
            <hr>
            <h2>2.4 Author References</h2>
            <hr>
            <h2>2.5 Entity Reference</h2>
            <hr>
            <hr>
        <h1>3. Thematic Review</h1>
            <h2>3.1 Structure and Keywords</h2>
            <hr>
            <h2>3.2 Main Topics</h2>
            <hr>
            <h2>3.3 Thematic Analysis 1</h2>
            <hr>
            <h2>3.4 Thematic Analysis 2</h2>
            <hr>
            <h2>3.5 Thematic Analysis 3</h2>
            <hr>
            <hr>
            <h1>Summary</h1>

            <h2>Loose notes</h2>
            <hr>
                </div>
                </body>
                </html>
        """
    
        # Create the new note
        new_note = self.zot.create_items([{
            "itemType": "note",
            'parentItem': item_id,
            "note": note_content,

    
    
        }])
    
        print("New note created:", new_note)
        time.sleep(15)
        new_note_id =new_note['successful']['0']['data']['key']
        if new_note_id:
            note = self.zot.item(new_note_id)
            note_content = note['data']['note']
    
            # Update the note content with the new note ID
            updated_content = note_content.replace(f'<em>Note date: {now}</em><br>',
                                                   f'<em>Note ID: {new_note_id}</em><br><em>Note date: {now}</em><br>')

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



    def update_zotero_note_section(self, note_id, updates, api):

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
        if 'data' in note and 'note' in note['data']:
            note_content = note['data']['note']
        else:
            print(f"No note content found for item ID {note_id}")
            return

        updated_content = note_content  # Initialize with the current note content

        # Process updates for each section
        for section, new_prompt in updates.items():
            # This pattern looks for the section, captures content until it finds the next <h2>, <h1>, or <hr>
            pattern = re.compile(f'({re.escape(section)})(.*?)(?=<h2>|<h1>|<hr>|$)', re.DOTALL | re.IGNORECASE)
            matches = pattern.search(updated_content)

            if matches:
                # Generate new content using the API based on the provided prompt
                new_content = api.send_message(new_prompt).strip()

                # Replace the old section content with the new one
                updated_section = f"{matches.group(1)}{new_content}"
                updated_content = updated_content[:matches.start()] + updated_section + updated_content[matches.end():]
            else:
                print(f"Section title '{section}' not found in the note content.")
        if section =="<h2>3.1 Structure and Keywords</h2>":
            tags.extend(self.extract_unique_keywords_from_html(new_content))
            self.schema = [i for i in self.extract_insert_article_schema(updated_content) if i not in ["Abstract","abstract"]]
            pattern = re.compile(f'({re.escape("<h1>Summary</h1>")})(.*?)(?=<h2>|<h1>|<hr>|$)', re.DOTALL | re.IGNORECASE)
            matches = pattern.search(updated_content)
            content= '<hr>\n'.join(self.schema) +"<hr>\n"
            if matches:
                updated_section = f"{matches.group(1)}{content}"
                updated_content = updated_content[:matches.start()] + updated_section + updated_content[matches.end():]
            else:
                print(f"Section title '<h1>Summary</h1>' not found in the note content.")

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
    def update_zotero_note_section2(self, note_id, sections,pdf,reference):

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
        if 'data' in note and 'note' in note['data']:
            note_content = note['data']['note']
        else:
            print(f"No note content found for item ID {note_id}")
            return

        updated_content = note_content  # Initialize with the current note content

        # Process updates for each section
        for section, new_prompt in sections.items():
            input(" enter")
            # This pattern looks for the section, captures content until it finds the next <h2>, <h1>, or <hr>
            pattern = re.compile(f'({re.escape(section)})(.*?)(?=<h2>|<h1>|<hr>|$)', re.DOTALL | re.IGNORECASE)
            matches = pattern.search(updated_content)

            if matches:
                # Generate new content using the API based on the provided prompt
                new_content =  chat_response(pdf,new_prompt+f"note:\nauthor reference={reference}")


                # Replace the old section content with the new one
                updated_section = f"{matches.group(1)}{new_content}"
                updated_content = updated_content[:matches.start()] + updated_section + updated_content[matches.end():]
            else:
                print(f"Section title '{section}' not found in the note content.")
        if section =="<h2>3.1 Structure and Keywords</h2>":
            tags.extend(self.extract_unique_keywords_from_html(new_content))
            self.schema = [i for i in self.extract_insert_article_schema(updated_content) if i not in ["Abstract","abstract"]]
            pattern = re.compile(f'({re.escape("<h1>Summary</h1>")})(.*?)(?=<h2>|<h1>|<hr>|$)', re.DOTALL | re.IGNORECASE)
            matches = pattern.search(updated_content)
            content= '<hr>\n'.join(self.schema) +"<hr>\n"
            if matches:
                updated_section = f"{matches.group(1)}{content}"
                updated_content = updated_content[:matches.start()] + updated_section + updated_content[matches.end():]
            else:
                print(f"Section title '<h1>Summary</h1>' not found in the note content.")

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

    
    def update_all(self,collection_name,index=0,tag=None,update=True,chat="chat"):
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
        collection_data = self.get_or_update_collection(collection_name=collection_name,update=update,tag=tag)
        data =[ (t,i) for t,i in collection_data["items"]["papers"].items() ][::-1]
        note_complete = len(collection_data["items"]["papers"].items())
        print("Note complete is",note_complete)
        if chat=="chat":
            api = ChatGPT(**self.chat_args
                          )

        # Setting up the tqdm iterator
        pbar = tqdm(data,
                    bar_format="{l_bar}{bar:30}{r_bar}{bar:-30b}",
                    colour='green')

        for keys, values in pbar:
            # Dynamically update the description with the current key being processed
            index1 = [i for i in collection_data["items"]["papers"]].index(keys)
            pbar.set_description(f"Processing index:{index1},paper:{keys} missing:{note_complete} ")
            note = values['note']
            id = values['id']
            pdf = values['pdf']



            if note is None and pdf is not None:
                print("note is None and pdf is None")


                note_id= self.create_note(id, pdf)

                if note_id:
                    try:
                        self.update_multiple_notes(sections_prompts=note_update,note_id=note_id,pdf=pdf,api=api
                                                   )
                    except Exception as e:
                        print("multiple notes function failed:",e)

                else:
                        print("Failed to update item.")
            if note and note["headings"]:
                note_content = note["content"]
                self.schema = self.extract_insert_article_schema(note_content)

                if self.schema:
                    section_dict = {
                        k: f"Perform an in-depth analysis of the '{self.clean_h2_title(k)}' in the attached PDF document, carefully counting each paragraph starting from the beginning of this section. For each key idea or theme identified, reference the specific paragraph numbers (e.g., 'Paragraph 1,' 'Paragraphs 2-3') and provide a focused summary of the principal ideas discussed in these paragraphs. Accompany each summary with direct quotes from the respective paragraphs to illustrate or support the key points identified. ### Guideline for Analysis Presentation: ```html <div> <h3>Paragraph 1 - [Key Idea or Theme]</h3> <p>[Provide a summary of the principal idea discussed in the first paragraph of the section.]</p> <blockquote>'[Direct quote from the first paragraph.]'</blockquote> <h3>Paragraphs 2-3 - [Next Key Idea or Theme]</h3> <p>[Summarize the principal ideas discussed across paragraphs 2 and 3, grouping them by the overarching theme or concept.]</p> <blockquote>'[Direct quote from paragraph 2.]'</blockquote> <blockquote>'[Direct quote from paragraph 3.]'</blockquote> <!-- Continue this structure for additional paragraphs or groups of paragraphs, correlating each with its key ideas or themes --> </div> ``` This methodical approach ensures a structured and precise examination of the '{k}', organized by the specific paragraphs and their associated key ideas or themes, all supported by direct quotations from the document for a comprehensive and insightful analysis."

                        for k in self.schema if k not in ["Abstract", "table pf"]}
                    note_update.update(section_dict)
                note_id=note["note_id"]
                print("note heading")
                print(note["headings"])



                note_update1 = {k: v for k, v in note_update.items() if k in note["headings"]}
                try:
                    self.update_multiple_notes(sections_prompts=note_update1,pdf=pdf, note_id=note_id)
                except Exception as e:
                    print("multiple notes function err if remaining",e)


            if note and note["headings"] == []:
                print("note heading==[]")
                note_complete -=1


        if note_complete>0:
            return True
        if note_complete ==0:
            return False
    def update_all2(self,collection_name,index=0,tag=None,update=True):
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
        collection_data = self.get_or_update_collection(collection_name=collection_name,update=update,tag=tag)
        data =[ (t,i) for t,i in collection_data["items"]["papers"].items() ][::-1]
        note_complete = len(collection_data["items"]["papers"].items())
        print("Note complete is",note_complete)
        # Setting up the tqdm iterator
        pbar = tqdm(data,
                    bar_format="{l_bar}{bar:30}{r_bar}{bar:-30b}",
                    colour='green')
        for keys, values in pbar:
            # Dynamically update the description with the current key being processed
            index1 = [i for i in collection_data["items"]["papers"]].index(keys)
            pbar.set_description(f"Processing index:{index1},paper:{keys} missing:{note_complete} ")
            note = values['note']
            id = values['id']
            pdf = values['pdf']
            print("values ",values)
            reference = values['reference']




            if note is None and pdf is not None:
                print("note is None and pdf is None")


                note_id= self.create_note(id, pdf)

                if note_id:
                    self.update_multiple_notes2(sections_prompts=sections_prompt,note_id=note_id,pdf=pdf,reference=reference
                                                   )

            if note and note["headings"]:
                note_content = note["content"]
                self.schema = self.extract_insert_article_schema(note_content)

                if self.schema:
                    section_dict = {
                        k: f"Perform an in-depth analysis of the '{self.clean_h2_title(k)}' in the attached PDF document, carefully counting each paragraph starting from the beginning of this section. For each key idea or theme identified, reference the specific paragraph numbers (e.g., 'Paragraph 1,' 'Paragraphs 2-3') and provide a focused summary of the principal ideas discussed in these paragraphs. Accompany each summary with direct quotes from the respective paragraphs to illustrate or support the key points identified. ### Guideline for Analysis Presentation: ```html <div> <h3>Paragraph 1 - [Key Idea or Theme]</h3> <p>[Provide a summary of the principal idea discussed in the first paragraph of the section.]</p> <blockquote>'[Direct quote from the first paragraph.]'</blockquote> <h3>Paragraphs 2-3 - [Next Key Idea or Theme]</h3> <p>[Summarize the principal ideas discussed across paragraphs 2 and 3, grouping them by the overarching theme or concept.]</p> <blockquote>'[Direct quote from paragraph 2.]'</blockquote> <blockquote>'[Direct quote from paragraph 3.]'</blockquote> <!-- Continue this structure for additional paragraphs or groups of paragraphs, correlating each with its key ideas or themes --> </div> ``` This methodical approach ensures a structured and precise examination of the '{k}', organized by the specific paragraphs and their associated key ideas or themes, all supported by direct quotations from the document for a comprehensive and insightful analysis."

                        for k in self.schema if k not in ["Abstract", "table pf"]}
                    sections_prompt.update(section_dict)
                note_id=note["note_id"]
                print("note heading")
                print(note["headings"])



                note_update1 = {k: v for k, v in sections_prompt.items() if k in note["headings"]}
                try:
                    self.update_multiple_notes2(sections_prompts=note_update1,pdf=pdf, note_id=note_id,reference=reference)
                except Exception as e:
                    print("multiple notes function err if remaining",e)


            if note and note["headings"] == []:
                print("note heading==[]")
                note_complete -=1


        if note_complete>0:
            return True
        if note_complete ==0:
            return False

    def clean_h2_title(self,html_string):
        """
           Extracts and cleans the text of the first <h2> tag found in the given HTML string.

           Parameters:
           - html_string (str): The HTML string to parse for an <h2> tag.

           Returns:
           - The cleaned text content of the first <h2> tag, with all HTML tags removed. Returns None if no <h2> tag is found.
           """
        # Use regular expression to extract text within <h2> tags
        h2_text = re.search(r'<h2>(.*?)</h2>', html_string)
        if h2_text:
            # If found, return the cleaned text without HTML tags
            return re.sub('<[^<]+?>', '', h2_text.group(1))
        else:
            # If not found, return None or handle the case appropriately
            return None
    
    def update_multiple_notes(self,sections_prompts,note_id,pdf='',start_section=False,):

        api = ChatGPT(**self.chat_args)
        # if self.chat_args.get("chat_id"):
        api.interact_with_page(path=pdf, copy=False)


        process=False
    
        # Assuming thematic_section is a dictionary
        total_iterations = len(sections_prompts)
        with tqdm(sections_prompts.items(), bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}]',
                  colour='blue') as pbar:

            for key, value in pbar:
                if start_section:
                    if key == start_section:
                        process = True
                if not start_section:
                    process=True

                if self.schema:
                    if key==self.schema[0] or key=="<h2>2.2 Theoretical Framework or Models</h2>":
                        api.open_new_tab()

                        api.interact_with_page(path=pdf, copy=False)

                if process:


                    pbar.set_description(f"Processing section {key}",
                                         )


                    self.update_zotero_note_section(note_id=note_id, updates={key:value},api=api)
                    pbar.update()

    def update_multiple_notes2(self, sections_prompts, note_id, pdf,reference):
        with tqdm(sections_prompts.items(), bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}]',
                  colour='blue') as pbar:

            for key, value in pbar:
                print("keys:",key)

                pbar.set_description(f"Processing section {key}",
                                     )

                self.update_zotero_note_section2(note_id=note_id, sections={key: value},pdf=pdf,reference=reference)
                pbar.update()

    def extract_relevant_h2_blocks(self,html_content):
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
        self.schema = self.extract_insert_article_schema(html_content)
        if self.schema:
            section_dict = {
                k: f"Perform an in-depth analysis of the '{self.clean_h2_title(k)}' in the attached PDF document, carefully counting each paragraph starting from the beginning of this section. For each key idea or theme identified, reference the specific paragraph numbers (e.g., 'Paragraph 1,' 'Paragraphs 2-3') and provide a focused summary of the principal ideas discussed in these paragraphs. Accompany each summary with direct quotes from the respective paragraphs to illustrate or support the key points identified. ### Guideline for Analysis Presentation: ```html <div> <h3>Paragraph 1 - [Key Idea or Theme]</h3> <p>[Provide a summary of the principal idea discussed in the first paragraph of the section.]</p> <blockquote>'[Direct quote from the first paragraph.]'</blockquote> <h3>Paragraphs 2-3 - [Next Key Idea or Theme]</h3> <p>[Summarize the principal ideas discussed across paragraphs 2 and 3, grouping them by the overarching theme or concept.]</p> <blockquote>'[Direct quote from paragraph 2.]'</blockquote> <blockquote>'[Direct quote from paragraph 3.]'</blockquote> <!-- Continue this structure for additional paragraphs or groups of paragraphs, correlating each with its key ideas or themes --> </div> ``` This methodical approach ensures a structured and precise examination of the '{self.clean_h2_title(k)}', organized by the specific paragraphs and their associated key ideas or themes, all supported by direct quotations from the document for a comprehensive and insightful analysis."

                for k in self.schema if k not in ["Abstract", "table of content"]}
            note_update.update(section_dict)
        soup = BeautifulSoup(html_content, 'html.parser')
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
        relevant_h2_blocks = [h2 for h2 in relevant_h2_blocks if h2 in note_update.keys()]
        return relevant_h2_blocks

    def html_update(self,note_id):
    # Your HTML content
        with open(r"../Word_modules/Html_templates/holder.html", "r", encoding="utf-8") as html_file:
    
    
            start_section =False
            # Parse the HTML
            soup = BeautifulSoup(html_file, 'html.parser')
    
            # Find all elements with the language-python class
            python_elements = soup.find_all('code', {'class': 'language-html'})
    
            # Open the file for writing
            with open("copytexts.txt", "w", encoding="utf-8") as file:
    
                # Extract and write the text from each element to the file
    
    
    
                for i, section_tuple in enumerate(note_update, 0):
                    if start_section:
                        if section_tuple[0] == start_section:
                            process = True
                    if not start_section:
                        process = True
    
                    if process:
                        text = python_elements[i].get_text()
                        update_dict = {section_tuple[0]: text}  # Convert tuple to dictionary
    
    
                        self.update_note_section_fromHtml(note_id=note_id, updates=update_dict)
    
                        if i > len(python_elements)-1:
                            break
                print(text)
                print("_"*50)

    def get_children_notes(self, item_id):
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
        # Fetch all children of the specified item
        children = self.zot.children(item_id)

        # Filter out only notes that contain headings
        notes = [child for child in children if
                 child['data']['itemType'] == 'note' and re.search(r'<h\d>(.*?)<\/h\d>', child['data']["note"],
                                                                   re.IGNORECASE)]
        # Check the number of notes and print them if more than one
        if len(notes) > 1:
            print("Note 1:", notes[0]['data']["note"])
            print("Note 2:", notes[1]['data']["note"])

        # Process each note
        for note in notes:
            note_id = note['data']["key"]
            note_content = note['data']["note"]
            tags = [tag["tag"] for tag in note['data']['tags']]

            # Extract headings still needing updates
            remaining_h2 = self.extract_relevant_h2_blocks(note_content)

            # Check if the note is marked as complete
            if "note_complete" in tags:
                print("Note complete\n")
                return {"note_id": note_id, "headings": [],"content": note_content}

            # Check if there are no remaining sections and the note is not marked complete
            if not remaining_h2 and "note_complete" not in tags:
                note['data']['tags'].append({"tag": "note_complete"})
                self.zot.update_item(note)
                return {"note_id": note_id, "headings": [],"content": note_content}

            # If there are remaining sections, return them with the note ID
            if remaining_h2:

                keys =list(note_update.keys())


                remaining_h2 = [h2 for h2 in remaining_h2 if h2 in keys]
                return {"note_id": note_id, "headings": remaining_h2,"content": note_content}

        # If no notes meet the criteria, return None
        return None

    def extract_unique_keywords_from_html(self, html_text):
        """
        Extracts unique keywords enclosed in <li> tags from the provided HTML text and returns them as a list.
        For the "Affiliations, Countries, and Regions" section, only the countries are extracted, without the context.

        Args:
        - html_text (str): A string containing HTML content.

        Returns:
        - list: A list of unique keywords extracted from the HTML text.
        """

        # Use regular expression to find all keywords within <li> tags
        keywords = re.findall(r"<li>(.*?)</li>", html_text)

        # Process keywords to extract only the country for the "Affiliations, Countries, and Regions" section
        processed_keywords = []
        for keyword in keywords:
            # Check if the keyword contains 'context:' indicating it is from the "Affiliations, Countries, and Regions" section
            if 'context:' in keyword:
                # Extract the country part before '(context:'
                country = keyword.split('(context:')[0].strip()
                processed_keywords.append(country)
            else:
                processed_keywords.append(keyword.strip())

        # Remove duplicates by converting the list to a set, then back to a list
        unique_keywords = list(set(processed_keywords))

        # Generate a list of dictionaries with tags
        tags = [{"tag": tag.lower()} for tag in unique_keywords]

        return tags

    def extract_insert_article_schema(self,html_content):
        """
            Extracts article schema information from the given HTML content and formats it into a list of <h2> tags.

            Parameters:
            - html_content (str): HTML content from which to extract the article schema.

            Returns:
            - A list of strings, each representing an article schema item formatted as an <h2> tag. If the 'Article Schema:' section is not found, returns an empty list.
            """
        soup = BeautifulSoup(html_content, 'html.parser')
        schema_list = []

        article_schema = soup.find('h3', string='Article Schema:')
        if article_schema:
            # Find the next sibling that is a <ul> tag
            schema_ul = article_schema.find_next_sibling(lambda tag: tag.name == 'ul' and tag.find('li'))

            # Check if a <ul> tag was found
            if schema_ul:
                schema_items = schema_ul.find_all('li')
                for item in schema_items:
                    schema_list.append(f'<h2>{item.text.strip()}</h2>')

        return schema_list

    def process_headings(self,title,key="", update=False):

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

        headings = self.extract_headings(update=update, title=title,key=key)
        dici = create_prompts_dict(headings=headings, prompts_list=book)
        print("dici:",dici)
        self.generate_book_content(dici=dici,title=title)

        return dici

    def extract_headings(self,title,update=False,key=""):
        headings_file = f"Zotero_module/Data/book_data/{title.title}_list.pickle"
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
                html_content += api.send_message(message=message, sleep=60*4) + "\n"
            soup = BeautifulSoup(html_content, 'html.parser')
            headings = [heading.text.strip() for heading in soup.find_all(['h2', 'h3', 'h4', 'h5'])]
            api.delete_quit()
            with open(headings_file, 'wb') as f:
                pickle.dump(headings, f)
            return headings
        else:

            with open(headings_file, 'rb') as f:
                headings = pickle.load(f)
                if key == "":
                    index = 0
                else:

                    index = [i for i in headings].index(key)

                return headings[index:]

    def generate_book_content(self,dici,title):
        book_file =f"Zotero_module/Data/book_data/book_{title}.html"
        api = ChatGPT(**self.chat_args)
        with (tqdm(total=len(dici.keys()), bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}]',
                   colour='green') as pbar):
            for key, value in dici.items():
                pbar.set_description("processing " + key)
                prompt = key.replace(":", " =") + "\n" + value
                # Assuming api is a pre-initialized ChatGPT API client instance within the class
                html_content= api.send_message(message=prompt,sleep=60*4)  # Simulated API call


                # Append the resulting HTML content to the file
                with open(book_file, "a+", encoding="utf-8") as fp:
                    fp.write(html_content + "\n\n")  # Adding a newline for separation between entries
