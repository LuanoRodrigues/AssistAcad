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
    # "conversation_id":'208296a2-adb8-4dc0-87f2-b23e23c0fc79',
    "chat_id": "meu",
    "os":"win"
}

zt=Zotero(
library_id = library_id,
    api_key=api_key,
    library_type =library_type,

    chat_args=chat_args,
    os="win",
    sleep=12





)


# collection_data =zt.get_or_update_collection(update=False,collection_name="lawful evidence")

# data =[ (t,i) for t,i in collection_data[("items")]["papers"].items()]
# for keys, values in data:
#     print("keys", keys)
#     # Dynamically update the description with the current key being processed
#     index1 = [i for i in collection_data["items"]["papers"]].index(keys)
#     print(index1)

# zt.update_all("lawful evidence",update=False,
#               index=4,
#               #article_title="",
#               specific_section=to_delete,delete=True)

# zt.update_all("lawful evidence",update=True,
#               index=0,
#               # article_title="Evidentiary Issues in International Disputes Related to State Responsibility for Cyber Operations",
#               specific_section=new_section)
#
zt.update_all("lawful evidence",update=False,
              # index=0,
              article_title="Network investigations of cyber attacks: the limits of digital evidence",
              # specific_section="<h2>2.4 Structure and Keywords</h2>"
              )



# data =zt.extract_relevant_h2_blocks(note_id="IPEHN9SC")
#
# data = zt.extract_insert_article_schema(note_id="IPEHN9SC",save=True)
#
# print(data)

