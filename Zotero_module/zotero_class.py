import os
import ast
import time
import pickle
from bs4 import BeautifulSoup
import pprint
from Pychat_module.Pychat import ChatGPT
import pyzotero
from pyzotero import zotero
from Zotero_module.zotero_data import note_update,initial_prompt,thematic_section, new_data,tags_prompt
from tqdm import tqdm
import requests
import re
from datetime import datetime
api_key = os.environ.get("wos_api_key")

class Zotero:
    def __init__(self,
                 library_id="<Library ID>",
                 library_type='user',
                 api_key="<API KEY>",
                 chat_args = { "chat_id": "pdf"}
                 ):
        self.library_id = library_id
        self.library_type = library_type
        self.api_key = api_key
        self.zot = self.connect()

        self.chat_args = chat_args

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
                        # Process each item in this batch
                        with tqdm(total=len(collection_items), bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}]',
                                  colour='green') as pbar:

                            for item in collection_items:
                                item_data = item['data']
                                item_type = item_data['itemType']

                                if item_type == 'note':

                                    note_content = item_data['note']
                                    quote= "<h2>1.1 Research Question</h2"
                                    if note_content.find(quote):

                                        note_data = {'id': item_data['key'], 'content': note_content}

                                elif item_type not in ['note', 'attachment', 'linkAttachment', 'fileAttachment',
                                                       'annotation']:
                                    paper_title = item_data.get('title', 'No Title')
                                    pbar.set_description(f"processing {paper_title}")

                                    paper_key = item_data['key']
                                    paper_data = {'id': paper_key, 'pdf': None, "note":note_data}
                                    # Process attachments if present
                                    if 'attachment' in item['links']:
                                        attachment_link = item['links']['attachment']['href'].split("/")[-1]
                                        directory = f"C:\\Users\\luano\\Zotero\\storage\\{attachment_link}"
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

    def update_zotero_item_tags(self,api="",item_id="",item=False):
    
    

        if not item:
        # Retrieve the latest version of the item
            item = zot.item(item_id)
    
        if item:
    
            if 'attachment' in item['links']:
                # Extract the 'href' value from the 'attachment' link
                attachment_link = item['links']['attachment']['href'].split("/")[-1]
                directory = f"C:\\Users\\luano\\Zotero\\storage\\{attachment_link}"
    
                # Pdf
                # Replace this with your actual storage path
                for root, dirs, files in os.walk(directory):
                    for file in files:
                        if file.endswith(".pdf"):
                            pdf_path = os.path.join(root, file)
    
            new_tags = ast.literal_eval(api.interact_with_page(prompt=tags_prompt, path=pdf_path,copy=True))
            print("new tags:",new_tags)
            new_tags = [{"tag":tag.strip().lower()} for tag in new_tags]
            item['data']['tags'] = new_tags  # Replace existing tags with new ones
    
            # Update the item on the server
            try:
                updated_item = zot.update_item(item)
                return updated_item  # Return the updated item
            except pyzotero.zotero_errors.PreConditionFailed as e:
                print("Item version conflict detected. Retrieving the latest version and retrying.",e)
                latest_item = zot.item(item_id)  # Get the latest version of the item
                latest_item['data']['tags'] = new_tags  # Update tags on the latest version
                updated_item = zot.update_item(latest_item)
                return updated_item
        else:
            return None  # Item was not found
    
    
    
    def create_note(self,item_id,path):
    
    
        # Fetch the item by ID
        item = zot.item(item_id)
        # tags = ["tag1", "tag2", "tag3", "tag4"]
    
        # Fetch the item by ID
        item = zot.item(item_id)
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
                 f'DO=("{doi}") OR '
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
        now = datetime.datetime.now().strftime("%d-%m-%Y at %H:%M")
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
        new_note = zot.create_items([{
            "itemType": "note",
            'parentItem': item_id,
            "note": note_content,
    
    
        }])
    
        print("New note created:", new_note)
        time.sleep(15)
        new_note_id =new_note['successful']['0']['data']['key']
    
        if new_note_id:
            note = zot.item(new_note_id)
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
                response = zot.update_item(updated_note)
                if response:
                    print("Note updated successfully.")
                    return new_note_id
                else:
                    print("Failed to update the note.")
            except Exception as e:
                print(f"An error occurred during the update: {e}")
    
    
    def get_items_in_collection(self,collection_id,tag=False):
        items_data = []
    
        # URL for the items in the collection
        url = f'https://api.zotero.org/users/{self.library_id}/collections/{collection_id}/items'
        headers = {
            'Zotero-API-Key': self.api_key
        }
        pdf_path  = None
        # Get items in the collection
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            items = response.json()
            attachment_link =None
    
            for item in items:
                metadata = item['data']
                # Assuming your data structure is stored in a variable named `item`
                # Assuming the variable 'item' holds your data
                if item['data']['itemType'] not in ['attachment', 'note','annotation']:
                    # Check if 'attachment' is a key in the 'links' dictionary
                    if 'attachment' in item['links']:
                        # Extract the 'href' value from the 'attachment' link
                        attachment_link = item['links']['attachment']['href'].split("/")[-1]
                        file_id = metadata.get('key')
    
    
                        directory = f"C:\\Users\\luano\\Zotero\\storage\\{attachment_link}"
    
                        # Pdf
                        # Replace this with your actual storage path
                        for root, dirs, files in os.walk(directory):
                            for file in files:
                                if file.endswith(".pdf"):
                                    pdf_path = os.path.join(root, file)
                                    data = {"id":file_id,"pdf":pdf_path}
                                    items_data.append(data)
                                    # # updated_item = update_zotero_item_tags(file_id)
                                    # updated_item = create_note(file_id, pdf_path)
                                    # if updated_item:
                                    #     print("Item updated successfully.")
                                    # else:
                                    #     print("Failed to update item.")
    
                        print("-" * 50)
                    else:
                        return
                else:
                    pass
            return items_data
        else:
            print(f"Failed to retrieve items: {response.status_code}")
    
    import re
    
    
    def update_zotero_note_section(self,note_id, updates,api):
        """
        Update specific sections of a Zotero note by item ID. Sections will only be updated if they currently have no content,
        except for 'Thematic Review', which will append new content to the end.
        """
        # Retrieve the current note content
    
        note = zot.item(note_id)
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
                response = zot.update_item(updated_note)
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
        note = zot.item(note_id)
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
            response = zot.update_item(updated_note)
            if response:
                print("Note updated successfully.")
            else:
                print("Failed to update the note.")
        except Exception as e:
            print(f"An error occurred during the update: {e}")

    
    def update_all(self,collection_data,index,tag=False):
        api = ChatGPT(**self.chat_args
                      )
        data =[ (t,i) for t,i in collection_data["items"]["papers"].items() ][index:]
        # Setting up the tqdm iterator
        pbar = tqdm(data,
                    bar_format="{l_bar}{bar:30}{r_bar}{bar:-30b}",
                    colour='green')
    
        for keys, values in pbar:
            # Dynamically update the description with the current key being processed
            index = [i for i in collection_data["items"]["papers"]].index(keys)
            pbar.set_description(f"Processing index:{index},paper:{keys} ")
    
            id = values['id']
            pdf = values['pdf']
            # updated_item = update_zotero_item_tags(file_id)
            if not tag:
                note_id= self.create_note(id, pdf)
    
                if note_id:
                    try:
                        print(note_id)
                        api.interact_with_page(path=pdf, prompt=initial_prompt)
    
                        self.update_multiple_notes(sections_prompts=note_update,note_id=note_id,api=api)
                        api.open_new_tab()
                        api.interact_with_page(path=pdf, prompt=initial_prompt)
                        self.update_multiple_notes(sections_prompts=thematic_section,note_id=note_id,api=api)
                        api.open_new_tab()
                        api.interact_with_page(path=pdf, prompt=initial_prompt)
                        self.update_multiple_notes(sections_prompts=new_data,note_id=note_id,api=api)
                    except:
                        return index
    
                else:
                    print("Failed to update item.")
            if tag:
                self.update_zotero_item_tags(api=api,item_id=id)
    # collection_data =get_or_update_collection("lawful evidence", update=False)
    #
    # update_all(collection_data=collection_data)
    
    def update_multiple_notes(self,sections_prompts,note_id,pdf='',api=False,start_section=False):
        if not api:
            api = ChatGPT(**self.chat_args
                          )
            if self.chat_args.get("chat_id"):
                api.interact_with_page(path=pdf, prompt=initial_prompt)
    
    
        process=False
    
        # Assuming thematic_section is a dictionary
        total_iterations = len(sections_prompts)
    
        with tqdm(total=total_iterations, desc="Processing sections",
                  bar_format="{l_bar}{bar:30}{r_bar}{bar:-30b}", colour='blue') as pbar:
            for i, section_tuple in enumerate(sections_prompts.items(), 1):
                if start_section:
                    if section_tuple[0] == start_section:
                        process = True
                if not start_section:
                    process=True
    
                if process:
                    pbar.set_postfix_str(f"Processing section {section_tuple[0]}",
                                         refresh=True)  # Optionally, update the postfix to display the current section being processed
                    #
                    # # Check if it's the 'Thematic Review' section which expects multiple updates
                    # if section_tuple[0] == '<h2>Thematic Review</h2>':
                    #     api.open_new_tab()
                    #
                    #     api.interact_with_page(path=pdf,prompt=initial_prompt)
                    #
                    #     for value in section_tuple[1]:  # section_tuple[1] should be the list of updates for Thematic Review
                    #         update_dict = {section_tuple[0]: value}  # Create a dictionary from the tuple
                    #
                    #         update_zotero_note_section(note_id, update_dict, pdf)
                    # else:
                    #
    
                        # For sections that are not 'Thematic Review', update normally
                    update_dict = {section_tuple[0]: section_tuple[1]}  # Convert tuple to dictionary
                    print("this is the dict for section {}",update_dict)
                    pbar.set_description( f'Processing: {section_tuple[0]}')  # Update the processing text with current section
    
                    self.update_zotero_note_section(note_id=note_id, updates=update_dict,api=api)
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
    
    
    
                for i, section_tuple in enumerate(thematic_section.items(), 0):
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
        global zot  # Use the global Zotero instance
    
        # Fetch all children of the item
        children = zot.children(item_id)
    
        # Filter out only the notes from the children
        notes = [child for child in children if child['data']['itemType'] == 'note']
        # Initialize a pretty printer
        pp = pprint.PrettyPrinter(indent=4)
    
        # Print out each note's key and content
        for n,note in enumerate(notes):
            note_info = {f'key {str(n+1)}': note['data']['key'], 'note': note['data']['note']}
            pp.pprint(note_info)  # Pretty print the note information
        return notes

