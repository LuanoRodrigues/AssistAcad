import time

from tqdm import tqdm

from Zotero_module.zotero_data import note_api,summary
from bs4 import BeautifulSoup

from Zotero_module.zotero_data import sections_prompt,note_update,tag_prompt
from Zotero_module.zotero_class import  Zotero
from Pychat_module.Pychat import  ChatGPT
from dotenv import load_dotenv
load_dotenv()  # loads the variables from .env
import os
from Pychat_module.gpt_api import process_pdf,process_document_sections
# Accessing environment variables
library_id = os.environ.get("LIBRARY_ID")
api_key = os.environ.get("API_KEY")
library_type = os.environ.get("LIBRARY_TYPE")
token = os.environ.get("TOKEN")
# chat_name= "summary"
chat_name= "o"



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
    sleep=60#4*71





)
# zt.creating_training_data_from_statements("Law and evidence",False)
prompt ="""Generate 3 questions in three dicts whose answers will be the text,system content. the output is jsonl format:{"messages":[{"role":"system","content":"You are an expert in responding questions from  academic papers statements, ensuring the output is formatted in HTML and includes in-text citations."},{"role":"user","content":[generate the question here about the following content assitant ]},{"role":"assistant","content":"While it is likely that international judicial forums will not relax standards of proof to accommodate the obvious cyber-challenges, circumstantial evidence is available as a potentially viable route to prove a violation. Since state to state disputes have been more commonly addressed in the International Court of Justice (‘‘ICJ / Court’’)” (Aravindakshan, 2021, p. 286)"}]}
 note1:the questions should not contain authors name. The questions should be academic about the academic topic. note2: output jsonl format in one line for every question in a codeblock"""
# zt.multilple_prompts(prompt=prompt)
# zt.extract_insert_article_schema(note_id="7WI5RJFA",save=True)
# zt.update_all("Law and evidence",update=True)
# zt.statements_citations(collection_name="Law and evidence",batch=False,update=True  ,store_only=False,chat=True,section=tag_prompt[0],follow_up=True)

# zt.statements_citations(collection_name="nova",batch=False,update=True,store_only=False,chat=False,sections=note_api,)
# print(zt.get_children_notes("76DQPE49"))


# prompt = "Please analyze this document and extract all key arguments, main ideas, and entire paragraphs with the author's original points in HTML format. Ensure 100% accuracy by extracting exact paragraphs without modification or paraphrasing. Focus on paragraphs representing the author's core arguments and ideas. Use <h2> for key ideas (3-4 words) and <blockquote> for exact paragraphs with references (author, year, page). Exclude paragraphs with cited statements (superscript numbers, in-text citations)."
# a = ['Limitations of public attribution and the need for legal attribution', 'Standards of proof in international law', 'Circumstantial evidence in context', 'The Corfu Channel rule: when circumstantial evidence was ‘‘Good Enough’’', 'The Bosnian Genocide case: when circumstantial evidence was not ‘‘Good Enough’’', 'Other international legal Jurisprudence', 'Cyberspace attribution: current status in brief', 'Circumstantial evidence in context', 'Conclusion']
# result = process_document_sections(file_path=r"C:\Users\luano\Zotero\storage\NREIF9TL\(Sharngan Aravindakshan, 2021).pdf",sections=a)
# zt.create_one_note(content=result,item_id="76DQPE49",api="",tag="pdf")


# result = process_pdf(r"C:\Users\luano\Downloads\DOROTHÉE VANDAMME_10.pdf", prompt,page_parsing=1,reference="(dorethe, 2018)")
# result = chat_response(pdf_path=pdf_path, query=prompt)
#
# zt.create_one_note(content=result,item_id="76DQPE49",api="",tag="citation")

# content = zt.get_content_after_heading("4UGZNIHB", "<h1>3. Summary</h1>", "h3")

