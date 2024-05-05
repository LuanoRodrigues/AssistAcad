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
    "<h2>1.1 Research Framework</h2>": f"Guidelines:\nTo analyze the attached PDF document, focus on extracting and understanding its core research elements, including the types of research conducted, the study's objectives, the central research problem, core research questions, and the corresponding hypotheses. Each element should be identified and discussed in relation to the content of the document. Provide explanations for the selected research type(s) directly in your analysis, along with citations that exemplify or can be interpreted as representing these research types. Similarly, outline the research problem directly before delving into the research questions and hypotheses, ensuring each is supported by direct references from the text. Here is how to structure your findings in an HTML format: <h3>Study Objectives</h3>  <li>[Specific objective of the study]</li> <li>[Another specific objective of the study]</li> <!-- Add more objectives as necessary -->  <h3>Research Problem</h3> <li>[The main problem the research aims to solve or the 'problematique' of the research]</li> <h3>Research Questions</h3> <h4>[Question 1]: [Specific research question]</h4> <blockquote>'[Direct citation from the text supporting this question.]'</blockquote> <h3>Hypotheses</h3> <h4>[Hypothesis 1]: [Specific hypothesis related to Question 1]</h4> <blockquote>'[Direct citation from the text supporting this hypothesis.]'</blockquote><h4>[Assumption 1]: [Specific assumption related to Question 1]</h4> <blockquote>'[Direct citation from the text supporting this assumption.]'</blockquote> <!-- Repeat the pattern for additional questions, hypotheses and assumptions -->   This format ensures a detailed and structured analysis, clearly presenting the study's foundational elements with direct references from the document.{note}",
    "<h2>1.2 Key Terms Definitions</h2>": f"Please analyze the PDF document to extract key terms and their definitions by focusing on specified linguistic, formatting, and citation cues. Use the following approach: 1. **Definition Phrases**: Search for sentences containing any of these indicators: - 'can be defined by' - 'it refers to' - 'is described as' - 'is known as' - 'means' - 'is defined as' - 'constitutes' - 'implies' - 'encompasses' - 'this means' - 'in other words' - 'this involves' - 'signifies' - 'represents' - 'entails' 2. **List and Structural Patterns**: Identify list or structured formats where definitions might be presented. 3. **Typographic Cues**: Detect key terms emphasized through typography like italics or bold. 4. **Contextual Keywords**: Look for paragraphs with keywords like 'definition', 'terminology', 'concept', 'explanation', 'illustration'. 5. **Citation Patterns**: Note sentences where terms are directly followed by citations, common in academic texts. For each key term and definition found: - Use `<h3>` tags for the key term. - Use `<blockquote>` tags for quoting the definition exactly as it appears, including the exact citation format. **Example of output format**: ```html <h3>[Key Term]</h3> <blockquote> [Direct definition by the author exactly as found, including citations] </blockquote> ``` This format should be strictly respected and used for each definition found.{note}",
    "<h2>1.3 Key Findings</h2>": f"Guidelines:\nDive into the attached PDF document to thoroughly identify its key findings. Concentrate on presenting a detailed analysis of these findings, outlining the main conclusions drawn by the authors within the study. For each finding, provide a clear explanation that encapsulates the essence of the discovery or conclusion, and include multiple direct quotes from the document that illustrate or support these findings. ### Example HTML Structure for Presentation of Findings: ```html  <h3>[Finding Statement]</h3><p>[Provide a short explanation that fully develops the author's finding, focusing exclusively on the content and conclusions within the study.]</p> <blockquote>'[Direct quote from the document illustrating the finding.]' (Author, Year, p. XX)</blockquote> <blockquote>'[Another direct quote related to the same finding.]' (Author, Year, p. XX)</blockquote> <!-- Repeat for each key finding identified -->   ``` {note}",
    "<h2>1.4 Shortcomings Limitations</h2>": f"Guidelines:\nPerform an in-depth examination of the attached PDF document to identify and elucidate its shortcomings and limitations. Your analysis should scrutinize the document thoroughly, extracting specific instances where the paper acknowledges its own limitations or where you perceive potential weaknesses. Each identified shortcoming should be clearly explained and substantiated with multiple direct quotes from the document. ### Example HTML Structure for Presentation of Shortcomings and Limitations: ```html  <h3>[Shortcoming 1 title]</h3><p>[Explanation of the shortcoming]</p> <blockquote>“[Direct quote from the document illustrating the shortcoming.]” (Author, Year, p. XX)</blockquote> <blockquote>“[Another direct quote related to the same shortcoming.]” (Author, Year, p. XX)</blockquote> <h3>Shortcoming 2:</h3><p>[Explanation of the second shortcoming]</p> <blockquote>“[Direct quote illustrating the second shortcoming.]” (Author, Year, p. XX)</blockquote> <blockquote>“[Additional quote related to the second shortcoming.]” (Author, Year, p. XX)</blockquote> <!-- Continue with additional shortcomings as identified -->  ``` This structured approach ensures a thorough presentation of the document's acknowledged limitations and perceived shortcomings, each supported by direct quotes for a nuanced understanding and critical analysis.{note}",
    "<h2>1.5 Research Gap and Future Research Directions</h2>": f"Guidelines:\nAnalyze the attached PDF document to extract and articulate the research gaps identified by the author(s) and the suggested future research directions. This analysis should cover the areas the study has not explored or fully addressed, highlighting opportunities for further investigation. Each identified research gap and proposed direction for future research should be clearly explained and, where possible, supported by direct quotes from the document. ### Example HTML Structure for Presentation of Research Gap and Future Research Directions: ```html  <h3>Research Gap </h3><h4>[Research Gap title]</h4> <p>[Detailed explanation of the found research gap identified in the document.]</p> <blockquote>“[Direct quote from the document highlighting this gap.]” (Author, Year, page number)</blockquote><--repeat that structure of h4 and blockcode until three research gaps are found along with direct citation if found--> <h3>Future Research Direction</h3><h4>[Future Research Direction title]</h4><p>[short Explanation of the suggested direction for future research ]</p> <li> [ research question related to the  gap- repeat this list if other important questions are found ]<--repeat that structure of h4 and blockcode with future directions for every gap found-->  ``` This format ensures a comprehensive presentation of the identified research gaps and future research directions, supported by direct citations from the document for clarity and accuracy in understanding the areas needing further exploration.{note}",
    "<h2>2.1 Main Topics</h2>": f"Guidelines:\nTo systematically analyze the attached PDF document, identify and elaborate on the top 5 main topics covered, incorporating explanations, their significance, and providing multiple direct citations related to each topic. Structure your findings in an HTML format for clarity and comprehensive presentation. ### Example HTML Structure for Main Topics Analysis: ```html   <h3>[Topic title]:</h3> <p>[explanation of the topic found in the paper]</p> <blockquote>[direct citation supporting the existence of the topic]</blockquote> <--repeat that for the top five topics found in the paper with the same structure h3 with topic title, short paragraph with explanation and the direct citation stricly extracted from the paper.{note}",
    "<h2>2.2 Author References</h2>": [
        f"Guidelines: Read the PDF carefully, paragraph by paragraph, to identify the top ten in-text citations linked to footnotes that are most critical in supporting the main themes, arguments, and claims of the paper. For each citation: 1. Identify the citation format (e.g., superscript, bracketed number, inline text). 2. Match each citation to its corresponding footnote that starts with the same number and includes detailed bibliographic information. 3. Ensure each pair of citation and footnote is unique, directly linked to the sentence preceding the citation in the text, and accurately represents the source material. 4. In the output, structure each entry as follows in HTML: <h4>Author (year)</h4> <h5>[Footnote number + full footnote text including the starting number]</h5> <blockquote> <cite>[Exact sentence from the body text that precedes the footnote number, including the footnote number]</cite> </blockquote> <--Ensure each author is listed once with all associated references consolidated under their name if multiple references are present in a single footnote. Repeat for the top 10 authors in the document. your first response will contain 5 and next prompt I will ask for the remaining 5.-->{note}",
        "Proceed with the next 5 authors.",
        f"now Scan the PDF carefully, paragraph by paragraph, to identify the top 10 direct in-text citations relevant to the paper content. opposed to the previous prompt that checked footnotes, Focus specifically on intext citations that include author names in formats like '(author, year)', or are introduced by phrases such as 'according to', 'as noted by', or verbs like 'proposes', 'advocates'. <div><h4>author name (year)</h4><blockquote><cite>[Exact sentence from the PDF where the author is mentioned, maintaining the original citation format]</cite></blockquote></div> Repeat for the top 10 authors in the document. your first response will contain 5 and next prompt I will ask for the remaining 5.{note}",
        "now,continue with the next 5 authors please enclosed in one single div in block code."],
    "<h2>2.3 Entity Reference</h2>": [
        f"now Scan the PDF document paragraph by paragraph, extracting in-text citations that specifically mention entities such as the organisations, companies etc. Document each citation in HTML format as follows: <div><h4>Entity Name</h4><blockquote><cite>[Exact sentence from the PDF where the entity is mentioned, including any inline reference numbers]</cite></blockquote></div> Ensure the final output accurately reflects the context in which the entity is discussed in the text. Repeat for the top 10 entities in the document. your first response will contain 5 and next prompt I will ask for the remaining 5.{note} ",
        f"now, the next 5 entities please enclosed in one single div in block code. "],
    "<h2>2.4 Structure and Keywords</h2>": f"Guidelines:\n Please perform a thorough analysis based on the following guidelines and format the output as detailed in the provided div structure: 1. **Article Schema:** Outline the article's structure with main headings and subheadings. Aim to provide a comprehensive table of contents. 2. **Keyword Extraction:** Identify and list academic keywords or phrases crucial for systematic review coding. Concentrate on extracting terms reflecting the core themes and methodologies. Limit phrases to three words where possible. 3. **Detailed Analysis:** Break down your analysis into specific categories: - **Academic Fields and Research Areas:** Identify the 3 primary disciplines or fields. - **Themes and Topics:** Extract 7 detailed themes or topics[they should not exceed 4 words]. - **Methodologies Keywords:** Highlight keywords for coding, focusing on methods like 'qualitative analysis', 'quantitative analysis', 'mixed-methods analysis'; epistemologies like 'positivism', 'interpretivism', 'critical realism'; and theories like 'realism', 'liberalism', 'constructivism'. - **Countries and Regions:** Note 6 significant  countries specifing where they were found with context . - **Affiliations** Note 1 significant affiliations . Example structure: ```html <h3>Article Schema:</h3><ul><li>Abstract</li><li>Section 1: Title</li><li>Section 2: Title</li></ul><h4>Academic Fields and Research Areas:</h4><ul><li>Field 1</li><li>Field 2</li><li>Field 3</li></ul><h4>Themes and Topics:</h4><ul><li>Theme 1</li><li>Theme 2</li><!-- More themes as needed --></ul><h4>Methodologies Keywords:</h4><ul><li>Qualitative Analysis</li><li>Positivism</li><li>Realism</li><!-- More methodologies as needed --></ul><h4>Countries, and Regions:</h4><ul><li>Region 1 title (the short context where is was found)</li><li>Country 1(the short context where is was found)</li><!-- More regions and countries as needed --></ul><h4>Affiliations:</h4><ul><li>Affiliation 1 (affiliation information)</li><ul> ``` Ensure your analysis fills in the placeholders based on the document's content.{note}",
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








