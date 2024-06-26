import time

from bs4 import BeautifulSoup

from Zotero_module.zotero_data import sections_prompt,note_update,tag_prompt
from Zotero_module.zotero_class import  Zotero
from Pychat_module.Pychat import  ChatGPT
from dotenv import load_dotenv
load_dotenv()  # loads the variables from .env
import os

# Accessing environment variables
library_id = os.environ.get("LIBRARY_ID")
api_key = os.environ.get("API_KEY")
library_type = os.environ.get("LIBRARY_TYPE")
token = os.environ.get("TOKEN")
chat_name= "evaluator"


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
    sleep=1*60





)


# collection_data =zt.get_or_update_collection(update=False,collection_name="lawful evidence")

# data =[ (t,i) for t,i in collection_data[("items")]["papers"].items()]
# for keys, values in data:
#     print("keys", keys)
#     # Dynamically update the description with the current key being processed
#     index1 = [i for i in collection_data["items"]["papers"]].index(keys)
#     print(index1)
# try:
#
#     print(zt.update_all(
#         "Law and evidence",
#         # "cyber due diligence",
#                         update=True
#     #               article_title="transparent attributions of cybera attacks to states?",
#     #               specific_section="<h2>2.1 Main Topics</h2>"
#
#                  ))
# except:
#     pass
# time.sleep(60*30)


# try:
#     print(zt.update_all(
#
#         "cyber due diligence",
#                         update=True
#     #               article_title="transparent attributions of cybera attacks to states?",
#     #               specific_section="<h2>2.1 Main Topics</h2>"
#
#                  ))
# except:
#     pass
# # time.sleep(60*30)
# print(zt.update_all(
#     "saved",
#     # "cyber due diligence",
#                     update=True
# #               article_title="transparent attributions of cybera attacks to states?",
# #               specific_section="<h2>2.1 Main Topics</h2>"
#
#              ))
# zt.evaluate("marking",tag_prompt,update=True)
# zt.rename_files_in_directory(r"C:\Users\luano\Downloads\17841037","-")
# zt.process_files_in_directory(r"C:\Users\luano\Downloads\17841037","marking")

# zt.process_collections_file("saved")
# data =zt.get_children_notes("BSRRQ7HD")
# data =zt.update_quotes("BSRRQ7HD",pdf=r"C:\Users\luano\Zotero\storage\LHZRBA2H\Johnson and Schmitt - 2021 - Responding to proxy cyber operations under international law.pdf",author="(Schmit,2015)",stop_words="")

# data =zt.get_or_update_collection("Law and evidence",False)
# data1 =[ (t,i) for t,i in data[("items")]["papers"].items()][::-1]
# for t,i in data1:
#     print(t)
#     print(i["note"]["headings"])

# data= zt.get_or_update_collection("Law and evidence",update=False)
# data1 =[(t,i["note"]["note_id"]) for t,i in data[("items")]["papers"].items() if i["note"]["note_id"]][4:]
# for t,i in data1:
#
#     try:
#         zt.extract_insert_article_schema(note_id=i,save=True)
#     except:
#         print(t)
# data =zt.extract_relevant_h2_blocks(note_id="IPEHN9SC")
#
# data = zt.extract_insert_article_schema(note_id="WQNGS522",save=True)
#
# print(data)
# ONE ZOTERO NOTE
# zt.update_zotero_note_section(updates=        {f'<h2><span style="color: #05a2ef">2.4 Structure and Keywords</span></h2>': f"""Guidelines:Please perform a thorough analysis of the document based on the following guidelines and format the results in HTML as detailed. Ensure that the format is scalable and applicable to any PDF document for analysis.", "TOC": "Extract the Table of Contents from the document. List only the main headings as they appear in the document, without adding or assuming subheadings unless explicitly mentioned in the document.", "Keyword Extraction": "Identify and list academic keywords or phrases crucial for systematic review coding, with a limit of three words per phrase.", "Detailed Analysis": [{{"Category": "Academic Fields and Research Areas", "Instruction": "Identify the three primary disciplines or fields discussed in the document."}}, {{"Category": "Themes and Topics", "Instruction": "Extract up to seven detailed themes or topics discussed in the document, ensuring each theme or topic does not exceed four words."}}, {{"Category": "Research Types", "Instruction": "List the main type of research found in the document under appropriate subcategories:", "Subcategories": [{{"Type": "Data Collection Methods", "List": ["Primary Research", "Secondary Research"]}}, {{"Type": "Data Types", "List": ["Qualitative Data", "Quantitative Data", "Mixed Methods"]}}]}}, {{"Category": "Research Designs", "Instruction": "Identify and list the research designs mentioned in the document, including but not limited to:", "List": ["Experimental", "Evaluation", "Exploratory", "Descriptive", "Case Study"]}}, {{"Category": "Countries and Regions", "Instruction": "List significant countries or regions discussed, specifying only the names as they appear in the document."}}, {{"Category": "Affiliations", "Instruction": "List any significant affiliations mentioned in the document, providing only the name of the institutions without additional context."}}], "Example Output Structure": "<h3>TOC:</h3><ul><li>[Main Heading from the document]</li><!-- More main headings as found in the document --></ul><h4>Academic Fields and Research Areas:</h4><ul><li>[Field 1]</li><li>[Field 2]</li><li>[Field 3]</li></ul><h4>Themes and Topics:</h4><ul><li>[Theme 1]</li><li>[Theme 2]</li><!-- More themes as needed --></ul><h4>Data Collection Methods:</h4><ul><li>[Primary Research or Secondary Research ]</li></ul><h4>Data Types:</h4><ul><li>[Qualitative Data OR Quantitative Data OR Mixed Methods]</li></ul><h4>Research Designs:</h4><ul><li>[one or two of the research designs]</li><!-- More designs as needed --></ul><h4>Countries and Regions:</h4><ul><li>[Country Name 1]</li><!-- More countries as needed --></ul><h4>Affiliations:</h4><ul><li>[Affiliation Name 1]</li><!-- More affiliations as needed --></ul>"""},
# )
