from time import sleep

import pandas as pd
import requests
import os
import xmltodict
from dotenv import load_dotenv
from dpla.api import DPLA
from elsapy.elsclient import ElsClient
from elsapy.elsprofile import ElsAuthor, ElsAffil
from elsapy.elsdoc import FullDoc, AbsDoc
from elsapy.elssearch import ElsSearch
import json

load_dotenv()  # loads the variables from .env
api_key = os.environ.get("wos_api_key")
ser_api_key = os.environ.get("ser_api_key")
DPLA_key = os.environ.get("DPLA_key")
ELSEVIER_KEY = os.environ.get("ELSEVIER_KEY")
SPRINGER_key =os.environ.get("SPRINGER_key")

def get_document_info1(query):
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
                result['keywords'] = hit.get('keywords').get('authorKeywords', )

                result['record_link'] = hit.get('links').get('record')
                result['citing_articles_link'] = hit.get('links').get('citingArticles')
                result['references_link'] = hit.get('links').get('reference')
                result['related_records_link'] = hit.get('links').get('related')
                result['citations'] = hit.get('citations')[0].get("count")

                return result

        else:
            print("No records found")
            return None

    else:
        # Print the status code and error message if the request failed
        print(f"Request failed with status code {response.status_code}: {response.text}")
        return None


def get_document_info2( query, author):
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



## Initialize client
client = ElsClient(ELSEVIER_KEY)

## Author example
# Initialize author with uri
my_auth = ElsAuthor(
        uri = 'https://api.elsevier.com/content/author/author_id/7004367821')
# Read author data, then write to disk
# if my_auth.read(client):
#     print ("my_auth.full_name: ", my_auth.full_name)
#     my_auth.write()
# else:
#     print ("Read author failed.")

## Affiliation example
# Initialize affiliation with ID as string
# my_aff = ElsAffil(affil_id = '60101411')
# if my_aff.read(client):
#     print ("my_aff.name: ", my_aff.name)
#     my_aff.write()
# else:
#     print ("Read affiliation failed.")

## Scopus (Abtract) document example
# Initialize document with ID as integer
# scp_doc = AbsDoc(scp_id = 84872135457)
# if scp_doc.read(client):
#     print("*"*100)
#
#     print ("scp_doc.title: ", scp_doc.title)
#     print(scp_doc.data)
#     scp_doc.write()
# else:
#     print ("Read document failed.")
#
# ## ScienceDirect (full-text) document example using PII
# pii_doc = FullDoc(sd_pii = 'S1674927814000082')
#
# if pii_doc.read(client):
#     print("*" * 100)
#     print ("pii_doc.title: ", pii_doc.title)
#     print(scp_doc.data)
#     pii_doc.write()
# else:
#     print ("Read document failed.")

## ScienceDirect (full-text) document example using DOI
# doi_doc = FullDoc(doi = '10.1002/1099-0682(200011)2000:11<2327::aid-ejic2327>3.0.co;2-6')
# if doi_doc.read(client):
#     print("*" * 100)
#     print ("doi_doc.title: ", doi_doc.title)
#     print(scp_doc.data)
#     doi_doc.write()
# else:
#     print ("Read document doi failed.")
# do_doc = FullDoc()
# if do_doc.read(client):
#     print("*" * 100)
#     print ("doi_doc.title: ", doi_doc.title)
#     print(scp_doc.data)
#     doi_doc.write()
# else:
#     print ("Read document doi failed.")
def format_dpla_results(items):
    formatted_results = []
    for item in items:
        # Extract key metadata
        title = item['sourceResource'].get('title', 'No title available')
        creator = item['sourceResource'].get('creator', 'Unknown creator')
        subjects = [subject['name'] for subject in item['sourceResource'].get('subject', [])]
        item_link = item.get('@id', 'No link available')
        view_link = item.get('hasView', {}).get('@id', 'No view link available')

        # Format the result as a dictionary
        result = {
            'Title': title,
            'Creator': creator,
            'Subjects': ', '.join(subjects),
            'Item Link': item_link,
            'View Link': view_link
        }
        formatted_results.append(result)
    return formatted_results
