
from docx.oxml import parse_xml
from tqdm import tqdm
from Vector_Database.qdrant_handler import get_headings_for_clusters, write_and_export_sections, QdrantHandler
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

# write_and_export_sections()
# zt.search_paragraphs_by_query(query="academic topic",collection_name='a')

pdf =r"C:\Users\luano\Zotero\storage\AZN6P3JU\(T Rid, B Buchanan, 2015).pdf"
# extract_citations_grobid(pdf_path=pdf,file_name="attributing.xml")
# update_quote(note_id="VWPNFE2J",pdf=pdf,zot=zt.zot,xml_path=xml)

# zt.processing_collection_paragraphs(collection_name='Law and evidence',
#                               insert_database=False,
#                               create_md_file=True,
#                               update_paragraph_notes=False,
#                               batch=False,
#                               store_only=False,
#                               update=False,
#                                     rewrite=False,
#                               # processing_batch=r'C:\Users\luano\Downloads\AcAssitant\Files\Batching_files\batch_qgQDngLBi0fdvibGZiJsnM6Q_output.jsonl'
# )
#
# ['9ASBYUZD','NTJLHS2W','SLTGCATF','WSZLFCRR','Y92SMUUI','6ZQUMIV6','3HQI2D4A','6LM42EYM','4VVH4ATW','76DQPE49','CIYMT97I',
#  'CBN4QWJQ','CBN4QWJQ','3654M8FV','W63DA6Z6','75995D72','NJJ3GVR4','CF9BMSTC','AKGJNIUK','7CJPMXT8','G7KN4SYC','QIP2P6JZ',
#  'J8QWBVHI','RMFZBFYI','GRHKF93L','MSU2EW6K','MAQNU48R','WL69LC46','XJM4QZ3Z','SDJNY2QQ','ZHHMAL3L']
# 'QGZYZT84 $7.65,ZHHMAL3L,'

# zt.insert_title_paragraphs(item_id='XJM4QZ3Z',insert_database=True,zotero_collection="Law and evidence",update_paragraph_notes=False,rewrite=True)
keywords = {
    "AND": ["attribution","cyber"],  # All keywords must appear
    "OR": ["challenge", "legal"],  # Any one of these keywords can appear
    "NOT": ["introduction","section"]  # Exclude results with these keywords
}
bk="""<p><span class="highlight" data-annotation="%7B%22attachmentURI%22%3A%22http%3A%2F%2Fzotero.org%2Fusers%2F9047943%2Fitems%2FECG8EK5H%22%2C%22pageLabel%22%3A%22668%22%2C%22position%22%3A%7B%22pageIndex%22%3A25%2C%22rects%22%3A%5B%5B81.41109978000003%2C534.5510982100001%2C382.32010883999953%2C543.3311860100001%5D%2C%5B71.43300000000004%2C522.5319780200001%2C382.39810961999956%2C531.3120658200002%5D%2C%5B71.43300000000004%2C510.5698584000002%2C382.3881095199997%2C519.3499462000002%5D%2C%5B71.43300000000004%2C498.5507382100002%2C382.39154117%2C508.129292%5D%2C%5B71.43243161000001%2C486.53255821%2C382.41354139000015%2C495.31264601%5D%2C%5B71.43243161000001%2C474.23043519%2C382.4073854499997%2C484.23053518999996%5D%2C%5B71.43227573000001%2C462.55145820999996%2C382.4073854499997%2C471.33154600999995%5D%2C%5B71.43227573000001%2C450.53233801999994%2C382.3313846900002%2C459.31242581999993%5D%2C%5B71.43227573000001%2C438.57021839999993%2C382.41538552999975%2C447.3503061999999%5D%2C%5B71.43227573000001%2C426.2110948099999%2C382.39638533999965%2C436.2111948099999%5D%2C%5B71.43227573000001%2C414.5319780199999%2C382.3173845499995%2C423.3120658199999%5D%2C%5B71.43227573000001%2C402.5698583999999%2C242.1849832399999%2C411.34994619999986%5D%5D%7D%2C%22citationItem%22%3A%7B%22uris%22%3A%5B%22http%3A%2F%2Fzotero.org%2Fusers%2F9047943%2Fitems%2FY92SMUUI%22%5D%2C%22locator%22%3A%22668%22%7D%7D">“The development of new customary norms in cyberspace is further facilitated by the uniqueness of the domain. While the applicability of international law to the cyber context is now settled, the urgency of coping with new technologies enables customary law to come into existence very rapidly.201 In the same way that novel principles concerning sovereignty in outer space developed ‘instantly’ after the first satellites were launched,202 a due diligence standard of attribution might quickly develop with respect to cyberspace. On balance, instances of supportive State practice lack the quantum and uniformity to establish a crystallized or emerging customary norm. If, however, the United States’ response to the Sony and DNC hacks signals a newfound willingness to allege State responsibility following cyber operations, a due diligence standards of attribution might soon follow.”</span> <span class="citation" data-citation="%7B%22citationItems%22%3A%5B%7B%22uris%22%3A%5B%22http%3A%2F%2Fzotero.org%2Fusers%2F9047943%2Fitems%2FY92SMUUI%22%5D%2C%22locator%22%3A%22668%22%7D%5D%2C%22properties%22%3A%7B%7D%7D">(<span class="citation-item">Chircop, 2018, p. 668</span>)</span></p>
</blockquote>
"""
# zt.paragraphs_reports(report='report 1',collection_name='Law and evidence')
# F
# s =zt.search_paragraphs_by_query(collection_name='Law and evidence',query='What are the challenges in cyber attribution?',function='raw report',keyword=keywords,n_clusters=None)
# s=zt.paragraphs_reports(collection_name='Law and evidence',n_clusters=None,report='raw')
# for cluster in s:
#     print(cluster)
# n =0
# for n,i in s.items():
#     print('cluster:',n)
#     for content in i:
#         print(content['content'][0])
#
#     print("-"*10)

# for i in s['paragraph_text']:
#
#     print(type(i))
#     print('*'*10)
#
#     pprint(i)
#     n=n+1
#     print(n)



# for k,v in s.items():
#     print('key',k)
#     print('value',v)


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

# Find the collection associated with the custom_id
# get_bigram_matches(text='take over is what is good for us')
def workingWith_search():
    from Vector_Database.qdrant_handler import QdrantHandler

    search_handler = QdrantHandler(qdrant_url="http://localhost:6333")
    # Step 2: Perform the search in the collection for top 10 similar paragraphs
    search_results = zt.search_paragraphs_by_query(
        collection_name='Law and evidence',  # Now we should have a valid collection name
            query='Technical Challenges',  # The embedding for the query
        # top_k=10,  # Retrieve top 10 similar paragraphs
        filter_conditions=None,  # No specific filter, searching across all data
        with_payload=True,  # Return payload (paragraph text)
        with_vectors=False,  # No need to return vectors
        score_threshold=0.75,  # Only return results with a score >= 0.75 (optional)
        # offset=0,  # Starting from the first result
        # limit=10  # Limit to 10 results
    )
    print(len(search_results['paragraph_title']))
    # Step 4: Print out the results
    for titles in search_results['paragraph_title']:
        print(titles)

workingWith_search()
#
# handler.replace_custom_id_with_embedding(input_batch_path=r'C:\Users\luano\Downloads\AcAssitant\Files\Batching_files\batch_input.jsonl',
#                                  embedding_batch_path=r'C:\Users\luano\Downloads\AcAssitant\Files\batch_ElitxAYgCWaWoywtCRYFUHCP_output.jsonl',
#                                  output_file_path='trigrams_database.json')
