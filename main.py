import time
import urllib

from bs4 import BeautifulSoup
from Zotero_module.zotero_data import note_update
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
    # "conversation_id":'258d2f9d-9932-4d1e-9e0a-40d18e28ae22',
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


# zt.get_or_update_collection(collection_name="cyber interference",update=True,tag="replace")
# zot =zt.connect()
# note = zot.item("7QE3D2H6")['data']['note']
# print(note)
#
print(note_update.keys())