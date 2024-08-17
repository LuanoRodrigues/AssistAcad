import time
from Zotero_module.zotero_data import note_api,summary
from bs4 import BeautifulSoup

from Zotero_module.zotero_data import sections_prompt,note_update,tag_prompt
from Zotero_module.zotero_class import  Zotero
from Pychat_module.Pychat import  ChatGPT
from dotenv import load_dotenv
load_dotenv()  # loads the variables from .env
import os
from Pychat_module.gpt_api import process_pdf,process_document_sections
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
    sleep=4*71





)
# zt.creating_training_data_from_statements("Law and evidence",False)
prompt ="""Generate 3 questions in three dicts whose answers will be the text,system content. the output is jsonl format:{"messages":[{"role":"system","content":"You are an expert in responding questions from  academic papers statements, ensuring the output is formatted in HTML and includes in-text citations."},{"role":"user","content":[generate the question here about the following content assitant ]},{"role":"assistant","content":"While it is likely that international judicial forums will not relax standards of proof to accommodate the obvious cyber-challenges, circumstantial evidence is available as a potentially viable route to prove a violation. Since state to state disputes have been more commonly addressed in the International Court of Justice (‘‘ICJ / Court’’)” (Aravindakshan, 2021, p. 286)"}]}
 note1:the questions should not contain authors name. The questions should be academic about the academic topic. note2: output jsonl format in one line for every question in a codeblock"""
# zt.multilple_prompts(prompt=prompt)
# zt.extract_insert_article_schema(note_id="7WI5RJFA",save=True)
zt.update_all("Law and evidence",update=True)
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

