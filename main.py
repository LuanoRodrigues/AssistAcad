import json
import time
from collections import defaultdict

import enchant
import nltk
import pdfplumber
from tqdm import tqdm

from Zotero_module.zotero_data import note_api,summary
from bs4 import BeautifulSoup
from pprint import pprint
from Zotero_module.zotero_data import sections_prompt,note_update,tag_prompt,summary_note
from Zotero_module.zotero_class import  Zotero
from Pychat_module.Pychat import  ChatGPT
from dotenv import load_dotenv
load_dotenv()  # loads the variables from .env
import os
from Pychat_module.gpt_api import process_pdf, process_document_sections, process_batch_output

# Accessing environment variables
library_id = os.environ.get("LIBRARY_ID")
api_key = os.environ.get("API_KEY")
library_type = os.environ.get("LIBRARY_TYPE")
token = os.environ.get("TOKEN")
# chat_name= "summary"
chat_name= "summary"



chat_args = {
    "session_token":token,
    # "conversation_id":'208296a2-adb8-4dc0-87f2-b23e23c0fc79',
    "chat_id": chat_name,
    "os":"win"
}

zt=Zotero(
library_id = library_id,
    api_key=api_key,
    library_type =library_type,

    chat_args=chat_args,
    os="win",
    sleep=71*3


)
prompt ="""Generate 3 questions in three dicts whose answers will be the text,system content. the output is jsonl format:{"messages":[{"role":"system","content":"You are an expert in responding questions from  academic papers statements, ensuring the output is formatted in HTML and includes in-text citations."},{"role":"user","content":[generate the question here about the following content assitant ]},{"role":"assistant","content":"While it is likely that international judicial forums will not relax standards of proof to accommodate the obvious cyber-challenges, circumstantial evidence is available as a potentially viable route to prove a violation. Since state to state disputes have been more commonly addressed in the International Court of Justice (‘‘ICJ / Court’’)” (Aravindakshan, 2021, p. 286)"}]}
 note1:the questions should not contain authors name. The questions should be academic about the academic topic. note2: output jsonl format in one line for every question in a codeblock"""


# zt.search_paragraphs_by_query(query="academic topic",collection_name='a')

pdf =r"C:\Users\luano\Zotero\storage\AZN6P3JU\(T Rid, B Buchanan, 2015).pdf"
# extract_citations_grobid(pdf_path=pdf,file_name="attributing.xml")
# update_quote(note_id="VWPNFE2J",pdf=pdf,zot=zt.zot,xml_path=xml)

# zt.processing_collection_paragraphs(collection_name='Law and evidence',
#                               insert_database=True,
#                               create_md_file=False,
#                               update_paragraph_notes=False,
#                               batch=False,
#                               store_only=False,
#                               update=False,
#                                     rewrite=False,
#                               # processing_batch=r'C:\Users\luano\Downloads\AcAssitant\Files\Batching_files\batch_qgQDngLBi0fdvibGZiJsnM6Q_output.jsonl'
# )

['9ASBYUZD','NTJLHS2W','SLTGCATF','WSZLFCRR','Y92SMUUI','6ZQUMIV6','3HQI2D4A','6LM42EYM','4VVH4ATW','76DQPE49','CIYMT97I',
 'CBN4QWJQ','CBN4QWJQ','3654M8FV','W63DA6Z6','75995D72','NJJ3GVR4','CF9BMSTC','AKGJNIUK','7CJPMXT8','G7KN4SYC','QIP2P6JZ',
 'J8QWBVHI','RMFZBFYI','GRHKF93L','MSU2EW6K','MAQNU48R','WL69LC46','XJM4QZ3Z','SDJNY2QQ','ZHHMAL3L']
'QGZYZT84 $7.65,ZHHMAL3L,'

# zt.insert_title_paragraphs(note_id='4APZPD5V',insert_database=True,zotero_collection="Law and evidence",update_paragraph_notes=False,rewrite=True)
s =zt.search_paragraphs_by_query(collection_name='Law and evidence',query='State responsibility')
for i in s['paragraph_text']:
    print(i)
# for k,v in s.items():
#     print('key',k)
#     print('value',v)


