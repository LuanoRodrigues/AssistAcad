import os
import ast
import time
import pickle
from bs4 import BeautifulSoup
import pprint
from Pychat_module.Pychat import ChatGPT
import pyzotero
from pyzotero import zotero
from Zotero_module.zotero_data import note_update,initial_prompt,tags_prompt
from tqdm import tqdm
import requests
import re
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()  # loads the variables from .env
api_key = os.environ.get("wos_api_key")

class Zotero:
    def __init__(self,
                 library_id="<Library ID>",
                 library_type='user',
                 api_key="<API KEY>",
                 chat_args = { "chat_id": "pdf"},
                 os = "mac"
                 ):
        self.library_id = library_id
        self.library_type = library_type
        self.api_key = api_key
        self.zot = self.connect()

        self.chat_args = chat_args
        self.zotero_directory = "/Users/pantera/Zotero/storage/" if os=="mac" else "C:\\Users\\luano\\Zotero\\storage\\"

    def connect(self):
        # Assuming you have zotero package installed

        return zotero.Zotero(self.library_id, self.library_type, self.api_key)
    def get_document_info(self,query):
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

    import ast
    import os
    import requests
    from tqdm import tqdm

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

            file_name = f'Zotero_module/collections_data/{collection_name.replace(" ", "_").lower()}_collection.pkl'
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
                        with tqdm(total=len(collection_items), bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}]',
                                  colour='green') as pbar:

                            for item in collection_items:
                                item_data = item['data']
                                paper_title = item_data.get('title', 'No Title')
                                pbar.set_description(f"processing {paper_title}")
                                paper_key = item_data['key']
                                note_data = self.get_children_notes(paper_key)

                                paper_data = {'id': paper_key, 'pdf': None, "note":note_data}
                                # Process attachments if present
                                if 'attachment' in item['links']:
                                    attachment_link = item['links']['attachment']['href'].split("/")[-1]
                                    directory = self.zotero_directory + attachment_link
                                    print(directory)
                                    for root, dirs, files in os.walk(directory):
                                        for file in files:
                                            if file.endswith(".pdf"):
                                                pdf_path = os.path.join(root, file)
                                                paper_data['pdf'] = pdf_path
                                                if tag !=None:

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

    def create_note(self,item_id,path):
    
    
        # Fetch the item by ID
        item = self.zot.item(item_id)
        # tags = ["tag1", "tag2", "tag3", "tag4"]
    
        # Fetch the item by ID
        item = self.zot.item(item_id)
        data = item
        links = ""
        date = data['data'].get('date')
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
            authors = None  # Ensure authors is set to None or an empty list if there is an error
            print(f"Error when parsing authors: {e}")
        title = data['data'].get('title')
        date = data['data'].get('date')
        year_match = re.search(r'\b\d{4}\b', date)
        if year_match:
            date = year_match.group(0)
        doi = "3457788"  # data['data'].get('DOI',"165432")
        publication_title = data['data'].get('publicationTitle', "journal")
    
        query = (f'('
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
        data_wos = self.get_document_info(query)
        if data_wos:
            title = data_wos.get('title')
            publication_title = data_wos.get("source")
            doi = data_wos.get('doi') if not doi else doi
            publication_title = data_wos.get('source') if not publication_title else publication_title
            links = f"""
    
                    <li><strong>Citing Articles</strong>: <a href="{data_wos.get("citing_articles_link")}">Citation[{data_wos.get('citations')}]</a></li>
                    <li><strong>References</strong>: <a href="{data_wos.get("references_link")}">References</a></li>
                    <li><strong>Related</strong>: <a href="{data_wos.get("related_records_link")}">Related</a></li>
                """
    
        # Construct the note content using the item details
        note_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{key}</title>
    </head>
    <body>
            <div>
            <em>Note date: {now}</em><br>
            <em>Parent id : {key}</em><br>
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
            {links}
    
        </ul>
        <hr>
        <hr>
        <h1>Abstract:</h1>
        <p>"{item['data'].get('abstractNote')}"</p>
        <hr>
        <hr>
        <h1>1. Introduction:</h1>
        <h2>1.1 Research Question</h2>
        <hr>
        <h2>1.2 Literature Review</h2>
        <hr>
        <h2>1.3 Key Arguments</h2>
        <hr>
        <h2>1.4 Key Findings</h2>
        <hr>
        <h2>1.5 Scientific Significance</h2>
        <hr>
        <h2>1.6 Shortcomings</h2>
        <hr>
        <h2>1.7 Future Research Directions</h2>
        <hr>
        <hr>
        <h1>2. Methodology and Methods:</h1>
        <h2>2.1 Data and Analysis</h2>
        <hr>
        <h2>2.2 Theoretical Framework or Models</h2>
        <hr>
        <h2>2.3 Research Methods and Epistemologies</h2>
        <hr>
        <h2>2.4 Critical Evidence</h2>
        <hr>
        <h2>2.5 Implications and Policy</h2>
        <hr>
        <h2>2.6 Authors Cited</h2>
        <hr>
        <hr>
        <h1>3. Thematic Review</h1>
        <h2>3.1 Terms and Definitions</h2>
        <hr>
        <h2>3.2 International Law</h2>
        <hr>
        <h2>3.3 Attribution Proposals</h2>
        <hr>
        <h2>3.4 Evidence and Proof Standards</h2>
        <hr>
        <h2>3.5 Sociotechnical Aspects</h2>
        <hr>
        <h2>3.6 Intelligence Methodology</h2>
        <hr>
        <h2>3.7 Technical Challenges</h2>
        <hr>
        <h2>3.8 Geopolitical Implications</h2>
        <hr>
        <h2>3.9 Responses to Cyber Attacks</h2>
        <hr>
        <hr>
        <h1>4. NPL analysis</h1>
        <hr>
        <h2>4.1 Article Structure</h2>
        <hr>
        <h2>4.2 Citation Analysis</h2>
        <hr>
        <h2>4.3 Topic Modeling Analysis</h2>
        <hr>
        <h2>4.4 Interdisciplinary Connections</h2>
        <hr>
        <hr>
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
            updated_content = note_content.replace(f'<em>Parent id : {key}</em><br>',
                                                   f'<em>Note ID: {new_note_id}</em><br><em>Parent id: {key}</em><br>')
    
            updated_note = {
                'key': note['data']['key'],
                'version': note['data']['version'],
                'itemType': note['data']['itemType'],
                'note': updated_content,
                'tags': note['data'].get('tags', [])
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
    
    

    def update_zotero_note_section(self,note_id, updates,api):
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
                original_content = matches[0][1].strip()  # The current (old) content of the section
                # if section == "<h2>Thematic Review</h2>":
                #     processed_content = api.send_message(new_content)
                #     # try:
                #     #     processed_content = processed_content.split("/")[1]
                #     # except:
                #     #     print("err")
                #
                #
                #
                #     # For 'Thematic Review', append new content to the end
                #     updated_section = f"{matches[0][0]}{original_content}{processed_content.lstrip()}<hr>"
                # if not original_content:
                processed_content = api.send_message(new_content)
                    # try:
                    #     processed_content = processed_content.split("/")[1]
                    # except:
                    #     print("err")
                    # For other sections, update only if there's no existing content
                updated_section = f"{matches[0][0]}{processed_content.lstrip()}<hr>"
                # else:
                #     # If there is existing content and it's not 'Thematic Review', do not update
                #     print(f"Existing content found in section {section}, no update made.")
                #     continue  # Skip to the next section
    
                # Update the note content with the new section content
                updated_content = updated_content.replace(matches[0][0] + matches[0][1] + "<hr>", updated_section)
            else:
                print(f"Section title '{section}' not found in the note content.")
    
        # Check if the content has been updated
        if updated_content != note_content:
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
                    print("Note updated successfully in section function.")
                else:
                    print("Failed to update the note in section function.")
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

    
    def update_all(self,collection_name,index=0,tag=None,update=True):
        collection_data = self.get_or_update_collection(collection_name=collection_name,update=update,tag=tag)
        data =[ (t,i) for t,i in collection_data["items"]["papers"].items() ][index:]
        # Setting up the tqdm iterator
        pbar = tqdm(data,
                    bar_format="{l_bar}{bar:30}{r_bar}{bar:-30b}",
                    colour='green')
    
        for keys, values in pbar:
            # Dynamically update the description with the current key being processed
            index1 = [i for i in collection_data["items"]["papers"]].index(keys)
            pbar.set_description(f"Processing index:{index1},paper:{keys} ")
            note = values['note']
            id = values['id']
            pdf = values['pdf']
            print("key:",keys)
            print("value:",values)

            if note is None and pdf is not None:
                print("note is None and pdf is None")
                print(note)

                note_id= self.create_note(id, pdf)

                if note_id:
                    try:
                        self.update_multiple_notes(sections_prompts=note_update,note_id=note_id,pdf=pdf
                                                   )
                    except:
                        return index

                else:
                        print("Failed to update item.")
                if note["headings"] is not None:
                    print("note heading")
                    print(note["headings"])
                    note_update1 = {k: v for k, v in note_update.items() if k in note["headings"]}
                    note_id = self.create_note(id, pdf)

                    if note_id:
                        try:
                            self.update_multiple_notes(sections_prompts=note_update1, note_id=note_id)
                        except:
                            return index1


    
    def update_multiple_notes(self,sections_prompts,note_id,pdf='',start_section=False):

        api = ChatGPT(**self.chat_args
                      )
        if self.chat_args.get("chat_id"):
            api.interact_with_page(path=pdf, copy=False)

    
        process=False
    
        # Assuming thematic_section is a dictionary
        total_iterations = len(sections_prompts)
        with tqdm(total=len(total_iterations), bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}]',
                  colour='blue') as pbar:

            for i, section_tuple in enumerate(sections_prompts.items(), 1):
                if start_section:
                    if section_tuple[0] == start_section:
                        process = True
                if not start_section:
                    process=True
                if i==13:
                    api.open_new_tab()
                if process:

                    pbar.set_description(f"Processing section {section_tuple[0]}",
                                         refresh=True)
                    update_dict = {section_tuple[0]: section_tuple[1]}  # Convert tuple to dictionary
                    pbar.set_description( f'Processing: {section_tuple[0]}')  # Update the processing text with current section
    
                    self.update_zotero_note_section(note_id=note_id, updates=update_dict,api=api)

    def extract_relevant_h2_blocks(self,html_content):
        soup = BeautifulSoup(html_content, 'html.parser')
        relevant_h2_blocks = []  # List to hold h2 texts that meet the specific conditions

        for element in soup.find_all(True):  # Iterating over all tags
            if element.name == 'h2':  # If it's an H2 element
                next_sibling = element.find_next_sibling(
                    text=False)  # Get the next non-text sibling (to check for actual content)
                if next_sibling:
                    sibling_text = next_sibling.get_text(" ", strip=True).lower()
                    # Check if the next non-text sibling starts with 'guidelines' or if there's no significant text following
                    if sibling_text.startswith('guidelines') or sibling_text == '':
                        relevant_h2_blocks.append(f"<h2>{element.get_text(strip=True)}</h2>")
                else:
                    # If there is no next sibling, the H2 has no content below it
                    relevant_h2_blocks.append(f"<h2>{element.get_text(strip=True)}</h2>")
        relevant_h2_blocks =  [i for i in relevant_h2_blocks if i in note_update.keys()]

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
    def get_children_notes(self,item_id):
        notes_info = []
        # Fetch all children of the item
        children = self.zot.children(item_id)
    
        # Filter out only the notes from the children
        notes = [child for child in children if child['data']['itemType'] == 'note']
        # Initialize a pretty printer

        # Print out each note's key and content
        for n,note in enumerate(notes):
            note_content = note['data']["note"]
            note_id = note['data']["key"]
            heading_pattern = re.compile(r'<h\d>(.*?)<\/h\d>', re.IGNORECASE)

            if heading_pattern.findall(note_content):
                reemaining_h2 =self.extract_relevant_h2_blocks(note_content)
                data = {"note_id": note_id, "headings": reemaining_h2}
                current_tags = note['data']['tags']
                print(note)
                print("current tags:",current_tags)
                if reemaining_h2==[] and not current_tags:
                        note['data']['tags'] = [{"tag":"note_complete"}]  # Replace existing tags with new ones
                        print("note completed")
                        self.zot.update_item(note)



                return data
            else:
                return None


