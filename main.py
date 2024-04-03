import time
import urllib

from bs4 import BeautifulSoup
from Zotero_module.zotero_data import note_update,test
from Zotero_module.zotero_class import  Zotero
import os
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
os="win")

# collection = zt.get_or_update_collection(collection_name="lawful evidence",update=True)
# # collection2 = zt.get_or_update_collection(collection_name="cyber due dilligence",update=False)
# collection3 = zt.get_or_update_collection(collection_name="state responsibility",
#                                           update=True,
#                                           tag="replace"
#                                     )
# loop = True
# while loop:
#     try:
#         loop = zt.update_all(collection_name="lawful evidence", update=True)
#         print(loop)
#     except Exception as e:
#         print(e)
#         time.sleep(60*30)


# zt.update_all(collection_name="lawful evidence",update=True)
# zot =zt.connect()
# note = zot.item("7QE3D2H6")['data']['note']
# print(note)
# #
# collection =zt.get_or_update_collection(collection_name="lawful evidence",update=True)
# data = [(t, i) for t, i in collection["items"]["papers"].items()][0:]
# for keys, values in data:
#     # Dynamically update the description with the current key being processed
#     index1 = [i for i in collection["items"]["papers"]].index(keys)
#     note = values['note']
#     id = values['id']
#     pdf = values['pdf']
#     print("key:", keys)
#     print("value:", values)
d ={'id': '76DQPE49', 'pdf': 'C:\\Users\\luano\\Zotero\\storage\\NREIF9TL\\Aravindakshan - 2021 - Cyberattacks a look at evidentiary thresholds in .pdf', 'note': {'note_id': '7QE3D2H6', 'headings': []}}
# print(zt.get_children_notes("5NNXUT6Q"))
# zt.update_multiple_notes(sections_prompts=test,note_id='7QE3D2H6',pdf=d["pdf"])


