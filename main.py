import time

from bs4 import BeautifulSoup

from Zotero_module.zotero_data import sections_prompt,note_update,tag_prompt
from Zotero_module.zotero_class import  Zotero
from Pychat_module.Pychat import  ChatGPT
from dotenv import load_dotenv
load_dotenv()  # loads the variables from .env
import os
from Pychat_module.gpt_api import process_pdf
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

# pdf_path = r"C:\Users\luano\Zotero\storage\NREIF9TL\(Sharngan Aravindakshan, 2021).pdf" # Replace with your PDF file path
# # prompt = "1. Analyze the text to identify note and numerical citations. This includes statements followed by a number or a number in brackets/parentheses (e.g., 'international relations theories such as realism and neoliberalism are mainstream¹' or 'international relations theories such as realism and neoliberalism are mainstream (1)'). 2. Check if the same number corresponds to a statement preceded by the same number (e.g., '1. John S Davis II and others, ‘Stateless Attribution: Toward International Accountability in Cyberspace’ (RAND Corporation 2017) 21.'). If a sentence is preceded by a number and this number is found following a sentence, it means this is an in-text citation and a corresponding footnote. 3. Handle 'ibid' and similar terms: For 'ibid', repeat the last citation in <h1>, <h2>, and <h3>, updating the <blockquote> with the new statement. Maintain an internal index for footnotes to track references. 4. When a statement is followed by a number, treat it as body text and include it in a <blockquote> with the number highlighted in <strong> tags and the rest of the sentence or other citations not highlighted. 5. When a statement is preceded by a number, treat it as a footnote and include it in an <h2> tag. 6. For each citation, extract the author and year from the footnote information and use it in the <h3> tag. If no author is found, set the value to 'None'. 7. Format the output in HTML: - Use <h1> for the footnote number. - Use <blockquote> for the full sentence with the citation highlighted and other citations not highlighted. - Use <h2> for the footnote information in full. - Use <h3> for the author and year, or 'None' if not available. 8. Ensure 100% accuracy by extracting exact sentences and corresponding footnotes. 9. Handle multiple citations in a sentence by highlighting each citation individually and retrieving them separately. 10. If no citation is found, return '<div>N/A</div>'. 11. Output as a single HTML code block. Note 1: Do not return incomplete <h1>, <blockquote>, <h2>, or <h3> tags. Note 2: Highlight in bold only the corresponding in-text citation statement with the <h2> author and <h3>. Do not highlight every number, only the specific citation."
#
# # prompt = "1. Analyze the text to identify author citations, including variations like (Author, Year), (Author, Year, Page), and any direct mentions of authors or companies by name (e.g., 'Smith's conclusion is...', 'Author defends...', 'United Nations advocates...'). 2. Extract all statements where an author or company is mentioned. 3. Format the output in HTML: - Use <h2> for the citation in the format (Author, Year). - Use <blockquote> for the full sentence or statement where the author or company is cited, highlighting the author's name or company name in <strong> tags. 4. Ensure 100% accuracy by extracting exact sentences where authors or companies are cited and include their respective statements. 5. Handle multiple author citations or mentions within a sentence by extracting and highlighting each citation separately. 6. If no author or company citation is found, return '<div>N/A</div>'. 7. Output as a single HTML code block. Note 1: Do not return incomplete <h2> or <blockquote> tags. Note 2: Highlight only the specific author's or company's name within the <blockquote> tag."
# prompt = "Analyze the text to extract key terms and definitions using phrases like 'can be defined by', 'is described as', or 'means'; identify lists, typographic cues (e.g., bold or italics), and contextual keywords (e.g., 'definition', 'concept'); note citations following definitions; use <h3> for key terms and <blockquote> for exact definitions with citations; ensure accuracy and include multiple definitions if present; format output as a single HTML block, and return '<div>N/A</div>' if no definitions are found. Example output: <div><h3>[Key Term]</h3><blockquote>[Definition]</blockquote></div>."
#




