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
# print(zt.extract_insert_article_schema('WXW2NV5W',save=True))
# zt.update_all(collection_name="state responsibility",update=True)
# zt.creating_training_data_from_statements("Law and evidence",False)
# zt.insert_title_paragraphs(note_id='SV5QMQSM')
# zt.attach_file_to_item(file_path=r'C:\Users\luano\Downloads\AcAssitant\new.md', parent_item_id='NTJLHS2W', tag_name='md paragraph')
print(zt.get_children_notes(item_id='NTJLHS2W',new_filename='saaa'))
prompt ="""Generate 3 questions in three dicts whose answers will be the text,system content. the output is jsonl format:{"messages":[{"role":"system","content":"You are an expert in responding questions from  academic papers statements, ensuring the output is formatted in HTML and includes in-text citations."},{"role":"user","content":[generate the question here about the following content assitant ]},{"role":"assistant","content":"While it is likely that international judicial forums will not relax standards of proof to accommodate the obvious cyber-challenges, circumstantial evidence is available as a potentially viable route to prove a violation. Since state to state disputes have been more commonly addressed in the International Court of Justice (‘‘ICJ / Court’’)” (Aravindakshan, 2021, p. 286)"}]}
 note1:the questions should not contain authors name. The questions should be academic about the academic topic. note2: output jsonl format in one line for every question in a codeblock"""
# zt.multilple_prompts(prompt=prompt)
# zt.extract_insert_article_schema(note_id="7WI5RJFA",save=True)
# zt.update_all("Law and evidence",update=True)
# zt.statements_citations(collection_name="Law and evidence",batch=False,update=True  ,store_only=False,chat=True,section=tag_prompt[0],follow_up=True)

# zt.statements_citations(collection_name="nova",batch=False,update=True,store_only=False,chat=False,sections=note_api,)
# print(zt.get_children_notes("76DQPE49"))


# prompt = "Please analyze this document and extract all key arguments, main ideas, and entire paragraphs with the author's original points in HTML format. Ensure 100% accuracy by extracting exact paragraphs without modification or paraphrasing. Focus on paragraphs representing the author's core arguments and ideas. Use <h2> for key ideas (3-4 words) and <blockquote> for exact paragraphs with references (author, year, page). Exclude paragraphs with cited statements (superscript numbers, in-text citations)."
# a = ['Limitations of public attribution and the need for legal attribution', 'Standards of proof in international law', 'Circumstantial evidence in context', 'The Corfu Channel rule: when circumstantial evidence was ‘‘Good Enough’’', 'The Bosnian Genocide case: when circumstantial evidence was not ‘‘Good Enough’’', 'Other international legal Jurisprudence', 'Cyberspace attribution: current status in brief', 'Circumstantial evidence in context', 'Conclusion']
# result = process_document_sections(file_path=r"C:\Users\luano\Zotero\storage\NREIF9TL\(Sharngan Aravindakshan, 2021).pdf",sections=a)
# zt.create_one_note(content=result,item_id="76DQPE49",api="",tag="pdf")


# result = process_pdf(r"C:\Users\luano\Downloads\DOROTHÉE VANDAMME_10.pdf", prompt,page_parsing=1,reference="(dorethe, 2018)")
# result = chat_response(pdf_path=pdf_path, query=prompt)
#
# zt.create_one_note(content=result,item_id="76DQPE49",api="",tag="citation")

# content = zt.get_content_after_heading("4UGZNIHB", "<h1>3. Summary</h1>", "h3")

from  Zotero_module.zotero_class import generate_zotero_annotation,extract_citations_grobid, get_last_four_tokens,find_phrase_in_pdf,replace_substring_and_check,parse_grobid_xml_to_dict



pdf =r"C:\Users\luano\Zotero\storage\AZN6P3JU\(T Rid, B Buchanan, 2015).pdf"
# extract_citations_grobid(pdf_path=pdf,file_name="attributing.xml")
# update_quote(note_id="VWPNFE2J",pdf=pdf,zot=zt.zot,xml_path=xml)

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
# )
