from bs4 import BeautifulSoup

from Zotero_module.zotero_data import sections_prompt
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
os="win")

# collection = zt.get_or_update_collection(collection_name="lawful evidence",update=True)
# collection2 = zt.get_or_update_collection(collection_name="cyber due dilligence",update=False)
# collection3 = zt.get_or_update_collection(collection_name="state responsibility",
#                                           update=True,
#                                           tag="replace"
#                                     )



zt.update_all(collection_name="lawful evidence",update=True)
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



# note =zt.get_children_notes("ZPS98M2N")
# print(note['headings'])
# print(note['content'])
# zt.update_multiple_notes(sections_prompts=test,note_id='7QE3D2H6',pdf=d["pdf"])
embeddings_file = "embeddings.json"

from Pychat_module.gpt_api import chat_response
# pdf_processor = PDFEmbeddingProcessor()
pdf_path = r'C:/Users/luano/Zotero/storage/SXBVWHDG/(Abhijeet Shrivastava, 2022).pdf'
query = sections_prompt["<h2>1.1 Research Framework</h2>"]
a = {"<h2>1.1 Research Framework</h2>": "<div> <h3>Research Type:</h3> <ul> <li>Exploration</li> <li>Description</li> <li>Evaluation</li> </ul> <p>[Analyze the document to determine the research types, providing explanations with citations as examples.]</p> <h3>Study Objectives</h3> <ul> <li>Objective 1: [Define objective 1]</li> <li>Objective 2: [Define objective 2]</li> </ul> <p>[Identify study objectives from the document, supported by direct citations.]</p> <h3>Research Problem</h3> <ul> <li>[Outline the central research problem/problematique of the article.]</li> </ul> <h4>Research Questions</h4> <ul> <li>Question 1: [State the question]</li> <blockquote>'[Support with a direct citation]'</blockquote> <h5>Hypotheses</h5> <li>Hypothesis 1: [Formulate the hypothesis]</li> <blockquote>'[Support with a direct citation]'</blockquote> </ul> </div>.Provide responses formatted as an HTML div"}

# res = chat_response(pdf_path=pdf_path, query=query)
# print(res)
# d= main(pdf_path=pdf_path,prompts_dict=a)










