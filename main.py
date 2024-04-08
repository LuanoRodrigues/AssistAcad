import time
import urllib

from bs4 import BeautifulSoup
from tqdm import tqdm

from Zotero_module.zotero_data import note_update,test,sections_prompt
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


zt.update_all(collection_name="lawful evidence",update=True)
# zt.update_all2(collection_name="cyber interference",update=True)

# zot =zt.connect()
# note = zot.item("7QE3D2H6")['data']['note']
# print(note)
# #
# collection =zt.get_or_update_collection(collection_name="lawful evidence",update=False)
# data = [(t, i) for t, i in collection["items"]["papers"].items()]
# for n,item in enumerate(data):
#     print(n,item)
#     print("\n")



# note =zt.get_children_notes("ZPS98M2N")
# print(note['headings'])
# print(note['content'])
# zt.update_multiple_notes(sections_prompts=test,note_id='7QE3D2H6',pdf=d["pdf"])
#
from gpt_api import chat_response
pdf_path = r'C:/Users/luano/Zotero/storage/SXBVWHDG/Abhijeet Shrivastava_2022.pdf'
query = sections_prompt["<h2>1.1 Research Framework</h2>"]
res = chat_response(pdf_path,query=query)
print(res)