def DOI_metadata(doi):
    """"
    Collecting data from OpenURL service:
    Journal,Title,Year and ISSN
    :parameter doi
    :type str
    :returns data(dict)
    """
    data = dict.fromkeys(['journal_title', 'article_title','year','DOI','issn'],'')
    data['DOI']=doi
    sleep(5)
    url = f'https://doi.crossref.org/openurl?pid=luanorodrigues@gmail.com&url_ver=Z39.88-2004&rft_id=info:doi/{doi}&noredirect=true'

    from requests.exceptions import Timeout
    try:
        r = requests.get(url)
        a = xmltodict.parse(r.content)

    except Timeout:
        raise Exception('deu ruim')

    results = a['crossref_result']['query_result']['body']['query']


    try:
        data['journal_title'] = results['journal_title']

        try:data['year'] = results['year']['#text']
        except:pass

        try:data['issn'] = results['issn'][0]['#text']
        except:pass

        try:data['article_title'] = results['article_title']
        except:pass

    except Exception as pt:
        print(pt)

    return data






def dpla_search(query):
    # Define your API key and initialize the DPLA object
    dpla = DPLA(api_key=DPLA_key)

    # Define the fields you want returned in your search
    fields = [
        "sourceResource.title",
        "sourceResource.date.begin",
        "sourceResource.identifier",
        "sourceResource.creator",
        "sourceResource.subject.name"
    ]

    # Perform the search
    result = dpla.search(q=query, fields=fields)

    # Initialize a list to hold cleaned results
    cleaned_results = []

    # Iterate through the items returned by the search
    for item in result.items:
        # Clean and reformat the data
        clean_item = {
            "Title": item.get("sourceResource.title", "No Title Provided"),
            "Date Begin": item.get("sourceResource.date.begin", "No Date Provided"),
            "Identifier": ", ".join(item.get("sourceResource.identifier", ["No Identifier Provided"])),
            "Creator": clean_creator(item.get("sourceResource.creator", "No Creator Provided")),
            "Subjects": ", ".join(item.get("sourceResource.subject.name", ["No Subjects Provided"]))
        }
        cleaned_results.append(clean_item)

    return cleaned_results


def clean_creator(creator):
    # Splitting the creator string to remove the URL if present
    if isinstance(creator, list):
        # Handling multiple creators, extracting names and ignoring URLs
        return ", ".join([name.split(", ")[0] for name in creator])
    else:
        # Assuming single creator, split by ',' and take the first part
        return creator.split(", ")[0]


def springer_search(query):
    # Define the API endpoint and your API key

    BASE_URL = 'http://api.springernature.com/meta/v2/json'

    # Construct the full API URL with the query and other parameters
    url = f"{BASE_URL}?q=title:{query}&api_key={SPRINGER_key}&p=10"  # adjust 'p' for more results

    # Send the GET request
    response = requests.get(url)
    response.raise_for_status()  # Ensure the request succeeded
    data = response.json()  # Parse the JSON response

    # Process and extract clean, useful metadata
    clean_results = []
    for item in data.get('records', []):
        # Process URLs

        # Extract and format URLs
        urls = []
        if isinstance(item.get('url'), list):
            for url_entry in item.get('url'):
                if url_entry.get('format') == 'html':
                    urls.append({"format": "html", "platform": "web", "value": url_entry.get('value')})
                elif url_entry.get('format') == 'pdf':
                    urls.append({"format": "pdf", "platform": "web", "value": url_entry.get('value')})
                urls.append({"format": "", "platform": "", "value": f"http://dx.doi.org/{item.get('doi', '')}"})
        else:
            # Fallback if URL format is unexpected
                urls.append({"format": "", "platform": "", "value": f"http://dx.doi.org/{item.get('doi', '')}"})
        creators = [{'ORCID': creator.get('orcid', ''), 'creator': creator.get('name', '')} for creator in item.get('creators', [])]

        # Construct the clean result dictionary
        clean_result = {
            'contentType': item.get('contentType', ''),
            'identifier': f"doi:{item.get('doi', '')}",
            'url': urls,
            'title': item.get('title', ''),
            'creators': creators,
            'publicationName': item.get('publicationName', ''),
            'openaccess': str(item.get('openaccess', False)).lower(),
            'doi': item.get('doi', ''),
            'publisher': item.get('publisher', ''),
            'publicationDate': item.get('publicationDate', ''),
            'publicationType': item.get('publicationType', ''),
            'issn': item.get('issn', ''),
            'eIssn': item.get('eIssn', ''),
            'startingPage': item.get('startingPage', ''),
            'endingPage': item.get('endingPage', ''),
            'abstract': item.get('abstract', ''),
            'keyword': [keyword for keyword in item.get('keyword', [])],
            'subjects': item.get('subjects', []),
            'disciplines': [{ 'term': discipline.get('term', '')} for discipline in
                            item.get('disciplines', [])]
        }

        clean_results.append(clean_result)

    return clean_results

