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
new_section = {
    # "<h2>1.4 Shortcomings Limitations</h2>": f"Guidelines:\nPerform an in-depth examination of the attached PDF document to identify and elucidate its shortcomings and limitations. Your analysis should scrutinize the document thoroughly, extracting specific instances where the paper acknowledges its own limitations or where you perceive potential weaknesses. Each identified shortcoming should be clearly explained and substantiated with multiple direct quotes from the document. ### Example HTML Structure for Presentation of Shortcomings and Limitations: ```html <div> <ul> <li><strong>Shortcoming 1:</strong> <p>[Explanation of the shortcoming]</p> <blockquote>“[Direct quote from the document illustrating the shortcoming.]” (Author, Year, p. XX)</blockquote> <blockquote>“[Another direct quote related to the same shortcoming.]” (Author, Year, p. XX)</blockquote> </li> <li><strong>Shortcoming 2:</strong> <p>[Explanation of the second shortcoming]</p> <blockquote>“[Direct quote illustrating the second shortcoming.]” (Author, Year, p. XX)</blockquote> <blockquote>“[Additional quote related to the second shortcoming.]” (Author, Year, p. XX)</blockquote> </li> <!-- Continue with additional shortcomings as identified --> </ul> </div> ``` This structured approach ensures a thorough presentation of the document's acknowledged limitations and perceived shortcomings, each supported by direct quotes for a nuanced understanding and critical analysis.{note}",
    # "<h2>2.2 Author References</h2>": [
    #     f"Guidelines: Read the PDF carefully, paragraph by paragraph, to identify the top ten in-text citations linked to footnotes that are most critical in supporting the main themes, arguments, and claims of the paper. For each citation: 1. Identify the citation format (e.g., superscript, bracketed number, inline text). 2. Match each citation to its corresponding footnote that starts with the same number and includes detailed bibliographic information. 3. Ensure each pair of citation and footnote is unique, directly linked to the sentence preceding the citation in the text, and accurately represents the source material. 4. In the output, structure each entry as follows in HTML: <h4>Author (year)</h4> <h5>[Footnote number + full footnote text including the starting number]</h5> <blockquote> <cite>[Exact sentence from the body text that precedes the footnote number, including the footnote number]</cite> </blockquote> <--Ensure each author is listed once with all associated references consolidated under their name if multiple references are present in a single footnote. Repeat for the top 10 authors in the document. your first response will contain 5 and next prompt I will ask for the remaining 5.-->{note}",
    #     "Proceed with the next 5 authors.",
    #     f"now Scan the PDF carefully, paragraph by paragraph, to identify the top 10 direct in-text citations relevant to the paper content. opposed to the previous prompt that checked footnotes, Focus specifically on intext citations that include author names in formats like '(author, year)', or are introduced by phrases such as 'according to', 'as noted by', or verbs like 'proposes', 'advocates'. <div><h4>author name (year)</h4><blockquote><cite>[Exact sentence from the PDF where the author is mentioned, maintaining the original citation format]</cite></blockquote></div> Repeat for the top 10 authors in the document. your first response will contain 5 and next prompt I will ask for the remaining 5.{note}",
    #     "now,continue with the next 5 authors please enclosed in one single div in block code."],
    # "<h2>2.3 Entity Reference</h2>": [
    #     f"now Scan the PDF document paragraph by paragraph, extracting in-text citations that specifically mention entities such as the organisations, companies etc. Document each citation in HTML format as follows: <div><h4>Entity Name</h4><blockquote><cite>[Exact sentence from the PDF where the entity is mentioned, including any inline reference numbers]</cite></blockquote></div> Ensure the final output accurately reflects the context in which the entity is discussed in the text. Repeat for the top 10 entities in the document. your first response will contain 5 and next prompt I will ask for the remaining 5.{note} ",
    #     f"now, the next 5 entities please enclosed in one single div in block code. "],
    "<h2>2.4 Structure and Keywords</h2>": f"Guidelines:\n Please perform a thorough analysis based on the following guidelines and format the output as detailed in the provided div structure: 1. **Article Schema:** Outline the article's structure with main headings and subheadings. Aim to provide a comprehensive table of contents. 2. **Keyword Extraction:** Identify and list academic keywords or phrases crucial for systematic review coding. Concentrate on extracting terms reflecting the core themes and methodologies. Limit phrases to three words where possible. 3. **Detailed Analysis:** Break down your analysis into specific categories: - **Academic Fields and Research Areas:** Identify the 3 primary disciplines or fields. - **Themes and Topics:** Extract 7 detailed themes or topics[they should not exceed 4 words]. - **Methodologies Keywords:** Highlight keywords for coding, focusing on methods like 'qualitative analysis', 'quantitative analysis', 'mixed-methods analysis'; epistemologies like 'positivism', 'interpretivism', 'critical realism'; and theories like 'realism', 'liberalism', 'constructivism'. - **Countries and Regions:** Note 6 significant  countries specifing where they were found with context . - **Affiliations** Note 1 significant affiliations . Example structure: ```html <h3>Article Schema:</h3><ul><li>Abstract</li><li>Section 1: Title</li><li>Section 2: Title</li></ul><h4>Academic Fields and Research Areas:</h4><ul><li>Field 1</li><li>Field 2</li><li>Field 3</li></ul><h4>Themes and Topics:</h4><ul><li>Theme 1</li><li>Theme 2</li><!-- More themes as needed --></ul><h4>Methodologies Keywords:</h4><ul><li>Qualitative Analysis</li><li>Positivism</li><li>Realism</li><!-- More methodologies as needed --></ul><h4>Countries, and Regions:</h4><ul><li>Region 1 title (the short context where is was found)</li><li>Country 1(the short context where is was found)</li><!-- More regions and countries as needed --></ul><h4>Affiliations:</h4><ul><li>Affiliation 1 (affiliation information)</li><ul> ``` Ensure your analysis fills in the placeholders based on the document's content.{note}"
}
to_delete= dict.fromkeys(["<h2>2.1 Data, Analysis and Epistemologies</h2>","<h2>2.2 Theoretical Framework or Models</h2>","<h2>2.3 Implications and Policy</h2>","<h2>3.3 Thematic Analysis 1</h2>","<h2>3.4 Thematic Analysis 2</h2>","<h2>3.5 Thematic Analysis 3</h2>" ],"")
# zt.update_all("lawful evidence",update=False,
#               index=4,
#               #article_title="",
#               specific_section=to_delete,delete=True)

# zt.update_all("lawful evidence",update=True,
#               index=0,
#               # article_title="Evidentiary Issues in International Disputes Related to State Responsibility for Cyber Operations",
#               specific_section=new_section)

zt.update_all("lawful evidence",update=False,
              index=0,
              article_title="transparent attributions of cyberattacks to states?",
              specific_section=new_section
              )

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








