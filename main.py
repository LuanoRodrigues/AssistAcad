from bs4 import BeautifulSoup

from Zotero_module.zotero_data import sections_prompt,note_update
from Zotero_module.zotero_class import  Zotero
from dotenv import load_dotenv
load_dotenv()  # loads the variables from .env
import os

# Accessing environment variables
library_id = os.environ.get("LIBRARY_ID")
api_key = os.environ.get("API_KEY")
library_type = os.environ.get("LIBRARY_TYPE")
token = os.environ.get("TOKEN")



chat_args = {
    "session_token":token,
    # "conversation_id":'704515c1-fb81-4a3b-a291-1b84568c4b16',
    "chat_id": "meu",
    "os":"win"
}

zt=Zotero(
library_id = library_id,
    api_key=api_key,
    library_type =library_type,

    chat_args=chat_args,
    os="win",
    sleep=8





)

# cool= zt.fetch_details('zotero', update=True, fetch_type='items')
# print(len(cool))
# for i in cool:
#     print(i)
# #
# collection_data =zt.get_or_update_collection(update=False,collection_name="lawful evidence")

# data =[ (t,i) for t,i in collection_data[("items")]["papers"].items()]
# for keys, values in data:
#     print("keys", keys)
#     # Dynamically update the description with the current key being processed
#     index1 = [i for i in collection_data["items"]["papers"]].index(keys)
#     print(index1)
note= "Take your time, review the final output for accuracy and consistency in HTML formatting and citation-context alignment.\nnote 1: citation should be provided in a short sentence strictly extracted from the pdf exactly as it is.\nnote2:output format:all output in a single  div in a code block."

to_delete= dict.fromkeys(["<h2>2.1 Data, Analysis and Epistemologies</h2>","<h2>2.2 Theoretical Framework or Models</h2>","<h2>2.3 Implications and Policy</h2>","<h2>3.3 Thematic Analysis 1</h2>","<h2>3.4 Thematic Analysis 2</h2>","<h2>3.5 Thematic Analysis 3</h2>" ],"")
# zt.update_all("lawful evidence",update=False,
#               index=4,
#               #article_title="",
#               specific_section=to_delete,delete=True)

# zt.update_all("lawful evidence",update=True,
#               index=0,
#               # article_title="Evidentiary Issues in International Disputes Related to State Responsibility for Cyber Operations",
#               specific_section=new_section)
#
# zt.update_all("lawful evidence",update=True,
#               # index=0,
#               # article_title="transparent attributions of cyberattacks to states?",
#               # specific_section="<h2>2.4 Structure and Keywords</h2>"
#               )
td = zt.extract_insert_article_schema("IPEHN9SC")
print("td =",td)
# zt.update_all("lawful evidence",update=True,)

file = r"C:\Users\luano\Downloads\reformatted_classified_items.json"
# zt.process_collections_file(file)
# zt.getting_infoFromJson(r"C:\Users\luano\Downloads\Academic_Writing_Attributes.json")
# zt.update_all(collection_name="lawful evidence",update=True)
# zt.evaluate(collection_name="examens2",update=True)

# zt.update_all2(collection_name="cyber deterrence",update=True)

# zot =zt.connect()
# note = zot.item("7QE3D2H6")['data']['note']
# print(note)
# #
# collection =zt.get_or_update_collection(collection_name="lawful evidence",update=False)
# data = [(t, i) for t, i in collection["items"]["papers"].items()]
# for n,item in enumerate(data):
#     print(n,item)
#     print("\n")