def writing_to_jsonl_from_batch_results(file_name):
    file_exists = os.path.isfile(file_name)
    a = process_batch_output(
        r'C:\Users\luano\Downloads\AcAssitant\Batching_files\batch_Ou8K1BjjLsinRQQ4yFfBzVva_output.jsonl')

    # Open the file in append mode if it exists, otherwise it will create it
    with open(file_name, 'a') as file:
        # If the file did not exist and is newly created, we don't need to prepend a newline
        if file_exists:
            # Add a newline before appending if the file already existed
            file.write('\n')
            for ids in a:
                # content = [i for i in eval(ids['content'].) if i['reference']!=[] ]
                content = ids['content']
                content2 = [content_inside for i in content if eval(i)['references'] for content_inside in
                            eval(i)['references']]
                if content2:
                    # Filter to keep only entries where 'ref' is numeric
                    seen_refs = set()
                    filtered_data = [x for x in content2 if
                                     x['ref'].isdigit() and x['ref'] not in seen_refs and not seen_refs.add(x['ref'])]

                    # Sort the filtered data by 'ref' as an integer
                    sorted_data = sorted(filtered_data, key=lambda x: int(x['ref']))
                    zt.validate_references(dict_list=sorted_data, file_name='resposta_chat.jsonl',
                                           pdf=r"C:\Users\luano\Zotero\storage\PC77HX8N\(Marco Roscini, Marco Roscini, 2015).pdf")

                    for entry in sorted_data:
                        file.write(json.dumps(entry) + '\n')  # Convert dict to JSON string and append a newline
                    print("jsonl file written in {}".format(file_name))
# writing_to_jsonl_from_batch_results('test.jsonl')
results = []
from Zotero_module.zotero_class import parse_headings_with_html_content
from NLP_module.foot_notes import extract_text_with_numbers_from_pdf
# Example usage (commented out):
# result = extract_sentences_by_reference_from_pdf("example.pdf")
# print(result)
# zt.create_citation_from_pdf(collection_name="Law and evidence",update=False,store_only=False,batch=True)

# pdf=r'C:\Users\luano\Zotero\storage\75BWFZS9\(Andrew Grotto, 2020).pdf'
# pdf =r"C:\Users\luano\Downloads\DOROTHÉE VANDAMME_10.pdf"
# pdf =r"C:\Users\luano\Zotero\storage\F9ZPYV3M\(KE Eichensehr, 2020).pdf"
# for i in range(11):
#     print({"ref": i+1, "preceding_text": "", "footnote": ""}
# )    zt.create_one_note(content=html_content,item_id='4VVH4ATW')    # Initialize an empty string to hold all relevant HTML content

pdf =r"C:\Users\luano\Zotero\storage\9WSSD7MF\(T Mikanagi, 2021).pdf"

# Parse the HTML with the improved function
# sections_improved = parse_headings_with_html_content(r"article_holder.html",pdf=pdf,parentItem='9ASBYUZD',h2_class='A title')
# zt.create_citation_from_pdf1(collection_name='state responsibility',update=False)
# zt.create_one_note(content=sections_improved,item_id='9ASBYUZD',tag='test')
# pprint(sections_improved)
# zt.create_one_note(content=sections_improved,item_id='4VVH4ATW')
# custom_id = "SV5QMQSM"  # Example paper ID
from Vector_Database.qdrant_handler import QdrantHandler

# # Find the collection associated with the custom_id
search_handler = QdrantHandler(qdrant_url="http://localhost:6333")
# collection_name = search_handler.find_collection_by_custom_id(custom_id)

from Vector_Database.embedding_handler import EmbeddingsHandler,query_with_history
emb =EmbeddingsHandler()
# Example: Query text for which we want to search similar paragraphs
query_text = "international law"
# Step 1: Retrieve the embedding (either from history or by generating a new one)
# query_embedding =  query_with_history(query_text)
# custom_id = search_handler.find_collection_by_custom_id(collection_name)
# #
# search =search_handler.advanced_search(collection_name='paper_NTJLHS2W',query_vector=query_embedding)
# print(search.keys())
# for paragraph in search['paragraph_text']:
#     print(paragraph)
# valid =search_handler.check_valid_embeddings()
#
# print(valid)
# # Step 2: Perform the search in the collection for top 10 similar paragraphs
# search_results = search_handler.advanced_search(
#     collection_name=collection_name,  # Now we should have a valid collection name
#     query_vector=query_embedding,  # The embedding for the query
#     top_k=10,  # Retrieve top 10 similar paragraphs
#     filter_conditions=None,  # No specific filter, searching across all data
#     with_payload=True,  # Return payload (paragraph text)
#     with_vectors=False,  # No need to return vectors
#     score_threshold=0.75,  # Only return results with a score >= 0.75 (optional)
#     offset=0,  # Starting from the first result
#     limit=10  # Limit to 10 results
# )
#
# # Step 4: Print out the results
# for result in search_results:
#     paragraph_text = result.payload.get('paragraph_text', "No paragraph text found")
#     score = result.score
#     print(f"Score: {score:.2f}, Paragraph: {paragraph_text}")