# prompt = """
# Please analyze this document thoroughly and extract all key arguments, main ideas, and entire paragraphs containing the author's original points in an HTML format. Ensure 100% accuracy by extracting exact paragraphs as found in the document, without any modification or paraphrasing. Focus on capturing paragraphs that represent the author's core arguments and ideas.
#
# Output the results in a single code block using the following HTML structure:
# - Use <h2> tags for key arguments or main ideas, summarizing them in three or four words.
# - Use <blockquote> tags for entire paragraphs exactly as found in the text, with references (author, year, page).
#
# Exclude any paragraph that contains cited statements with superscript numbers, in-text citations (e.g., author, year), or any other form of reference to external sources.
#
# Example Output:
# <h2>Key Argument One</h2>
# <blockquote>
# Exact paragraph text from the document without any modifications, including proper citation formatting (author, year, page).
# </blockquote>
# """

# 1. Analyze the text to identify the citation type (parenthetical, numerical, or note).
# 2. For numerical and note citations, retrieve all statements followed by a number or a number in brackets/parentheses. Identify if these numbers correspond to footnotes by checking for a statement preceded by the same number.
# 3. For 'ibid' and similar terms, repeat the last citation in <h2> and <h3>, updating the blockquote with the new statement. Maintain an internal index for footnotes to track references.
# 4. For parenthetical citations (e.g., (Author, Year)), extract the entire sentence containing the citation, highlight the citation in <strong> tags, and set <h3> to N/A.
# 5. Format the output in HTML:
#    - Use <h2> for cited authors and year.
#    - Use <blockquote> for complete sentences with highlighted citations.
#    - Use <h3> for full footnote information or complete bibliographic references.
# 6. Ensure 100% accuracy by extracting exact sentences with their citation references and details, ensuring they are complete and unbroken.
# 7. Handle multiple citations in a sentence by highlighting each citation individually.
# 8. If no citation is found, return "<div>N/A</div>".
# 9. Output as a single HTML code block.
#  """

# result = process_pdf(pdf_path, prompt,page_parsing=1)
# # result = chat_response(pdf_path=pdf_path, query=prompt)
#
# zt.create_one_note(content=result,item_id="76DQPE49",api="",tag="chat.citation")
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
zt.statements_citations("Law and evidence",update=True,chat=True)

# zt.create_one_note(item_id="7CJPMXT8",tag="testinho",content="content content content",api="")
# print(zt.update_all(
#     "lawful evidence",
#     tag="statements",
#     # "cyber due diligence",
#                     update=True
#               article_title="transparent attributions of cybera attacks to states?",
#               specific_section="<h2>2.1 Main Topics</h2>"

             # ))
# zt.evaluate("marking",tag_prompt,update=True)
# zt.rename_files_in_directory(r"C:\Users\luano\Downloads\17841037","-")
# zt.process_files_in_directory(r"C:\Users\luano\Downloads\17841037","marking")

# zt.process_collections_file("saved")
# data =zt.get_children_notes("BSRRQ7HD")
# data =zt.update_quotes("BSRRQ7HD",pdf=r"C:\Users\luano\Zotero\storage\LHZRBA2H\Johnson and Schmitt - 2021 - Responding to proxy cyber operations under international law.pdf",author="(Schmit,2015)",stop_words="")

# data =zt.get_or_update_collection("Law and evidence",False)
# data1 =[ (t,i) for t,i in data[("items")]["papers"].items()][3:5]
# print(data["items"]["papers"]['Evidentiary issues in international disputes related to state responsibility for cyber operations']["reference"])
# author = zt.get_html_info(note_content)

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
# zt.merging_notes("Law and evidence", update=False, section="<h1>3. Summary</h1>",filter_words=None, function="")

# content = zt.get_content_after_heading("4UGZNIHB", "<h1>3. Summary</h1>", "h3")
# print(content)
# content = zt.get_children_notes("3HQI2D4A")
# print(content)