from  Zotero_module.zotero_class import generate_zotero_annotation,extract_citations_grobid, get_last_four_tokens,find_phrase_in_pdf,replace_substring_and_check,parse_grobid_xml_to_dict
citation_styles=[

{"objective": "To demonstrate a variety of numerical citation styles across different academic disciplines", "examples": [{"ref": "¹", "preceding_text": "Smith provides a comprehensive analysis of economic theories.", "footnote": "1. John Smith, *Economic Theories of the 21st Century* (New York: Academic Press, 2018), 56."}, {"ref": "[1]", "preceding_text": "Kumar's research highlights the application of AI in healthcare.", "footnote": "[1] A. Kumar, 'Artificial Intelligence in Healthcare,' in *Proceedings of the IEEE Conference on AI*, San Francisco, CA, 2021, pp. 45-50."}, {"ref": "1", "preceding_text": "Global warming trends have been thoroughly analyzed in recent studies.", "footnote": "Smith J, Doe J. A Comprehensive Study on Global Warming. *Environmental Journal*. 2020;45(4):120-134."}, {"ref": "³", "preceding_text": "Cystatin C is a non-glycosylated protein produced by all nucleated cells¹.", "footnote": "3. Griffin BR, Faubel S, Edelstein CL. Biomarkers of drug-induced kidney toxicity. Ther Drug Monit 2019;41:213-26."}]}
,
{
  "objective": "To use 'author, year' format for streamlined referencing in academic writing",
  "examples": [
    {
      "ref": "(Smith, 2020)",
      "preceding_text": "According to Smith's findings on climate change",
      "footnote": ""
    },
    {
      "ref": "(Jones, 1998, p. 199)",
      "preceding_text": "She stated, 'Students often had difficulty using APA style'",
      "footnote": ""
    },
    {
      "ref": "(Smith & Miller, 1966)",
      "preceding_text": "The study by Smith and Miller (1966) demonstrates this phenomenon",
      "footnote": ""
    },
    {
      "ref": "(Lynch et al., 1999)",
      "preceding_text": "Mutational studies of various species show consistent results",
      "footnote": ""
    },
    {
      "ref": "(Osam, 1997)",
      "preceding_text": "Osam (1997) discusses the grammatical relations in Akan",
      "footnote": ""
    },
    {
      "ref": "(Coie et al., as cited in Weist, 2001)",
      "preceding_text": "According to Coie et al. (as cited in Weist, 2001), racial injustice is a significant factor",
      "footnote": ""
    }
  ]
}

,
{
  "objective": "To make comments",
  "examples": [
    {
      "ref": "1",
      "preceding_text": "As discussed in earlier sections",
      "footnote": "For a more detailed discussion, refer to the analysis in Chapter 3."
    },
    {
      "ref": "2",
      "preceding_text": "This conclusion aligns with the theory proposed by Smith",
      "footnote": "However, Smith's theory has been subject to criticism, particularly in Johnson (2018), p. 202."
    },
    {
      "ref": "³",
      "preceding_text": "The results support the hypothesis that",
      "footnote": "3. These results are consistent with findings from other studies mentioned earlier. See also note 4 below."
    },
    {
      "ref": "4",
      "preceding_text": "Further research is needed to confirm these outcomes",
      "footnote": "Subsequent studies should focus on the variables outlined in the appendix."
    },
    {
      "ref": "5",
      "preceding_text": "The model's limitations are recognized",
      "footnote": "The current model does not account for all possible variables as suggested by recent publications. Future revisions could address this gap."
    },
    {
      "ref": "6",
      "preceding_text": "It is important to consider alternative interpretations",
      "footnote": "Alternative interpretations have been suggested in the literature, particularly in Davis (2020), p. 45."
    },
    {
      "ref": "7",
      "preceding_text": "The data presented here is preliminary",
      "footnote": "Further analysis is required to validate these findings. See additional data in the supplementary materials."
    },
    {
      "ref": "8",
      "preceding_text": "The theoretical framework used is well-established",
      "footnote": "This framework has been widely accepted, but its application in this context is still debated. See note 5 above for more details."
    }
  ]
}
,
{
  "objective": "To provide examples of diverse block quotes presented in the text using varied citation styles, with numerical and superscript citations using footnotes including bibliographic information, and others not",
  "examples": [
    {
      "ref": "(1)",
      "preceding_text": "In discussing the impact of industrialization on modern cities, Davis provides a compelling overview: 'The rapid expansion of industrial activities fundamentally altered the urban landscape, bringing with it not only economic growth but also significant social challenges. The rise of factories and mass production systems led to unprecedented population growth in cities, often outpacing the development of necessary infrastructure.'",
      "footnote": "Davis, J. (2005). *The Transformation of Urban Spaces: Industrialization and Social Change*. New York: Urban Studies Press, p. 123."
    },
    {
      "ref": "[2]",
      "preceding_text": "As noted by Smith, the shift in educational paradigms has profound implications: 'Traditional education models focused heavily on rote learning and memorization. However, the current shift towards critical thinking and problem-solving skills represents a significant departure from these methods, suggesting a future where students are more engaged and better prepared for complex challenges.'",
      "footnote": "Smith, A. (2018). *Educational Paradigms: From Rote Learning to Critical Thinking*. Boston: Academic Press, p. 67."
    },
    {
      "ref": "(3)",
      "preceding_text": "Johnson offers a critical perspective on environmental policy, stating: 'Without a strong foundation in empirical data, environmental policies risk being driven by short-term political agendas rather than long-term sustainability goals. This disconnect between science and policy can lead to ineffective or even harmful outcomes.'",
      "footnote": "Johnson, L. (2019). *Environmental Policy and Scientific Integrity*. London: Green Earth Publications, p. 45."
    },
    {
      "ref": "(Miller, 2017, p. 88)",
      "preceding_text": "In his analysis of global economic trends, Miller presents the following observation: 'The globalization of markets has created both opportunities and challenges. While access to international markets has allowed for unprecedented economic growth, it has also exposed vulnerabilities, particularly in developing economies that struggle to compete on a global scale.'",
      "footnote": ""
    },
    {
      "ref": "(2)",
      "preceding_text": "Brown discusses the complexities of cultural identity in his recent work: 'Cultural identity is not a fixed concept; it evolves over time and is influenced by a variety of factors, including migration, globalization, and personal experiences. Understanding this fluidity is crucial for addressing issues related to multiculturalism and social cohesion.'",
      "footnote": "Brown, P. (2019). *Cultural Identity in a Globalized World*. Cambridge: Cambridge University Press, p. 102."
    },
    {
      "ref": "[5]",
      "preceding_text": "Chomsky's critique of modern media practices remains relevant today: 'The media, far from being a neutral conduit of information, actively shapes public perception by framing issues in ways that align with the interests of the elite. This manipulation of public discourse serves to maintain the status quo and marginalize dissenting voices.'",
      "footnote": "Chomsky, N. (1997). *Media Control: The Spectacular Achievements of Propaganda*. New York: Seven Stories Press, p. 34."
    },
    {
      "ref": "(Garcia, 2020, pp. 55-56)",
      "preceding_text": "In her study on the psychology of consumer behavior, Garcia highlights: 'Consumer decisions are rarely based on rational calculations alone. Emotional and psychological factors play a significant role in shaping purchasing behavior, often leading to decisions that contradict logical reasoning.'",
      "footnote": ""
    },
    {
      "ref": "⁷",
      "preceding_text": "In his analysis of linguistic patterns, Thompson argues: 'Language is not just a medium of communication; it is a tool of power, shaping perceptions and controlling discourse. Those who control language control the narrative, and by extension, the collective understanding of reality.'",
      "footnote": "Thompson, G. (2021). *Language and Power: The Linguistic Tools of Domination*. Oxford: Oxford University Press, p. 76."
    }
  ]
},
{
  "objective": "To provide examples of direct quotations embedded in the text using varied citation styles, with numerical and superscript citations including full bibliographic information",
  "examples": [
    {
      "ref": "(1)",
      "preceding_text": "Davis offers a critical view on the social impacts of industrialization, stating, 'The rapid expansion of industrial activities fundamentally altered the urban landscape, bringing with it not only economic growth but also significant social challenges.'",
      "footnote": "Davis, J. (2005). *The Transformation of Urban Spaces: Industrialization and Social Change*. New York: Urban Studies Press, p. 123."
    },
    {
      "ref": "[2]",
      "preceding_text": "Smith emphasizes the importance of modern educational approaches, noting, 'The shift towards critical thinking and problem-solving skills represents a significant departure from traditional rote learning methods, suggesting a future where students are more engaged and better prepared for complex challenges.'",
      "footnote": "Smith, A. (2018). *Educational Paradigms: From Rote Learning to Critical Thinking*. Boston: Academic Press, p. 67."
    },
    {
      "ref": "(Miller, 2017, p. 88)",
      "preceding_text": "Miller discusses the dual nature of global economic trends, arguing, 'While access to international markets has allowed for unprecedented economic growth, it has also exposed vulnerabilities, particularly in developing economies that struggle to compete on a global scale.'",
      "footnote": ""
    },
    {
      "ref": "(3)",
      "preceding_text": "Johnson critiques the current state of environmental policy, asserting, 'Without a strong foundation in empirical data, environmental policies risk being driven by short-term political agendas rather than long-term sustainability goals.'",
      "footnote": "Johnson, L. (2019). *Environmental Policy and Scientific Integrity*. London: Green Earth Publications, p. 45."
    },
    {
      "ref": "[5]",
      "preceding_text": "Chomsky remains a vocal critic of media practices, stating, 'The media, far from being a neutral conduit of information, actively shapes public perception by framing issues in ways that align with the interests of the elite.'",
      "footnote": "Chomsky, N. (1997). *Media Control: The Spectacular Achievements of Propaganda*. New York: Seven Stories Press, p. 34."
    },
    {
      "ref": "(Garcia, 2020, pp. 55-56)",
      "preceding_text": "Garcia highlights the psychological influences on consumer behavior, noting, 'Consumer decisions are rarely based on rational calculations alone. Emotional and psychological factors play a significant role in shaping purchasing behavior, often leading to decisions that contradict logical reasoning.'",
      "footnote": ""
    },
    {
      "ref": "⁷",
      "preceding_text": "Thompson discusses the relationship between language and power, stating, 'Language is not just a medium of communication; it is a tool of power, shaping perceptions and controlling discourse.'",
      "footnote": "Thompson, G. (2021). *Language and Power: The Linguistic Tools of Domination*. Oxford: Oxford University Press, p. 76."
    }
  ]
}


]

pdf =r"C:\Users\luano\Zotero\storage\AZN6P3JU\(T Rid, B Buchanan, 2015).pdf"
# extract_citations_grobid(pdf_path=pdf,file_name="attributing.xml")
# update_quote(note_id="VWPNFE2J",pdf=pdf,zot=zt.zot,xml_path=xml)
zt.creating_training_data_gpt("training_gpt_style.jsonl",data_list=citation_styles)

