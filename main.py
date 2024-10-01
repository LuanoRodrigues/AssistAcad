

from Zotero_module.zotero_class import  Zotero



from Pychat_module.Pychat import  ChatGPT
from dotenv import load_dotenv
load_dotenv()  # loads the variables from .env
import os

# """
# docker run -p 6333:6333 -v "C:\Users\luano\OneDrive - University College London\Database_articles:/qdrant/storage" qdrant/qdrant# """
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
# zt.update_all(collection_name='Law and evidence',update=True,article_title='A DUE DILIGENCE STANDARD OF ATTRIBUTION IN CYBERSPACE',pdf=False)

pdf =r"C:\Users\luano\Zotero\storage\AZN6P3JU\(T Rid, B Buchanan, 2015).pdf"
# extract_citations_grobid(pdf_path=pdf,file_name="attributing.xml")
# update_quote(note_id="VWPNFE2J",pdf=pdf,zot=zt.zot,xml_path=xml)
#rewrite ["75995D72","Y3EEKUDQ"]
zt.processing_collection_paragraphs(collection_name='Law and evidence',
                                    # item_start='Tre',
                              insert_database=True,
                              create_md_file=True,
                              update_paragraph_notes=False,
                              batch=False,
                              store_only=False,
                              update=False,
                                    rewrite=True,
                                    database_name='paragraph_title',
                                    overwrite_payload=False,
                                    # corpus=True
                              # processing_batch=r'C:\Users\luano\Downloads\AcAssitant\Files\Batching_files\batch_qgQDngLBi0fdvibGZiJsnM6Q_output.jsonl'
)


# a =zt.insert_title_paragraphs(item_id='NGCR7JSU',note_id='8ERNL6GE',insert_database=True,zotero_collection="Law and evidence",update_paragraph_notes=False,rewrite=True,overwrite_payload=False,database_name='paragraph_title',create_md_file=False,corpus=False)

root=r"C:\Users\luano\OneDrive - University College London\Obsidian\cyber evidence\test.md"
from Word_modules.md_config import convert_zotero_to_md_with_id
# keywords = call_openai_api(function='getting_keywords',
#                            data=bk,
#                            id='')
# keywords= {'keywords': {'topics': ['vulnerability countries', 'technical prowess', 'covert operations', 'government skills', 'industrialized nations'], 'entities': ['Rid e Buchanan'], 'academic_features': ['attribution logic']}}
# dt= zt.convert_to_obsidian_tags(keywords)
# print('keywords:',dt)
# data= convert_zotero_to_md_with_id(html_paragraph=bk,item_id='AZN6P3JU',keywords=dt)
#
# print(data)
# input('')
# with open(file=root,mode='w', encoding='utf-8') as f:
#     f.write(str(data))
# zt.paragraphs_reports(report='report 1',collection_name='Law and evidence',update=False,type_collection='paragraph_title')
# metadata = generate_cabecalho(zot=zt.zot, item_id="NGCR7JSU", dict_response=True, links=False)
# print(metadata['authors'])
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
from Vector_Database.qdrant_handler import QdrantHandler
#
import hashlib
# zt.summary_gpt()


data='“Each of the levels of the attribution process represents a discrete analytical challenge, relies on specific input data and specific expertise, and illuminates a separate aspect of successful attribution (see Figure 2). The analysis on each level needs to be informed and tempered by the others. Though the attribution process typically has a beginning and an end, the cycle does not necessarily follow a specific sequential or chronological order, as hypotheses are confronted with new details and new details give rise to new hypotheses in turn. Nevertheless, the layers represent separate tasks that, though they interrelate, will be analysed individually here. Usually so-called ‘indicators of compromise’ trigger the attribution process. Such indicators raise specific technical questions. More questions are likely to follow only after more facts have been gathered. On occasion, the attribution process may begin on the operational or strategic level. Sometimes the ‘first knowers’ of an incident will be above the technical level. Guided by non-forensic sources of intelligence, or by the broader geopolitical context — sometimes even by intuition — the possibility of malicious activity may be identified before technical indicators flag it, or indeed even before it begins. Attribution can go either way: the strategic and operational layers may inform the subsequent technical analysis, or vice versa.” (Rid e Buchanan, 2015, p. 9)'
# generate_paragraph_id("Each level of attribution presents unique challenges and requires specific expertise.")

# search_handler = QdrantHandler(qdrant_url="http://localhost:6333")
# search_handler.clear_and_set_payload(collection_name='75995D72_paragraph',new_payload={'test':'test'},point_id='34692445')

def workingWith_search():
    from Vector_Database.qdrant_handler import QdrantHandler

    # # Step 2: Perform the search in the collection for top 10 similar paragraphs
    # search_results = zt.search_paragraphs_by_query(
    #     type_collection='paragraph_title',
    #     collection_name='Law and evidence',  # Now we should have a valid collection name
    #         query='Findings',  # The embedding for the query
    #     # top_k=10,  # Retrieve top 10 similar paragraphs
    #     filter_conditions=None,  # No specific filter, searching across all data
    #     with_payload=True,  # Return payload (paragraph text)
    #     with_vectors=False,  # No need to return vectors
    #     score_threshold=0.7,  # Only return results with a score >= 0.75 (optional)
    #     # offset=0,  # Starting from the first result
    #     # limit=10  # Limit to 10 results
    # )
    # print(len(search_results['paragraph_title']))
    # # Step 4: Print out the results
    # for titles in search_results['paragraph_title']:
    #     print(titles)
#
def one_search():
    # Initialize the QdrantHandler
    search_handler = QdrantHandler(qdrant_url="http://localhost:6333")
    # search_handler.get_all_collections_payloads_and_save_csv()
    # Define your query and collection
    query = 'cyber*'
    collection_name = 'NGCR7JSU_paragraph_title'

    # Define keywords for filtering (optional)
    keywords = {
        "AND": ["network", "security"],
        "OR": ["attack", "breach"],
        "NOT": ["outdated"]
    }

    # Perform the search, using the cache if available
    results = search_handler.hybrid_search(collection_name=collection_name, query=query,update=True)
    print(results.keys())
    # Check if results are not empty before processing
    if not results:
        print("No results found.")
    else:
        # Print the results
        for title, text, score in zip(results['paragraph_title'], results['paragraph_text'],results['score']):
            print(f"Title: {title}\nText: {text}\n,score: {score}")


# one_search()
# workingWith_search()


# handler.replace_custom_id_with_embedding(input_batch_path=r'C:\Users\luano\Downloads\AcAssitant\Files\Batching_files\batch_input.jsonl',
#                                  embedding_batch_path=r'C:\Users\luano\Downloads\AcAssitant\Files\batch_ElitxAYgCWaWoywtCRYFUHCP_output.jsonl',
#                                  output_file_path='trigrams_database.json')




# parent={'title':'burden of proof', 'level':'h2','subsections': []}
# # Example usage:
# updated_response = update_response_with_paragraph_data(response=response, aggregated_paragraph_data=heading,parent=parent)
# print(updated_response)

