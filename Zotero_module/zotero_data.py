
# note= "\nNote:\n Focus on direct information from the article but if indirect evidence is found, provide an interpretation based on the above instructions and the paper content. if no relevant information is found, return a None div. output:HTML div in a code block"
note= "Take your time, review the final output for accuracy and consistency in HTML formatting and citation-context alignment.\n\nnote1:Direct quotes format must be in form of one full sentence. The full sentence must be exactly as it is in the document, strictly unmodified. before getting it, check if there is a full match in the sentence and the word text. After getting the exacly quote that supports you analysis, reference with the author name between () like (author)\nnote:2output format:html in a code block."
note_assign= "Take your time, review the final output for accuracy and consistency in HTML formatting and citation-context alignment.\n \nnote1: output format:html in one single code block.\nnote2:Act like a Professor talking to the student, then use the second person(You demonstrate) instead of third(the student demonstrates). "
summary_note = "\nnote:1 do not write additional information, all the information must be found and referenced in the document, if no reference is found, skip the task and go to the next.\nnote 2: follow the citation apa format:author,year,page. author and year was already provided, you should identify the page.\nnote3:output format: code block html```"
summary=[{"summary":
    [f"Guidelines: Read the text in full, write paragraphs about the following: 1. Key Terms and Definitions, 2. Research types and objectives, 3. Central research problem, 4. Core research questions, 5. Hypotheses, 6. Key findings.\nImportant Notes: - every paragraph should be referenced with direct citations from the document or paraphrased and referenced. - Everything should be supported by your reading. If no information is found, do not make it up, skip and write the next paragraph. - Do not write unsupported statements. - The text should be academic, concise, objective, coherent, and cohesive, using linking/transitioning words. - Include real citations from the document, specifying the author, year, and page number. Example HTML Structure output: ```html <div><h2>Summary</h2> <h3>Key Terms and Definitions</h3><p>[search for all useful definitions in the text if any or skip it]</p> <h3>Research Type and Objectives</h3> <p>[explain the paper's research type and its objectives]</p> <h3>Research Problem</h3><p>[explain the paper's research problem, what is the object of the research, and why it is relevant]</p> <h3>Central Research Questions</h3> <p>[go through some central research questions of the author and how they interact with the research problem]</p><h3>Hypothesis</h3> <p>[explain how the hypothesis of the author interacts with the research question and the problem, meaning what the author proposes to address the research problem and respond to the research questions]</p><h3>Findings</h3> <p>[cite and explain the main findings found in the paper related to the research problem and the subject, including direct citations with author, year, and page number]</p> </div>``` {summary_note}",
    f"Guidelines: Read the text to find: 1. Shortcomings and Limitations: Summarize the document's shortcomings and limitations with direct quotes. 2. Research Gaps and Future Research Directions: Identify research gaps and future research directions with quotes. 3. Implications and Policy Recommendations: Summarize practical implications, and policy recommendations. If none, skip this section. Important Notes: Support everything with references. Provide at least two examples with references for each subject. Do not make unsupported statements. Be concise, objective, coherent, and cohesive. Use real citations specifying author, year, and page number. Example HTML Structure output: ```html <div><h3>Shortcomings</h3><p>[explain two shortcomings found in the text, supported by quotes. write them in a single paragraph, this one]</p><h3>Research gaps</h3><p>[identify and explain two research gaps, supported by quotes in this same paragraph]</p><p><h3>Implications and Policy Recommendations</h3>[summarize practical implications and/or theoretical contributions, and/or policy recommendations if none,skip it]</p><h3>Future Research Directions</h3><li>[propose two research questions for future research ]</li></div>```{summary_note}",
    f"Guidelines:\nRead the text in full, searching for the following information:\n1. Data Collection Techniques: Identify and explain the data collection techniques used in the study. Discuss the sampling techniques, data collection instruments, and measurement tools. Provide at least two examples with references.\n2. Data Analysis: Identify and explain the data analysis methods used in the study. Discuss quantitative, qualitative, and mixed-methods analysis as applicable. Provide at least two examples with references.\n3. Theoretical Frameworks or Models: Identify and articulate the theoretical frameworks and models that underlie the research. Provide explanations based on the document's content, supplemented by direct quotes as evidence of these theoretical/model orientations. Provide at least two examples with references.\n\n**Important Notes:**\n- Paragraphs should be mostly referenced with direct citations from the document or paraphrased and referenced.\n- Everything should be supported by your reading.\n- For every subject discussed, provide at least two examples with references. If no information is found, do not make it up.\n- Do not write unsupported statements.\n- If no clear data, analysis, or theoretical frameworks are found, skip it. If none of the three are found, return an empty div.\n- The text should be academic, concise, objective, coherent, and cohesive, using linking/transitioning words.\n- Include real citations from the document, specifying the author, year, and page number where the information can be found.\n\n**Example HTML Structure for the Summary:**\n```html\n<div>\n   <h3>Data Collection</h3><p>[explain one data collection technique used in the study, supported by direct quotes if any,If none, skip it]</p>\n  <h3>Data Analysis Methods</h3> <p>[identify and explain one data analysis method used in the study, supported by direct quotes if any, If none, skip it]</p>\n  <h3>Theoretical Frameworks or Models</h3><p>[explain theoretical frameworks or models used in the study, supported by direct quotes. If none, skip it]</p>\n  </div>```{summary_note}",
    f"Guidelines: Analyze the text to identify note and numerical citations. This includes statements followed by a number or a number in brackets/parentheses (e.g., 'international relations theories such as realism and neoliberalism are mainstream¹' or 'international relations theories such as realism and neoliberalism are mainstream (1)'). Check if the same number corresponds to a statement preceded by the same number (e.g., '1. John S Davis II and others, ‘Stateless Attribution: Toward International Accountability in Cyberspace’ (RAND Corporation 2017) 21.'). If a sentence is preceded by a number and this number is found following a sentence, it means this is an in-text citation and a corresponding footnote. Identify APA citation style too like (author, year) and its variations. The pattern is statement+ (author,year) or any mention to an author. Focus in getting the following:\n. 1. Authors: Reference_processing with footnote or in (author, year) citation style, focusing exclusively on authors (not companies or entities). 2. Entities: Reference_processing in various formats, focusing exclusively on entities such as organizations and governmental bodies. 3. Legal Cases: Any reference to a legal case. After identifying the main citation in each case - author, entities, and legal cases - write a paragraph for each listing the main ones and their context, explaining how it was used by the author. Always include references with author, year, and page number. Example HTML Structure Structure output: ```html <div><h3>Authors</h3><p>[list the main authors references and their context]</p><h3>Entities</h3><p>[list the main entities references and their context]</p><h3>Legal cases</h3><p>[list the main legal cases references and their context]</p></div>```{summary_note}"]
}
]

note_summary_schema="""
<h1>1. Introduction:</h1>
<h2>1.1 Research Framework</h2>
<hr>
<h2>1.2 Key Findings</h2>
<hr>
<h2>1.3 Shortcomings Limitations</h2>
<hr>
<h2>1.4 Research Gap and Future Research Directions</h2>
<hr>
<hr>
<h2>1.5 Structure and Keywords</h2>
<hr>
<hr>
<h2>Loose notes</h2>
<hr>
              """

prompts = {
   "name": "thematic_review",
  "strict": True,
  "schema": {
    "type": "object",
    "properties": {
      "heading": {
        "type": "string",
        "enum": ["h1", "h2", "h3", "h4", "h5", "h6"],
        "description": "The valid HTML heading level (e.g., 'h1', 'h2', etc.) representing the section's hierarchy."
      },
      "title": {
        "type": "string",
        "description": "The title of the heading that summarizes the content of the section."
      },
      "paragraphs": {
        "type": "array",
        "items": {
          "type": "string",
          "description": "A cohesive paragraph of text written based on the provided references. Each paragraph should critically analyze the content and contribute to a coherent narrative that connects with the overarching theme. Maximum tokens: 500 for sections, 300 for subsections."
        }
      }
    },
    "required": ["heading", "title", "paragraphs"],
    "additionalProperties": False
  },
  "config": {
    "model": "gpt-4",
    "temperature": 0.3,
    "max_tokens": {
      "h1": 500,
      "h2": 500,
      "h3": 300,
      "h4": 300
    },
    "stop": ["###"],
    "top_p": 0.9
  },
  "instructions": {
    "style": {
      "transitions": "Ensure smooth transitions between paragraphs to maintain thematic unity.",
      "structure": "Use valid HTML headings (h1-h6) to reflect document hierarchy and maintain logical progression."
    }
  }



,

  "get_headings": {
    "text": "I have clustered topic sentences representing paragraphs. Your task is to give them a cohesive and coherent structure by assigning headings in HTML tags (h1, h2, h3, h4) nested where appropriate. The structure should be in the format: <h1> title </h1>, <h1> paragraph IDs </h1>, <h2> title </h2>, <h2> paragraph IDs </h2>, etc. You will receive a list of dicts with 'id' and 'p' (paragraph content). Your output should be a list of headings with their corresponding titles and the paragraph IDs associated with them. For example: [{'h1': {'title': 'Main Heading Title', 'paragraph_ids': ['67bc2e0e', 'a4c3cde6']}}, {'h2': {'title': 'Subsection Title', 'paragraph_ids': ['8c497488']}}]. Add an overarching theme at the top before the <h1> heading that represents the entire structure.",
    "json_schema": {
      "name": "headings_and_titles_generator",
      "strict": True,
      "schema": {
        "type": "object",
        "properties": {
          "overarching_theme": {
            "type": "string",
            "description": "The overarching theme that summarizes the entire document, placed before the first <h1> heading."
          },
          "structure": {
            "type": "array",
            "items": {
              "type": "object",
              "properties": {
                "heading": {
                  "type": "string",
                  "enum": ["h1", "h2", "h3", "h4"],
                  "description": "The HTML heading level (e.g., h1, h2, h3, h4) representing the section's hierarchy."
                },
                "title": {
                  "type": "string",
                  "description": "A title summarizing the central idea of the section or subsection."
                },
                "paragraph_ids": {
                  "type": "array",
                  "items": {
                    "type": "string",
                    "description": "A list of paragraph IDs that are grouped under this heading."
                  },
                  "description": "The list of paragraph IDs associated with this heading."
                }
              },
              "required": ["heading", "title", "paragraph_ids"],
              "additionalProperties": False
            }
          }
        },
        "required": ["overarching_theme", "structure"],
        "additionalProperties": False
      }
    },
    "content": "You will read through clusters of paragraphs and return a structured list of HTML headings (h1 to h4) with their titles and associated paragraph IDs. Ensure proper nesting of headings (h1 > h2 > h3 > h4) according to the logical flow of the content. Each heading should summarize the central idea of the associated paragraphs. Add an overarching theme that describes the entire document before the first <h1> heading. For example: {'overarching_theme': 'Cybersecurity Challenges', 'structure': [{'h1': {'title': 'Main Heading Title', 'paragraph_ids': ['67bc2e0e', 'a4c3cde6']}}, {'h2': {'title': 'Subsection Title', 'paragraph_ids': ['8c497488']}}]}."
  },



    "footnote": {
        "text": "Your text goes here",
        "json_schema": {
            "name": "citation_extraction",
            "strict": True,
            "schema": {
                "type": "object",
                "properties": {
                    "references": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "ref": {"type": "string"},
                                "preceding_text": {"type": "string"},
                                "footnote": {"type": "string"}
                            },
                            "required": ["ref", "preceding_text", "footnote"],
                            "additionalProperties": False
                        }
                    }
                },
                "required": ["references"],
                "additionalProperties": False
            }
        },
        "role": {
            "system": {
                "content": "You are an academic reference extractor, responding in json object"
            }
        }
    },
    "find_title": {
        "text": "Read carefully the paragraphs considering the context of the overral context of the academic paper with {{title}} and {{section/subsections}}. After analysing each paragraph in its context, return a list of paragraph titles resuming the paragraph content in a declarative sentence affirming one fact central to the paragraph, that is one or two complete sentence about the central idea of the paragraph. Return a list of dicts, each with paragraph number and title."
,
        "json_schema": {
             "name": "title_creator",
    "strict": True,
    "schema": {
        "type": "object",
        "properties": {
            "titles": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "paragraph_number": {"type": "integer"},
                        "h3_title": {"type": "string"}
                    },
                    "required": ["paragraph_number", "h3_title"],
                    "additionalProperties": False
                }
            }
        },
        "required": ["titles"],
        "additionalProperties": False
    }
        },
        "content": "You read paragraphs and summarise them in a declarative short sentence"


    },


}

tag_note ="note1: start with the first section. I will ask you to output more statement while you advance in your search. If no more relevant statement found, return <div>N/A</div> note2: Statements should contain at least 150 words size, highlighting in bold, strong tag, the main statement.note3:output format: code block html```"
tag_prompt = [
    {
        "Statements Database":
            f"Please analyze this document thoroughly and extract all key arguments, main ideas, and citable statements in section {{section}}. Ensure 100% accuracy by extracting exact statements as found in the document, without any modification or paraphrasing. Focus on capturing statements that represent the author's core arguments, contributions, and ideas section by section. The output is: <div><h2>[Section title]</h2><h3>[first Key Argument/Idea/Contribution in less than 6 words]</h3> <p>[short context of the h3 title, explaining the argument/idea/contribution with objective and direct language]</p><blockquote>[other statements] <strong>[Main statement in bold linked to the <h3> title].</strong> [other statements] (author, year, page).</blockquote><h3>[ Second Key Argument/Idea/Contribution in less than 6 words]</h3><p>[short context of the h3 title, explaining the argument/idea/contribution with objective and direct language]</p><blockquote>[other statements] <strong>[Main statement in bold linked to the <h3> title].</strong> [other statements] (author, year, page).</blockquote></div> <--continue extracting all the main statements from this section, providing contribution title in h3, statement in bold with others around it in 150 words in blockquote and -->.{tag_note}"

    }
    ,
    {
        "Authors Cited":
           f"1. Analyze the text to identify note and numerical citations. This includes statements followed by a number or a number in brackets/parentheses (e.g., 'international relations theories such as realism and neoliberalism are mainstream¹' or 'international relations theories such as realism and neoliberalism are mainstream (1)'). 2. Check if the same number corresponds to a statement preceded by the same number (e.g., '1. John S Davis II and others, Stateless Attribution: Toward International Accountability in Cyberspace (RAND Corporation 2017) 21.'). If a sentence is preceded by a number and this number is found following a sentence, it means this is an in-text citation and a corresponding footnote. 3. Handle 'ibid' and similar terms: For 'ibid', repeat the last citation in <h2>, updating the <blockquote> with the new statement. Maintain an internal index for footnotes to track references. 4. When a statement is followed by a number, treat it as body text and include it in a <blockquote> with the number highlighted in <strong> tags and the rest of the sentence or other citations not highlighted. 5. When a statement is preceded by a number, treat it as a footnote and include it in an <h2> tag. 6. For each citation, extract the author and year from the footnote information and use it in the <h3> tag. If no author is found, set the value to 'None'. 7. Format the output in HTML: Use <h1> for the section title analyzed. Use <h2> for the footnote number or 'None' if author-year citation style is not used. Use <blockquote> for the full cited statement in bold, including other statements not in bold preceding and following the main statement. Use <h3> for the full footnote information if using author-year style, or 'None'. Use <h4> for the author's name and year of the cited statement, or 'None' if not available. 8. Ensure 100% accuracy by extracting exact sentences and corresponding footnotes. 9. If no citation is found, return a <div>N/A</div>.{tag_note}"
}]


note_update =\
    {
        "<h2>1.1 Research Framework</h2>": [f"Guidelines:\nTo analyze the attached word , focus on extracting and understanding its core research elements, including the types of research conducted, the study's objectives, the central research problem, core research questions, and the corresponding hypotheses. Each element should be identified and discussed in relation to the content of the document. Provide explanations for the selected research type(s) directly in your analysis, along with citations that exemplify or can be interpreted as representing these research types. Similarly, outline the research problem directly before delving into the research questions and hypotheses, ensuring each is supported by direct references from the text. Here is how to structure your findings in an HTML format: <h3>Study Objectives</h3>  <li>[Specific objective of the study]</li> <li>[Another specific objective of the study]</li> <!-- Add more objectives as necessary -->  <h3>Research Problem</h3> <li>[The main problem the research aims to solve or the 'problematique' of the research]</li> <h3>Research Questions</h3> <h4>Question 1: [Specific research question]</h4> <blockquote>'[Direct citation from the text supporting this question.]'</blockquote> <h3>Hypotheses</h3> <h4>Hypothesis 1: [Specific hypothesis related to the previous question]</h4> <blockquote>'[Direct citation from the text supporting this hypothesis.]'</blockquote><h4>Assumption 1: [Specific assumption related to the previous question]</h4> <blockquote>'[Direct citation from the text supporting this assumption.]'</blockquote>  This format ensures a detailed and structured analysis, clearly presenting the study's foundational elements with direct references from the document. split your response in two: one exactly as instructed and the next prompt I will ask you additional research question number 2 along with eveything after eg. assumption, hypothesis... So now provide the first response.{note}",  "now read the word again and provide the second response in the following format:<h4>Question 2: [Specific research question]</h4> <blockquote>'[Direct citation from the text supporting this question.]'</blockquote> <h3>Hypotheses</h3> <h4>Hypothesis 2: [Specific hypothesis related to the previous question]</h4> <blockquote>'[Direct citation from the text supporting this hypothesis.]'</blockquote><h4>Assumption 2: [Specific assumption related to the previous question]</h4> <blockquote>'[Direct citation from the text supporting this assumption.]'</blockquote><h3>Contribution</h3><h4>Contribution 1:[resume the contribution in one sentence]</h4><blockquote>'[Direct citation from the text supporting the contribution 1.]'</blockquote><h4>Contribution 2:[resume the contribution in one sentence]</h4><blockquote>'[Direct citation from the text supporting the contribution 2]'</blockquote>"],
        "<h2>1.2 Key Findings</h2>": f"Guidelines:\nDive into the attached word document to thoroughly identify its key findings. Concentrate on presenting a detailed analysis of these findings, outlining the main conclusions drawn by the authors within the study. For each finding, provide a clear explanation that encapsulates the essence of the discovery or conclusion, and include multiple direct quotes from the document that illustrate or support these findings. ### Example HTML Structure for Presentation of Findings: ```html  <h3>[Finding Statement]</h3><p>[Provide a short explanation that fully develops the author's finding, focusing exclusively on the content and conclusions within the study.]</p> <blockquote>'[Direct quote from the document illustrating the finding.]' (Author, Year, page number)</blockquote> <blockquote>'[Another direct quote related to the same finding.]' (Author, Year, page number)</blockquote> <!-- Repeat for each key finding identified -->   ``` {note}",
        "<h2>1.3 Shortcomings Limitations</h2>": f"Guidelines:\nPerform an in-depth examination of the attached word document to identify and elucidate its shortcomings and limitations. Your analysis should scrutinize the document thoroughly, extracting specific instances where the paper acknowledges its own limitations or where you perceive potential weaknesses. Each identified shortcoming should be clearly explained and substantiated with multiple direct quotes from the document. ### Example HTML Structure for Presentation of Shortcomings and Limitations: ```html  <h3>[Shortcoming 1 title]</h3><p>[Explanation of the shortcoming]</p> <blockquote>“[Direct quote from the document illustrating the shortcoming.]” (Author, Year, page number)</blockquote> <blockquote>“[Another direct quote related to the same shortcoming.]” (Author, Year, page number)</blockquote> <h3>Shortcoming 2:</h3><p>[Explanation of the second shortcoming]</p> <blockquote>“[Direct quote illustrating the second shortcoming.]” (Author, Year, page number)</blockquote> <blockquote>“[Additional quote related to the second shortcoming.]” (Author, Year, page number)</blockquote> <!-- Continue with additional shortcomings as identified -->  ``` This structured approach ensures a thorough presentation of the document's acknowledged limitations and perceived shortcomings, each supported by direct quotes for a nuanced understanding and critical analysis.{note}",
        "<h2>1.4 Research Gap and Future Research Directions</h2>": f"Guidelines:\nAnalyze the attached word document to extract and articulate the research gaps identified by the author(s) and the suggested future research directions. This analysis should cover the areas the study has not explored or fully addressed, highlighting opportunities for further investigation. Each identified research gap and proposed direction for future research should be clearly explained and, where possible, supported by direct quotes from the document. ### Example HTML Structure for Presentation of Research Gap and Future Research Directions: ```html  <h3>Research Gap </h3><h4>[Research Gap title]</h4> <p>[Detailed explanation of the found research gap identified in the document.]</p> <blockquote>“[Direct quote from the document highlighting this gap.]” (Author, Year, page number)</blockquote><--repeat that structure of h4 and blockcode until three research gaps are found along with direct citation if found--> <h3>Future Research Direction</h3><h4>[Future Research Direction title]</h4><p>[short Explanation of the suggested direction for future research ]</p> <li> [ research question related to the  gap- repeat this list if other important questions are found ]<--repeat that structure of h4 and blockcode with future directions for every gap found-->  ``` This format ensures a comprehensive presentation of the identified research gaps and future research directions, supported by direct citations from the document for clarity and accuracy in understanding the areas needing further exploration.{note}",
        "<h2>1.5 Structure and Keywords</h2>": [
            "Guidelines: 1. Analyze the Document: Extract the Table of Contents (TOC) using common formatting cues in academic papers. 2. Formatting Cues: Look for numbered headings (e.g., 1, 2, 3; 1.1, 1.2; A., B., C...), bold, italic, or larger font sizes. Main headings are usually larger and left-aligned, subheadings might be indented. 3. Verify Accuracy: Cross-reference with the document. 4. HTML Output Example: Provide the TOC in the following HTML format: <h3>TOC:</h3><ul><li>[Main Heading 1]</li><li>[Main Heading 1: Subheading 1.1]</li><li>[Main Heading 1: Subheading 1.2]</li><li>[Main Heading 1: Subheading 1.2: subheading 1.2.1]</li><!-- Additional headings and subheadings as found --></ul>. For headings, use: <li>Main Heading</li>. For subheadings, use: <li>Main Heading: Subheading</li>. if more than one subheadings, continue with main:subheading:subheading:subheading.  Ensure the TOC titles  accurately reflects the structure of the document and subheadings are preceded by its parents headings separated by ':'.\noutput format: code block html```",
            "Guidelines: Analyze the document and extract: 1. Bibliographic information: <h4> Bibliographical Information</h4><ul> <li>Citation style: [analyse the whole document and search for intext citations. if numerical citations like \"cyberspace can be dangerous5\" are found return here numerical. if APA style like author year (Smith, 2022), return APA]</li> <li>Bibliographic position: [In-text or End]</li> </ul> 2. Academic fields (list three primary disciplines with at least two of each): <h4>Academic Fields</h4><ul> <li>Field: [Field found in the article]</li> <li>Research area: [Research area found in the article]</li> </ul> 3. Topics (list up to seven themes, each up to four words): <h4>Themes and Topics:</h4> <ul> <li>Topic: [Theme or Topic found in the article, list up to seven themes, each up to four words]</li> </ul> 4. Research information: <h4>Research information</h4><ul> <li>Research type: [The research type, e.g., Qualitative, Quantitative, Mixed Methods, Experimental, Longitudinal]</li> <li>Research design: [The research design, e.g., Treaty Analysis, Comparative Policy Analysis, Normative Legal Analysis]</li> <li>Data type: [The data type found in the text]</li> 5. Data Collection Methods:<h4>Data Collection Methods</h4> <li>Method:[Method used by the author, e.g., Archival Research, Structured Interviews, Policy Review. If more than one method, create another list in the same format data collection method[method]]</li> </ul>note1 . [] are commands, do not print []. note 2 output in a code block"

]
    }

note_api = [
    {"Key Terms Definitions": "Extract key terms and their definitions from the text using phrases like 'can be defined by', 'is described as', or 'means'. Look for lists, typographic cues (e.g., bold, italics), and keywords (e.g., 'definition', 'concept'). Include any citations. Format the output in HTML with <h2> for key terms and <blockquote> for definitions. Ensure the exact wording from the text is used. Return '' if no clear definitions are found."},

     {"Authors cited": "1. Analyze the text to identify note and numerical citations. This includes statements followed by a number or a number in brackets/parentheses (e.g., 'international relations theories such as realism and neoliberalism are mainstream¹' or 'international relations theories such as realism and neoliberalism are mainstream (1)'). 2. Check if the same number corresponds to a statement preceded by the same number (e.g., '1. John S Davis II and others, ‘Stateless Attribution: Toward International Accountability in Cyberspace’ (RAND Corporation 2017) 21.'). If a sentence is preceded by a number and this number is found following a sentence, it means this is an in-text citation and a corresponding footnote. 3. Handle 'ibid' and similar terms: For 'ibid', repeat the last citation in <h1>, <h2>, and <h3>, updating the <blockquote> with the new statement. Maintain an internal index for footnotes to track references. 4. When a statement is followed by a number, treat it as body text and include it in a <blockquote> with the number highlighted in <strong> tags and the rest of the sentence or other citations not highlighted. 5. When a statement is preceded by a number, treat it as a footnote and include it in an <h2> tag. 6. For each citation, extract the author and year from the footnote information and use it in the <h3> tag. If no author is found, set the value to 'None'. 7. Format the output in HTML: - Use <h1> for the footnote number. - Use <blockquote> for the full sentence with the citation highlighted and other citations not highlighted. - Use <h2> for the footnote information in full. - Use <h3> for the author and year, or 'None' if not available. 8. Ensure 100% accuracy by extracting exact sentences and corresponding footnotes. 9. Handle multiple citations in a sentence by highlighting each citation individually and retrieving them separately. 10. If no citation is found, return ''. 11. Output as a single HTML code block. Note 1: Do not return incomplete <h1>, <blockquote>, <h2>, or <h3> tags. Note 2: Highlight in bold only the corresponding in-text citation statement with the <h2> author and <h3>. Do not highlight every number, only the specific citation."},
     {"Statements database": "Please analyze this document thoroughly and extract all key arguments, main ideas, and entire paragraphs containing the author's original points in an HTML format. Ensure 100% accuracy by extracting exact paragraphs as found in the document, without any modification or paraphrasing. Focus on capturing paragraphs that represent the author's core arguments and ideas. The html format is:h2 [key argument/idea in three or four words] and <blockquote> [statements exact as found in the text with references]. but this statement should not be refering to other authors. Exclude any statement followed by in-text citation (parenthetical, numerical, note] "}
]
methodology_section = {
    "Introduction to Methodology": "In this research, reflexive thematic analysis (TA) is employed to explore [specific topic or research question], aligning with the constructivist paradigm. This approach allows for the interpretation of complex human experiences within peer-reviewed articles, facilitating a deep understanding of the narratives presented in scholarly discourse.",

    "Research Design": "This study adopts a reflexive thematic analysis approach to scrutinize peer-reviewed articles related to [specific field or topic]. The design focuses on extracting and analyzing themes that reflect scholarly discourse and trends, ensuring reliability and validity by utilizing high-quality, vetted sources.",

    "Participant Selection and Sampling": "Describe the selection criteria for the peer-reviewed articles included in this study. Discuss the inclusion and exclusion criteria, such as time frame, relevance to the research question, and academic credibility, to ensure a comprehensive and representative dataset of the literature.",

    "Data Collection Methods": "Detail the process of collecting data, which, in this case, involves the systematic selection and retrieval of peer-reviewed articles from academic databases. Explain the search strategy, including databases used, keywords, and the selection process for relevant articles.",

    "Data Analysis": "Describe the step-by-step process of coding the selected articles, including initial coding, theme development, and refinement of themes. Explain how codes were generated, how themes were identified, and the role of the central organizing concept in synthesizing themes across the literature.",

    "Reflexivity and the Researcher’s Role": "Discuss the researcher’s reflexivity in the analysis process. Reflect on how your background, biases, and theoretical commitments might have influenced the interpretation of the data, and how you accounted for these influences to maintain the rigor of the analysis.",

    "Ensuring Rigor and Trustworthiness": "Explain strategies used to ensure rigor and trustworthiness in your thematic analysis, such as credibility, transferability, dependability, and confirmability. Detail specific actions taken, like member checking or triangulation, to enhance these aspects.",

    "Limitations": "Discuss any limitations encountered in the methodology, such as potential biases in article selection, limitations of the databases used, or challenges in interpreting the data. Explain how these limitations were addressed or their impact on the findings.",

    "Conclusion": "Summarize the methodological approach and reflect on its effectiveness in addressing the research questions. Consider the implications of your methodological choices for the field of study and future research."
}
methodology = {
    "Introduction to Methodology": {
        "Questions": [
            "What are the primary aims and research questions of your study?",
            "Why is Braun and Clarke’s reflexive thematic analysis chosen as the appropriate method?"
        ],
        "Options to Consider": [
            "To explore the lived experiences of [specific group].",
            "To understand the impact of [specific event or condition] on [specific group].",
            "To identify and analyze patterns of [behavior, practice, belief] in [specific context]."
        ]
    },
    "Data Collection": {
        "Questions": [
            "What types of data will be collected (e.g., interviews, observations, textual materials)?",
            "What criteria will you use to select secondary data sources?",
            "How will you ensure data richness and relevance to the research objectives?"
        ],
        "Options to Consider": [
            "Analysis of interview transcripts available in public databases.",
            "Review of observational data from previously published studies.",
            "Utilization of textual material from peer-reviewed articles and official reports."
        ]
    },
    "Data Analysis Process": {
        "Questions": [
            "How will you apply Braun and Clarke's six-phase framework of thematic analysis in your study?",
            "What specific steps will you take to generate initial codes and develop themes from your data?",
            "How will you ensure that the themes developed are deeply connected to the data?"
        ],
        "Options to Consider": [
            "Iterative reading and familiarization with data to develop initial codes.",
            "Searching for themes through an interactive process of data comparison.",
            "Continuous refinement and definition of themes with direct quotes to ground the findings."
        ]
    },
    "Reflexivity and Researcher’s Role": {
        "Questions": [
            "How will your personal background, assumptions, and preconceptions be acknowledged and managed throughout the research process?",
            "What strategies will you use to maintain reflexivity and document these reflections?"
        ],
        "Options to Consider": [
            "Maintaining a reflexive journal throughout the research process.",
            "Engaging with peer debriefing to challenge and refine analytical insights.",
            "Disclosing personal biases and their potential influence on the research analysis."
        ]
    },
    "Ensuring Quality and Rigor": {
        "Questions": [
            "What steps will you take to ensure the credibility and validity of your thematic analysis?",
            "How will you demonstrate that your analysis provides a trustworthy interpretation of the data?"
        ],
        "Options to Consider": [
            "Using techniques such as triangulation, member checking, and rich, thick descriptions.",
            "Providing clear examples of how themes were derived from the data.",
            "Demonstrating an audit trail of decisions made during the research process."
        ]
    },
    "Reporting and Presenting Themes": {
        "Questions": [
            "How do you plan to present the themes in the results section?",
            "What examples or quotes will you use to illustrate the themes and ensure they are rooted in the data?"
        ],
        "Options to Consider": [
            "Structuring the presentation of themes around narrative accounts supported by direct quotes.",
            "Creating thematic maps to visually represent the relationships between themes.",
            "Discussing each theme in detail while linking back to the literature and research questions."
        ]
    },
    "Limitations": {
        "Questions": [
            "What are the potential limitations of using reflexive thematic analysis in your study?",
            "How might these limitations affect the findings and their interpretation?"
        ],
        "Options to Consider": [
            "Acknowledging the subjective nature of the analysis and its impact on the findings.",
            "Discussing the constraints of the sample size and composition.",
            "Considering the implications of the chosen theoretical framework on the analysis."
        ]
    }
}


note_update1_inconstruction =\
    {
        "<h2>1.1 Research Framework</h2>": f"Guidelines:\nTo analyze the attached PDF document, focus on extracting and understanding its core research elements, including the types of research conducted, the study's objectives, the central research problem, core research questions, and the corresponding hypotheses. Each element should be identified and discussed in relation to the content of the document. Provide explanations for the selected research type(s) directly in your analysis, along with citations that exemplify or can be interpreted as representing these research types. Similarly, outline the research problem directly before delving into the research questions and hypotheses, ensuring each is supported by direct references from the text. Here is how to structure your findings in an HTML format: <div> <h3>Research Type:</h3> <ul> <li>Exploration</li> <li>Description</li> <li>Evaluation</li> </ul> <p>[Provide an explanation for the selected research type(s) based on the document's content.]</p> <blockquote>'[Citation that can be interpreted as the research type.]'</blockquote> <h3>Study Objectives</h3>  <h4>[Specific objective of the study]</h4> <h4>[Another specific objective of the study]</h4> <!-- Add more objectives as necessary -->  <h3>Research Problem</h3> <h4>[The main problem the research aims to solve or the 'problematique' of the research]</h4> <h3>Research Questions</h3> <h4>Question 1: [Specific research question]</h4> <blockquote>'[Direct citation from the text supporting this question.]'</blockquote> <h4>Hypotheses</h4> <h5>Hypothesis 1: [Specific hypothesis related to Question 1]</h5> <blockquote>'[Direct citation from the text supporting this hypothesis.]'</blockquote> <!-- Repeat the pattern for additional questions and hypotheses -->  </div> This format ensures a detailed and structured analysis, clearly presenting the study's foundational elements with direct references from the document.{note}",
        "<h2>1.2 Key Terms Definitions</h2>": f"Guidelines:\nPrepare an HTML document that defines key terms as outlined by the author in the attached PDF document, incorporating direct quotes for these definitions. Each term's explanation should be followed by a citation in the proper author, year, page format. This structured approach is designed to enhance the clarity and accuracy of the terminology presentation. ### Example HTML Structure for Correctly Formatted Key Terms Definitions: ```html <div> <h3>Key Terms Defined by the Author</h3> <h4>Adverse Cyber Operation</h4> <blockquote>“Accordingly, an adverse cyber operation is the employment of cyber capabilities with the purpose of causing harm in or by the use of cyberspace.” (Aravindakshan, 2021, page number)</blockquote> <h4>Causality</h4> <blockquote>“Causality is a purely factual issue and asks whether a cyber operation can be traced to a particular computer system and even more importantly to a particular person, group of persons, or entity.” (Aravindakshan, 2021, page number)</blockquote> <h4>Attribution</h4> <blockquote>“In contrast, attribution of the conduct of a particular person, group of persons, or entity to a particular State is primarily a normative issue.” (Aravindakshan, 2021, page number)</blockquote> <h4>Standard of Proof</h4> <blockquote>“The standard of proof denotes the degree of probability that must be achieved for the trier of facts to determine the factual allegation is correct.” (Aravindakshan, 2021, page number)</blockquote> <h4>Active Defense</h4> <blockquote>“Indeed some scholars conclude that countermeasures against adverse cyber operations may take the form of so-called ‘active defenses’ or ‘active cyber defenses,’ which are ‘in-kind response(s) ... against the attacker’s system.’” (Aravindakshan, 2021, page number)</blockquote> <h4>Due Diligence</h4> <blockquote>“...with regard to adverse cyber operations causality, attribution, and evidentiary issues are also and decisively informed by the exercise of due diligence (or lack thereof) by the State of origin...” (Aravindakshan, 2021, page number)</blockquote> </div> ``` Note: Replace 'XX' with the actual page numbers where these quotes can be found in the document. This structure is devised to ensure a detailed and accessible presentation of key terms with direct quotes from the document, correctly formatted to include author, year, and page number for precise referencing.{note}",
        "<h2>1.3 Key Findings</h2>": f"Guidelines:\nDive into the attached PDF document to thoroughly identify its key findings. Concentrate on presenting a detailed analysis of these findings, outlining the main conclusions drawn by the authors within the study. For each finding, provide a clear explanation that encapsulates the essence of the discovery or conclusion, and include multiple direct quotes from the document that illustrate or support these findings. ### Example HTML Structure for Presentation of Findings: ```html <div> <h2>Findings</h2> <ul> <li><strong>1. [Finding Statement]:</strong> <p>[Provide an explanation that fully develops the author's finding, focusing exclusively on the content and conclusions within the study.]</p> <blockquote>'[Direct quote from the document illustrating the finding.]' (Author, Year, page number)</blockquote> <blockquote>'[Another direct quote related to the same finding.]' (Author, Year, page number)</blockquote> </li> <!-- Repeat for each key finding identified --> </ul> </div> ``` This structured approach is designed to facilitate an in-depth and focused examination of the study’s findings, supported by direct quotations from the text for a comprehensive understanding.{note}",
        "<h2>1.4 Shortcomings Limitations</h2>": f"Guidelines:\nPerform an in-depth examination of the attached PDF document to identify and elucidate its shortcomings and limitations. Your analysis should scrutinize the document thoroughly, extracting specific instances where the paper acknowledges its own limitations or where you perceive potential weaknesses. Each identified shortcoming should be clearly explained and substantiated with multiple direct quotes from the document. ### Example HTML Structure for Presentation of Shortcomings and Limitations: ```html <div> <ul> <li><strong>Shortcoming 1:</strong> <p>[Explanation of the shortcoming]</p> <blockquote>“[Direct quote from the document illustrating the shortcoming.]” (Author, Year, page number)</blockquote> <blockquote>“[Another direct quote related to the same shortcoming.]” (Author, Year, page number)</blockquote> </li> <li><strong>Shortcoming 2:</strong> <p>[Explanation of the second shortcoming]</p> <blockquote>“[Direct quote illustrating the second shortcoming.]” (Author, Year, page number)</blockquote> <blockquote>“[Additional quote related to the second shortcoming.]” (Author, Year, page number)</blockquote> </li> <!-- Continue with additional shortcomings as identified --> </ul> </div> ``` This structured approach ensures a thorough presentation of the document's acknowledged limitations and perceived shortcomings, each supported by direct quotes for a nuanced understanding and critical analysis.{note}",
        "<h2>1.5 Research Gap and Future Research Directions</h2>": f"Guidelines:\nAnalyze the attached PDF document to extract and articulate the research gaps identified by the author(s) and the suggested future research directions. This analysis should cover the areas the study has not explored or fully addressed, highlighting opportunities for further investigation. Each identified research gap and proposed direction for future research should be clearly explained and, where possible, supported by direct quotes from the document. ### Example HTML Structure for Presentation of Research Gap and Future Research Directions: ```html <div> <ul> <li><strong>Research Gap 1:</strong> <p>[Detailed explanation of the first research gap identified in the document.]</p> <blockquote>“[Direct quote from the document highlighting this gap.]” (Author, Year, page number)</blockquote> </li> <li><strong>Future Research Direction 1:</strong> <blockquote>“[Direct quote from the document suggesting this future research direction.]” (Author, Year, page number)</blockquote>  <p>[short Explanation of the suggested direction for future research and one research question related to the first gap ]</p></li> <!-- Repeat for additional gaps and future research directions as identified --> </ul> </div> ``` This format ensures a comprehensive presentation of the identified research gaps and future research directions, supported by direct citations from the document for clarity and accuracy in understanding the areas needing further exploration.{note}",
        "<h2>2.1 Data, Analysis and Epistemologies</h2>": f"Guidelines:\nConduct a detailed analysis of the attached PDF document to assess the data collection techniques, data analysis methods, and epistemological foundations employed in the study. Your analysis should focus on identifying the specific methodologies used, discussing their application and relevance to the research objectives, and explaining the theoretical underpinnings that guide the study's approach. ### Example HTML Structure for Presentation: ```html <div> <p>This article will rely on the standards used by the ICJ, while also pointing out a few decisions by other international judicial forums as well.” (Aravindakshan, 2021, p. 286)</p> <h3>Data Collection Techniques</h3> <ol> <li><strong>Sampling Techniques:</strong> The study employs a purposive sampling technique, selecting ICJ cases relevant to the discussion of standards of proof.</li> <li><strong>Data Collection Instruments:</strong> The primary data collection instruments are legal documents, including ICJ judgements, legal statutes, and international treaties.</li> <li><strong>Measurement Tools:</strong> The measurement tools are qualitative, focusing on the interpretation of legal texts and judgements.</li> </ol> <h3>Data Analysis</h3> <ol> <li><strong>Quantitative Analysis:</strong> Not applicable. The study focuses on legal theory and jurisprudence without employing statistical analysis.</li> <li><strong>Qualitative Analysis:</strong> Thematic analysis is used to examine ICJ cases and legal principles, identifying themes related to standards of proof.</li> <li><strong>Mixed-Methods Analysis:</strong> Not applicable. The research focuses exclusively on qualitative legal analysis.</li> </ol> <h3>Epistemological Foundations</h3> <ol> <li><strong>Interpretivism:</strong> The research embodies an interpretivist epistemological stance, interpreting legal texts, principles, and judicial decisions.</li> <li><strong>Critical Realism:</strong> Elements of critical realism could be inferred, acknowledging the complexity of legal practices and the influence of broader social, political, and historical factors.</li> <li><strong>Pragmatism:</strong> The pragmatic implications of the research aim to enhance the clarity and fairness of ICJ decisions.</li> </ol> <h4>Research Design and Epistemological Considerations</h4> <p>The research questions explore the application and implications of standards of proof within ICJ jurisprudence, reflecting an interpretivist perspective.</p> </div> ``` This structured approach ensures a comprehensive examination and presentation of the study's methodological and theoretical framework, supported by insights into the data sources, analytical techniques, and epistemological foundations.{note}",
        "<h2>2.2 Theoretical Framework or Models</h2>": f"Guidelines:\nExamine the attached PDF document to discern and articulate the theoretical frameworks and models that underlie the research. This involves two main tasks: identifying the frameworks or/and models that guide the study's conceptual underpinnings or cited by the author. For each category, provide a clear explanation based on the document's content, supplemented by direct quotes as evidence of these theoretical/model orientations. If the document lacks direct mention of frameworks or models, or if they cannot be inferred with confidence, please denote this with 'NA'. ### Guideline for HTML Presentation: ```html <div> <h3>Framework</h3> <p>[Provide a short explanation of the identified theoretical framework, detailing how it underpins the study's research approach and its significance to the study's objectives. If no framework is mentioned or can be inferred, state 'NA'.]</p> <blockquote>'[Direct quote from the document illustrating the theoretical framework]' (Author, Year, p. X).</blockquote> <h3>Models</h3> <p>[Explain the models used in the study, discussing how they are applied within the research design and analysis, and their relevance to the research questions or cited by the author. If no models are mentioned or can be inferred, state 'NA'.]</p> <blockquote>'[Direct quote from the document suggesting the application or relevance of the model]' (Author, Year, p. X).</blockquote> </div> ``` This approach ensures a detailed and structured examination of the theoretical bases of the research, offering clarity and depth in the presentation of frameworks and models, supported by direct quotations from the study.{note}",
        "<h2>2.3 Implications and Policy</h2>": f"Guidelines:\nDelve into the attached PDF document to explore and summarize the implications and policy recommendations it presents. Focus on extracting the practical implications for the field or industry, theoretical contributions to the academic discipline, and specific policy recommendations or considerations that emerge from the research findings. Discuss how these implications and recommendations aim to address the research problem, fill identified gaps, or influence policy and practice. If the document does not explicitly detail implications or policy recommendations, or if they cannot be reasonably inferred from its content, please indicate 'NA'. ### Guideline for HTML Presentation: ```html <div> <h2>Implications and Policy</h2> <h3>Practical Implications</h3> <p>[Summarize the practical implications of the research findings, detailing how they can be applied in the field or industry. If no practical implications are mentioned or can be inferred, state 'NA'.]</p> <blockquote>'[Direct quote from the document highlighting practical implications]' (Author, Year, p. X).</blockquote> <h3>Theoretical Contributions</h3> <p>[Discuss the theoretical contributions of the study, explaining how they enhance or challenge existing academic perspectives. If no theoretical contributions are mentioned or can be inferred, state 'NA'.]</p> <blockquote>'[Direct quote from the document supporting theoretical contributions]' (Author, Year, p. X).</blockquote> <h3>Policy Recommendations</h3> <p>[Outline the policy recommendations made by the research, including any proposed changes or considerations for policymakers. If no policy recommendations are mentioned or can be inferred, state 'NA'.]</p> <blockquote>'[Direct quote from the document suggesting policy recommendations]' (Author, Year, p. X).</blockquote> </div> ``` This structured approach ensures a comprehensive presentation of the implications and policy recommendations stemming from the research, supported by direct quotations from the document for a clear and insightful analysis.{note}",
        "<h2>2.4 Author Reference_processing</h2>": f"Guidelines:\nTo analyze the attached PDF document,focusing exclusively on the significant references made within, specifically from authors (not companies or entities). Your analysis should be structured into two primary sections with the following detailed tasks and presented in the given HTML format: 1. **Footnotes Examination:** Carefully go through all footnotes to identify key citations from authors. For each significant author citation, you are to: - Determine its relevance by matching the citation number with its context in the text. - For each cited author, use an HTML `<h5>` tag for the bibliographic reference. - Provide a context block detailing the significance of the citation within the document, followed by a direct quote or summary. Immediately after the context, include the direct citation from our document, precisely indicating the author's name, year, and page. Ensure this analysis includes more than five author citations for depth. 2. **Author-Year Style Reference_processing:** Search for and analyze any references made in the author-year style within the text. If absent, explicitly note 'NA' in this section. Here's an HTML template for your output, emphasizing author contributions and direct citations within the analysis context: ```html <div> <h3>Principal Authors Referenced in the Research</h3> <h4>Footnotes Style</h4> <div> <h5>Marco Roscini (2015)</h5> <p>'Evidentiary Issues in International Disputes Related to State Responsibility for Cyber Operations,' <em>Texas International Law Journal</em>, 50(2), 233-256.</p> <blockquote> Context: Roscini's insights are leveraged to delve into the evidence complexities in cyber operation state responsibility cases. He articulates, 'While the standard of proof...over a non-state actor that caused the violation.' <br><cite>Roscini, cited in Aravindakshan (2021, p. 287)</cite> </blockquote> </div> <!-- Include at least five more author citations with the above structure --> <h4>Author-Year Style Reference_processing</h4> <p>NA</p> </div> ```\nnote:if less than 5 authors are found, read carefully the pdf again and find more authors. ",
        "<h2>2.5 Entity Reference</h2>": f"Guidelines:\nTo analyze the attached PDF document, focusing exclusively on references to entities such as organizations, governmental bodies, legal cases, and publications. This analysis should elucidate how these references contribute to the discussion on cyberattacks and international law. The analysis must be formatted for HTML presentation and meticulously cover at least eight distinct entity references without placeholders, following these enhanced instructions: 1. **Detailed Footnotes Examination for Entity Reference_processing:** Review all footnotes to identify references strictly to entities. Each entity reference should: - Be accurately linked to its context within the text. - Be highlighted with an `<h5>` tag, numbered as a subsection under the `<h4>` section, corresponding to the sequence of entity references. - Include a context block detailing the citation's significance, immediately followed by a direct quote from the document, ensuring the citation format is correct and precise. 2. **Author-Year Style Reference_processing Examination:** Accurately identify and format references made to entities in the author-year style within the text. If such references do not pertain to entities or are absent, denote 'NA'. Use the following HTML template for your output, ensuring clarity, accuracy, and inclusion of direct quotes from the text for each cited entity: ```html <div> <h3>Principal Entities Referenced in the Research</h3> <h4>Footnotes Style</h4> <div> <h5>4.1 NATO Cooperative Cyber Defence Centre of Excellence (CCD COE)</h5> <p>Insights on cyber defence and legal frameworks.</p> <blockquote> Context: \"The CCD COE's work...\" <br><cite>Direct quote from Aravindakshan's text discussing the CCD COE's impact.\" (2021)</cite> </blockquote> </div> <div> <h5>4.2 International Court of Justice (ICJ)</h5> <p>Reference_processing to cases elucidating international legal standards.</p> <blockquote> Context: \"ICJ case law...\" <br><cite>\"Direct quote from Aravindakshan's text on ICJ's relevance.\" (2021)</cite> </blockquote> </div> <!-- Continue with additional entities, following the structured format and ensuring direct quotes are included --> <h4>Author-Year Style Reference_processing</h4> <p>NA</p> </div> ``` This directive is crafted to ensure a comprehensive overview of significant entity references within 'Cyberattacks: a look at evidentiary thresholds in International Law', highlighting their key roles in the discourse on cyberattack attribution and international law, strictly focusing on entities with precise citations and direct quotes.{note}",
        "<h2>3.1 Structure and Keywords</h2>": f"Guidelines:\n Please perform a thorough analysis based on the following guidelines and format the output as detailed in the provided div structure: 1. **Article Schema:** Outline the article's structure with main headings and subheadings. Aim to provide a comprehensive table of contents. 2. **Keyword Extraction:** Identify and list academic keywords or phrases crucial for systematic review coding. Concentrate on extracting terms reflecting the core themes and methodologies. Limit phrases to three words where possible. 3. **Detailed Analysis:** Break down your analysis into specific categories: - **Academic Fields and Research Areas:** Identify the 5 primary disciplines or fields. - **Themes and Topics:** Extract 10 detailed themes or topics[they should not exceed 4 words]. - **Methodologies Keywords:** Highlight keywords for coding, focusing on methods like 'qualitative analysis', 'quantitative analysis', 'mixed-methods analysis'; epistemologies like 'positivism', 'interpretivism', 'critical realism'; and theories like 'realism', 'liberalism', 'constructivism'. - **Countries and Regions:** Note 6 significant  countries specifing where they were found with context . - **Affiliations** Note 1 significant affiliations .Example structure within a div: ```html <div><h3>Article Schema:</h3><ul><li>Abstract</li><li>Section 1: Title</li><li>Section 2: Title</li></ul><h4>Academic Fields and Research Areas:</h4><ul><li>Field 1</li><li>Field 2</li><li>Field 3</li></ul><h4>Themes and Topics:</h4><ul><li>Theme 1</li><li>Theme 2</li><!-- More themes as needed --></ul><h4>Methodologies Keywords:</h4><ul><li>Qualitative Analysis</li><li>Positivism</li><li>Realism</li><!-- More methodologies as needed --></ul><h4>Countries, and Regions:</h4><ul><li>Region 1 title (the short context where is was found)</li><li>Country 1(the short context where is was found)</li><!-- More affiliations and countries as needed --></ul><h4>Affiliations:</h4><ul><li>Affiliation 1 (the short context where is was found)</li><ul></div> ``` Ensure your analysis fills in the placeholders based on the document's content.{note}",
        "<h2>3.2 Main Topics</h2>": f"Guidelines:\nTo systematically analyze the attached PDF document, identify and elaborate on the top 5 main topics covered, incorporating explanations, their significance, and providing multiple direct citations related to each topic. Structure your findings in an HTML format for clarity and comprehensive presentation. ### Example HTML Structure for Main Topics Analysis: ```html <div> <h3>Main Topics Analyzed:</h3> <ol> <li><strong>Public Attribution and its Limitations:</strong> <p>This topic explores the governments' practice of public attribution, detailing its potential benefits and significant limitations, questioning the effectiveness of public attribution in deterring cyber misconduct.</p> <blockquote>“a state that has been victim to a cyber-attack has to also be able to resort to legal remedies since the benefits of public attribution, though important, are still limited.” (Aravindakshan, 2021, p. 288)</blockquote> </li> <li><strong>Legal Remedies in International Law:</strong> <p>Focuses on the advantages of seeking legal remedies through international forums over public attribution, highlighting the potential for tangible outcomes like injunctions and reparations.</p> <blockquote>“Pursuing legal remedies in an international legal forum can result in tangible benefits such as injunctions and reparations, serving as strong reminders that cyber mal-activities have real consequences.”</blockquote> </li> <li><strong>Evidentiary Thresholds in Cyber Operations:</strong> <p>Discusses the challenges of meeting evidentiary standards in proving state responsibility for cyber operations and the potential role of circumstantial evidence.</p> <blockquote>“...it should be noted that no matter what the attributive test, the evidentiary standard of proof remains high and the methods of proof in cyberspace difficult to navigate.”</blockquote> </li> <li><strong>Challenges in Cyberspace for Legal Attribution:</strong> <p>Addresses the difficulties of legal attribution in cyberspace, including issues like anonymity and the use of proxies that complicate attribution efforts.</p> <blockquote>“Despite the technical detail in these Reports, the connections drawn by them from inferences or ‘dots’, so to speak, to link the perpetrators to the states, are tenuous and not likely to meet legal thresholds.”</blockquote> </li> <li><strong>Recommendations for Lowering the Attribution Threshold:</strong> <p>Examines proposals for adjusting control tests in cyber attribution to address evidentiary challenges, critiquing the adequacy of these efforts.</p> <blockquote>“As for ongoing efforts to lower the threshold for attribution in case of non-state actors...it is worthwhile to point out that these tests of attribution should not be conflated with the standards of proof that states’ evidence must meet to prove their claims.”</blockquote> <blockquote>“In the cyber domain, new tests are being proposed...even lower threshold than the overall control test.”</blockquote> </li> </ol> </div> ``` This HTML structure is designed to ensure a detailed and accessible presentation of the critical discussions within the document, supported by direct citations for a comprehensive overview and insightful understanding.{note}",
        "<h2>3.3 Thematic Analysis 1</h2>": f"Guidelines:\nEngage in a thematic analysis focusing on 'Cyber Law Principles,' 'Responses to Cyber Attribution,' and 'Cyber Evidence Standards.' For each theme, delve into the relevant subthemes, providing explanations supported by multiple direct quotes from the document. This analysis should illuminate the intricacies and applications of these themes within the context of the study. ### Example HTML Structure: ```html <div> <h3>Cyber Law Principles</h3> <h4>Subtheme 1</h4><blockquote>'[Quote 1]'</blockquote> <blockquote>'[Quote 2]'</blockquote> <h3>Responses to Cyber Attribution</h3> <h4>Subtheme 2</h4> <p>Explanation of the various responses to cyber attribution challenges.</p> <blockquote>'[Quote 1]'</blockquote> <blockquote>'[Quote 2]'</blockquote> <h3>Cyber Evidence Standards</h3> <h4>Subtheme 3</h4> <p>Summarize standards and practices of cyber evidence in attribution.</p> <blockquote>'[Quote 1]'</blockquote> <blockquote>'[Quote 2]'</blockquote> </div> ``` Ensure your analysis comprehensively covers these principles, examining their relevance and implications for cyber attribution practices, with a clear presentation of multiple quotes for rich insight.{note}",
        "<h2>3.4 Thematic Analysis 2</h2>": f"Guidelines:\nPerform an analysis on 'Information Sharing and Intelligence Methods Disclosure,' 'Geopolitical Implications of attribution,' and 'The Interdisciplinary Nature of Cyber Attribution.' Each theme should be broken down into subthemes, with detailed explanations and supported by multiple quotes from the document. ### Example HTML Structure: ```html <div> <h3>Information Sharing and Intelligence Methods Disclosure</h3> <h4>Subtheme 1</h4><blockquote>'[Quote 1]'</blockquote> <blockquote>'[Quote 2]'</blockquote> <h3>Geopolitical Implications of attribution</h3> <h4>Subtheme 2</h4> <p>Detail the specific attribution solutions proposed in the document.</p> <blockquote>'[Quote 1]'</blockquote> <blockquote>'[Quote 2]'</blockquote> <h3>Interdisciplinary Nature of Cyber Attribution</h3> <h4>Subtheme 3</h4> <p>Explore the integration of technical challenges with broader societal aspects.</p> <blockquote>'[Quote 1]'</blockquote> <blockquote>'[Quote 2]'</blockquote> </div> ``` This analysis is aimed at delving into the complexities and suggestions within the study, providing an enriched understanding through multiple perspectives and direct quotations.{note}",
        "<h2>3.5 Thematic Analysis 3</h2>": f"Instructions:\nCarry out a detailed examination focusing on 'Challenges of Cyber Attribution,' 'Opportunities in Cyber Attribution,' 'Problems in Cyber Attribution,' and 'Solutions for Cyber Attribution.' For each main topic, explore the related subtopics, giving clear explanations backed up with direct quotes from the document. This exploration should shed light on how these topics are presented and their significance in the context of cyber attribution. ### Example HTML Structure: ```html <div> <h3>Challenges of Cyber Attribution</h3> <h4>Subtopic 1</h4><blockquote>'[Quote 1]'</blockquote> <blockquote>'[Quote 2]'</blockquote> <h3>Opportunities in Cyber Attribution</h3> <h4>Subtopic 2</h4> <p>Discuss the opportunities that arise from cyber attribution efforts.</p> <blockquote>'[Quote 1]'</blockquote> <blockquote>'[Quote 2]'</blockquote> <h3>Problems in Cyber Attribution</h3> <h4>Subtopic 3</h4> <p>Outline the problems that persist in the field of cyber attribution.</p> <blockquote>'[Quote 1]'</blockquote> <blockquote>'[Quote 2]'</blockquote> <h3>Solutions for Cyber Attribution</h3> <h4>Subtopic 4</h4> <p>Propose solutions or methods to address cyber attribution challenges.</p> <blockquote>'[Quote 1]'</blockquote> <blockquote>'[Quote 2]'</blockquote> </div> ``` Your examination should thoroughly investigate these areas, highlighting their importance and the implications for cyber attribution efforts, with a structured presentation of multiple quotes for depth of understanding.{note}"
}
sections_prompt ={
    "<h2>1.1 Research Framework</h2>": "<div> <h3>Research Type:</h3> <ul> <li>Exploration</li> <li>Description</li> <li>Evaluation</li> </ul> <p>[Analyze the document to determine the research types, providing explanations with citations as examples.]</p> <h3>Study Objectives</h3> <ul> <li>Objective 1: [Define objective 1]</li> <li>Objective 2: [Define objective 2]</li> </ul> <p>[Identify study objectives from the document, supported by direct citations.]</p> <h3>Research Problem</h3> <ul> <li>[Outline the central research problem/problematique of the article.]</li> </ul> <h4>Research Questions</h4> <ul> <li>Question 1: [State the question]</li> <blockquote>'[Support with a direct citation]'</blockquote> <h5>Hypotheses</h5> <li>Hypothesis 1: [Formulate the hypothesis]</li> <blockquote>'[Support with a direct citation]'</blockquote> </ul> </div>",
    "<h2>1.2 Key Terms Definitions</h2>": "Find terms defined by the author<div> <h3>Key Terms Defined by the Author</h3> <h4>Term 1</h4> <blockquote>'[Definition]' (Author, Year, Page)</blockquote> <h4>Term 2</h4> <blockquote>'[Definition]' (Author, Year, Page)</blockquote> <p>[Define key terms using direct quotes from the document, each followed by a citation.]</p> </div>",
    "<h2>1.3 Key Findings</h2>": "<div> <h3>Findings</h3> <ul> <li><strong>[Findings title 1]:</strong> <p>[Summarize the finding]</p> <blockquote>'[Direct quote illustrating the finding]' (Author, Year, Page)</blockquote> </li> [other findings in the same format]</div>",
    "<h2>1.4 Shortcomings Limitations</h2>": "<div> <h3>Shortcomings and Limitations</h3> <ul> <li><strong>[Shortcoming 1]:</strong> <p>[shortcoming description]</p> <blockquote>'[Direct quote]' (Author, Year, Page)</blockquote>  [other shortcomings in the same format]</li> </div>",
    "<h2>1.5 Research Gap and Future Research Directions</h2>": "<div> <h3>Research Gaps</h3> <ul> <li><strong>[Research Gap title 1]:</strong> <p>[Explain the gap]</p> <blockquote>'[Direct quote highlighting the gap]' (Author, Year, Page)</blockquote> </li>[other research gaps in the same format] <h3>Research Directions</h3><li><strong>Future Research Direction title 1:</strong> <p>[Suggest a direction]</p> <blockquote>'[Supporting quote]' (Author, Year, Page)</blockquote> </li> </ul> <p>[Outline future directions, with evidence from the document.]</p> </div>",
    "<h2>2.1 Main Topics</h2>": "<div><h3>Main Topics Analyzed:</h3><ol><li><strong>[Topic 1 title]:</strong> <p>[Summary.]</p> <blockquote>'[Direct quote]' (Author, Year, Page)</blockquote></li><p>[Identify and elaborate on main topics with direct citations for clarity.] </p>[other topics in the same format]</div>",
    "<h2>2.2 Author Reference_processing</h2>": "Examine key author references, providing context and direct quotes. Search particularly for footnotes with references numbered or in text citation, normally in the format (author,year)<div> <h3>Principal Authors Referenced in the Research</h3> <h4>Footnotes Style</h4> <div> <h5>[Author 1 (Year)]</h5> <p>[Summary.]</p> <blockquote>Context: '[Context]' <br><cite>'[Direct quote]' (Author, Year, Page)</cite> </blockquote> </div> <h4>Author-Year Style Reference_processing</h4> <p>[Summarize or state 'NA']</p> </div>",
    "<h2>2.3 Entity Reference</h2>": "Examine key entity references, providing context and direct quotes. Search particularly for footnotes with references numbered or in text citation, normally in the format (entity,year)<div> <h3>Principal Entities Referenced in the Research</h3> <h4>Footnotes Style</h4> <div> <h5>Entity 1</h5> <p>[Summary.]</p> <blockquote>Context: '[Context]' <br><cite>'[Direct quote]' (2021)</cite> </blockquote> </div> <h4>Author-Year Style Reference_processing</h4> <p>[Summarize or state 'NA']</p> <p>[Detail entity references within the context of cyberattacks and international law, including direct quotes.]</p> </div>",
    "<h2>2.4 Structure and Keywords</h2>": "<div><h3>Article Schema:</h3><ul><li>Section 1: [Title]</li><li>Section 2: [Title]</li></ul><h4>Academic Fields and Research Areas:</h4><ul><li>Field 1: [Define]</li><li>Field 2: [Define]</li></ul><h4>Themes and Topics:</h4><ul><li>Theme 1: [Define]</li><li>Theme 2: [Define]</li></ul><h4>Methodologies Keywords:</h4><ul><li>Method 1: [Define]</li><li>Method 2: [Define]</li></ul><h4>Affiliations, Countries, and Regions:</h4><ul><li>Affiliation 1: [Define]</li><li>Country 1: [Define]</li></ul><p>[Perform a comprehensive analysis, using direct quotes where possible.]</p></div>",

}

updgrade = {"introduction":
                {"Definitions":"""
1.Cyber Operations: The employment of cyber capabilities with the primary purpose of achieving objectives in or by the use of cyberspace tallin glossary,"
2. 'Article 2 of the International Law Commission’s Articles on State Responsibility clarifies the two elements constituting internationally wrongful acts: There is an internationally wrongful act of a State when conduct consisting of an action or omission: (a) is attributable to the State under international law; and (b) constitutes a breach of an international obligation of the State' (T Mikanagi, 2021)"""
                 }}





# overall_score ="""
# now  evaluate the student assignment(first document)  thoroughly and then provide scores(based on the second document:marking rubric), list of weeknesses,strengths, directions
# in the following format:
#  <div class="container"><h1>Score Explanation</h1><h2>Overall Score: [total] = Conceptual [score] + Critical [score] + Communication [score]</h2><h3>Conceptual Score: [score]</h3><p>[Evaluate understanding and guidelines adherence, address question success.]</p><h3>Critical Score: [score]</h3><p>[Assess logical coherence and concept integration.]</p><h3>Communication Score: [score]</h3><p>[Examine spelling, coherence, effectiveness.]</p><h2>Weaknesses and future directions:</h2><ul><li>CONTEXT: [Detail]<p>[Suggest improvements and research directions related to weekness]</p></li><li>EVIDENCE: [Detail]<p>[Suggest improvements and research directions related to weekness]</p></li><li>ANALYSIS STRUCTURE: [Detail]<p>[Suggest improvements and research directions related to weekness]</p></li><li>ADDITIONAL ANALYSIS: [Detail]<p>[Suggest improvements and research directions related to weekness]</p></li><li>REUSABILITY: [Detail]<p>[Suggest improvements and research directions related to weekness]</p></li></ul><h2>Strengths:</h2><ul><li>CONTEXT: [Detail]</li><li>EVIDENCE: [Detail]</li><li>ANALYSIS STRUCTURE: [Detail]</li><li>ADDITIONAL ANALYSIS: [Detail]</li><li>REUSABILITY: [Detail]</li></ul>
# </div>
# \nnote: 1.take your time, dont rush to respond.  2. more guidelines are in [], so responses should be replaced by it. 3. read every document before responding and come with your own conclusion before responding. the score should be stemmed of your analysis of the student assignment agaisnt the marking rubric and the assignment instructions. 4. provide citation to support your responses in the format (section, page) 5.output in html in code block
# """
# feedback= """now first, read the student assignment again attached and search for the positive aspects of the assignment related to the marking rubric and the assignment instructions. then search for weekneesses and think about ways to improve it. then write the score and find the range in the marking rubric document and write the feedback inspired by it.
#  before providing feedback, read marking rubric(second document) and feedback template ( third document ) to output a feedback trictly from those documents, while adpating to the student assignment .the feedback should be in prose and contain 350 words overall . in the following format:
#  <div class="container">
#  <h2>Overall Score: [total] = Conceptual [score] + Critical [score] + Communication [score]</h2>
#  <h2>Feedback</h2>
#  <p> [start by an opening compliment eg:This was [excellent,an outstanding, very good, good] submission. then list what was good about the assignment, providing direct references to the student eg "You provided an excellent overview of proposed evidence requirements, and your two tables bridging the evidence needs with existing and proposed analysis (table 2) were a cleverly structured"]</p>
#  <p> [start this paragraph by providing another positive feedback but constrasting with the main negative one, proposing improvements to the future eg. A minor note is that it might help your future reader to have a visual accompany your proposed ideas. You have great clarity about the interconnections and sequential dependencies (input-output / validation) between activities. For some it may help to have a visual reference point. Overall, a pleasure to read and well done.]</p>
#  </div>
#   your response output must be in  div in code block"""
# questions_note="\nnote:1.provide references in the format(section, page) 2. more guidelines are in [], so responses should be replaced by it. 3. for the lists, every theme found list them one by one with citation and new line. 4. citation format is (section, page). 5. output in a html div code block."
# questions_addressed = [
#     f"""act as a professor:take your time, dont rush to respond. evaluate the student assignment document(document 1) checking the assignment instructions(document 2) and return  a code block htmt with your evaluation in the following format:
#     <div><h1>Assignment Evaluation - Context and Purpose</h1><div><h2>1. Context and Purpose</h2><h3>Assumptions about UAE Science Context</h3><ol><li>Assumption 1: [Check for student's identification of assumptions specific to UAE's advanced sciences fields like materials science, physics, etc., with direct citation or return NA if none found (section, page)].</li></ol><h3>Overarching Purpose of the UAE Science 2035 Strategic Framework</h3><ol><li>Purpose 1: [Evaluate the student’s understanding of the strategic framework's goal to guide UAE's development in science over the next decade, with direct citation or return NA if none found (section, page)].</li></ol><h3>Users and Uses of the Analysis</h3><h4>Users</h4><ol><li>User Group 1: [List specific user groups the student identifies as stakeholders of the UAE Science 2035 project, with direct citation or return NA if none found (section, page)].</li></ol><h4>Uses</h4><ol><li>Use Case 1: [Review how the student describes the application of the UAE Science 2035 analysis in policy making and strategy development, with direct citation or return NA if none found (section, page)].</li></ol><h3>Main Challenges to Quality of Analysis</h3><ol><li>Challenge 1: [Examine student's discussion on potential challenges like resource limitations or time constraints impacting the quality of analysis, with direct citation or return NA if none found (section, page)].</li></ol><h2>2. Evidence Requirements</h2><h3>Types of Analytic Evidence</h3><h4>Type</h4><ol><li>Evidence Type 1: [Verify the types of analytic evidence the student mentions, ensuring they align with the needs of the UAE Science 2035 framework, with direct citation or return NA if none found (section, page)].</li></ol><h4>Purpose</h4><ol><li>Purpose of Evidence 1: [Confirm the student's understanding of how each type of evidence serves the framework's goals, with direct citation or return NA if none found (section, page)].</li></ol><h4>Illustrative Example</h4><ol><li>Example 1: [Check for illustrative examples provided by the student to demonstrate understanding of the evidence type, with direct citation or return NA if none found (section, page)].</li></ol><h3>Interplay of Evidence</h3><ol><li>Interplay 1: [Assess how well the student describes the interdependencies between different types of evidence, with direct citation or return NA if none found (section, page)].</li></ol></div>
#     {note}""",
#     f"""likewise for:
#     <div><h2>3. Structure of Analytic Process</h2><h3>Outline of Analytic Activities</h3><ol><li>Activity 1: [Evaluate the student’s proposed structure of analytic activities needed for UAE Science 2035, including their purpose and outcomes, with direct citation or return NA if none found (section, page)].</li><li>Activity 2: [Further evaluation details with direct citation or return NA if none found (section, page)].</li><li>Activity 3: [Additional activity details with direct citation or return NA if none found (section, page)].</li></ol><h3>Rationale for Data Sources</h3><ol><li>Data Source Rationale 1: [Review the student's rationale for choosing specific data sources and how they align with the project's needs, with direct citation or return NA if none found (section, page)].</li></ol><h3>Mitigation of Project Failure</h3><ol><li>Mitigation Step 1: [Assess student's proposed steps to avoid or mitigate potential failures in the project, with direct citation or return NA if none found (section, page)].</li></ol><h3>Contribution of the Elsevier Bibliometric Analysis</h3><ol><li>Contribution 1: [Check the student’s understanding of how the Elsevier report contributes to the UAE Science 2035 framework, with direct citation or return NA if none found (section, page)].</li></ol><h2>4. Additional Analysis</h2><h3>Purpose and Objectives</h3><ol><li>Purpose 1: [Ensure the student clearly defines the purpose and objectives of any suggested additional analyses, showing how they support the main framework, with direct citation or return NA if none found (section, page)].</li></ol><h3>Data Collection Methods</h3><h4>Data Sources</h4><ol><li>Data Source 1: [Review the appropriateness of the data sources/types suggested by the student for additional analysis, with direct citation or return NA if none found (section, page)].</li></ol><h4>Methods</h4><ol><li>Method 1: [Examine the student's identification and rationale for the methods chosen for data analysis, considering their strengths and weaknesses, with direct citation or return NA if none found (section, page)].</li></ol><h3>Reflection on Biases</h3><ol><li>Bias Consideration 1: [Evaluate the student's reflections on potential biases in data collection, analysis, and interpretation, with direct citation or return NA if none found (section, page)].</li></ol><h3>Criteria for Judging Quality of Analysis</h3><ol><li>Quality Criterion 1: [Assess the student’s criteria for evaluating the quality of additional analysis, with direct citation or return NA if none found (section, page)].</li></ol><h2>5. Reusability and Reproducibility</h2><h3>Adoption of Open Science Principles</h3><ol><li>Open Science Principle 1: [Review the student’s recommendation on Open Science principles to be adopted, ensuring they are suitable for enhancing the project's reusability and reproducibility, with direct citation or return NA if none found (section, page)].</li></ol></div>
#     {note}"""
# ]How do these phenomena (air quality and citizen health) interact or interrelate?

responses = [
    f"Evaluate the attached assignment providing responses to the assignment with direct citation in the following format: <h1>Part 1. Exploratory Data Analysis</h1> <h2>Q1. Produce for the Mayor</h2> <h3>How do these phenomena (air quality and citizen health) interact or interrelate?</h3> <p>[provide the response given if the student answered]</p> <blockquote>[provide the direct passage from the the assignment supporting your analysis]</blockquote> <h3>How do these differ between cities with different characteristics (e.g. population size, exercise levels or modal split)?</h3> <p>[provide the response given if the student answered]</p> <blockquote>[provide the direct passage from the the assignment supporting your analysis]</blockquote> <h3>How does London compare to other cities around the world?</h3>  <p>[provide the response given if the student answered]</p> <blockquote>[provide the direct passage from the the assignment supporting your analysis]</blockquote> <h3>A short opening or closing summary</h3> <p>[provide the response given if the student answered]</p> <blockquote>[provide the direct passage from the the assignment supporting your analysis]</blockquote>{note_assign}\nnote3:direct citation within blockquote should be exactly as it is in the student assignment and the size should be one direct citation sentence for supporting your response",

    f"Evaluate the attached assignment providing responses to the assignment with direct citation in the following format: <h1>Part 2: Informing Policy Decisions</h1> <h2>Q2. Based on the two total expected cost profiles in Figure 1, which of the two air quality mitigation options being considered would you advise the Mayor to go with? Why? [~5%]</h2>  <p>[provide the response given if the student answered]</p> <blockquote>[provide the direct passage from the the assignment supporting your analysis]</blockquote>{note_assign}\nnote3:direct citation within blockquote should be exactly as it is in the student assignment and the size should be one direct citation sentence for supporting your response",

    f"Evaluate the attached assignment providing responses to the assignment with direct citation in the following format: <h2>Q3. The Mayor seems happy and expresses her intent to use the consultants’ analysis to justify her decision. What additional advice might you want to give her before she makes a final decision? [~5%]</h2>  <p>[provide the response given if the student answered]</p> <blockquote>[provide the direct passage from the the assignment supporting your analysis]</blockquote>{note_assign}\nnote3:direct citation within blockquote should be exactly as it is in the student assignment and the size should be one direct citation sentence for supporting your response",

    f"Evaluate the attached assignment providing responses to the assignment with direct citation in the following format: <h2>Q4. You have been asked to provide the mayor with a short text on how the expert advisory board might inform the mayor’s ultimate decision. Your contribution should include: [~15%]</h2> <h3>Advice on the use of the expert advisory board in terms of analysis of policy options, or what not to use it for (i.e. it has been decided that having a board is a desirable thing for public image, but what exactly should they do, instead of e.g. if a citizen forum had been created instead).</h3>  <p>[provide the response given if the student answered]</p> <blockquote>[provide the direct passage from the the assignment supporting your analysis]</blockquote> <h3>Advice on the criteria for selecting the membership of the expert advisory board, including your rationale for how these criteria are relevant to the analytical integrity of the board’s work.</h3> <p>[provide the response with direct quotes if the student answered]</p> <h3>Recommendation for the specific use and role of MCA methods in support the board’s work (note: the Mayor is not asking you to explain the MCA methodology – she is in need of understanding how it can be used to support her upcoming decision making).</h3>  <p>[provide the response given if the student answered]</p> <blockquote>[provide the direct passage from the the assignment supporting your analysis]</blockquote> <p>[provide the response given if the student answered]</p> <blockquote>[provide the direct passage from the the assignment supporting your analysis]</blockquote> <h3>Any further reflections and recommendations on alternative ways that participatory methods and processes could usefully contribute to the analysis informing this air quality enhancement programme you have for the mayor.</h3>  <p>[provide the response given if the student answered]</p> <blockquote>[provide the direct passage from the the assignment supporting your analysis]</blockquote>{note_assign}\nnote3:direct citation within blockquote should be exactly as it is in the student assignment and the size should be one direct citation sentence for supporting your response",

    f"Evaluate the attached assignment providing responses to the assignment with direct citation in the following format: <h2>Q5. You have been asked to provide the mayor with a briefing note with your thoughts on three questions she currently has. Please provide her with a summary of key points you think of greatest relevance: [~25%]</h2> <h3>Embedded values in analysis:</h3> <p>[provide the response with direct quotes if the student answered]</p> <h3>Use of scenarios:</h3> <p>[provide the response with direct quotes if the student answered]</p>{note_assign}\nnote3:direct citation within blockquote should be exactly as it is in the student assignment and the size should be one direct citation sentence for supporting your response"
]

Marking = [
    f"""Evaluate the attached assignment providing marking and explanations. The marking scheme is in the UK is: lower second class: satisfactory>50-52, fair>53-55, good>56-59, upper second class satisfactory>60-62, good>63-65, very good>66-69, first class:good>70-74 very good>75-79. The rubric is in the following format: 
    <h1>Marking (Total: [total score])</h1>
    <h1>Part 1: Exploratory Data Analysis (Total: [total score])</h1>  
    <h2>Conceptual Understanding (40%)</h2>  
    <h3>Marking: [marking score]</h3> 
    <h3>Explanation</h3> :
    <p>[explain with at least 3 examples why the assignment got the marking score]</p>
    <blockquote>[direct quote from the assignment to support the explanation]</blockquote>
    <h2>Reasoning & Critical Analysis (40%)</h2>
    <h3>Marking: [marking score]</h3>
    <h3>Explanation</h3> :
    <p>[explain with at least 3 examples why the assignment got the marking score]</p>
    <blockquote>[direct quote from the assignment to support the explanation]</blockquote>
    <h2>Communication, Structure and Clarity (20%)</h2>
    <h3>Marking: [marking score]</h3>
    <h3>Explanation</h3> :
    <p>[explain with at least 3 examples why the assignment got the marking score]</p>
    <blockquote>[direct quote from the assignment to support the explanation]</blockquote>{note_assign}\nnote3:direct citation within blockquote should be exactly as it is in the student assignment and the size should be one direct citation sentence by explanation. """,

    f"""Evaluate the attached assignment providing marking and explanations in the following format:

    <h1>Marking (Total: [total score])</h1>
    <h1>Part 2: Informing Policy Decisions (Total: [total score])</h1>
    <h2>Conceptual Understanding (40%)</h2>
    <h3>Marking: [marking score]</h3>
    <h3>Explanation</h3> :
    <p>[explain with at least 3 examples why the assignment got the marking score]</p>
    <blockquote>[direct quote from the assignment to support the explanation]</blockquote>
    <h2>Reasoning & Critical Analysis (40%)</h3>
    <h3>Marking: [marking score]</h3>
    <h3>Explanation</h3> :
    <p>[explain with at least 3 examples why the assignment got the marking score]</p>
    <blockquote>[direct quote from the assignment to support the explanation]</blockquote>
    <h2>Communication, Structure and Clarity (20%)</h2>
    <h3>Marking: [marking score]</h3>
    <h3>Explanation</h3> :
    <p>[explain with at least 3 examples why the assignment got the marking score]</p>
    <blockquote>[direct quote from the assignment to support the explanation]</blockquote>{note_assign}\nnote3:direct citation within blockquote should be exactly as it is in the student assignment and the size should be one direct citation sentence by explanation."""
]



feedback_guidelines = [f"""Feedback for Part A:
You are tasked with evaluating the student's assignment on exploratory data analysis (EDA) concerning air quality and citizen health. Your feedback should be detailed, specific, directly tied to the student's submission, not exceed 250 words, and match the style from the provided feedback examples document. Follow the structured feedback format below, ensuring to cite relevant parts of the assignment. Avoid generic comments and focus on the content provided. Know that the first document is the student assignment entitled anonymous. Read the later line by line before providing feedback. the second  is the Assignment Feedback Summary document containing positive feedback and recommendations which serves as a reference for you.

**Assignment Expectations and Feedback Points:**

**What was asked:**
- Undertake exploratory data analysis (EDA) with a broad topic: briefing the mayor on the relationship between air quality and citizen health to lead a global policy knowledge community.
- Report key findings and considerations for the mayor, including key aspects of how the EDA generated those findings.
- Include a discussion of how London compares to other cities around the world.
- Discuss how air quality and health interact and differ between cities with different characteristics (e.g., population size, exercise levels, or modal split).

**Guidelines for Specific Feedback:**
- Focus on the student's responses to the key questions and the assignment rubric.
- If the student does not explore the mayor’s stated interest in air quality and citizen health or comparison with other cities or regions, note this and advise them to always be guided by the intended uses of their work. Where not feasible, they should clarify why.

**Intended Learning Reinforcement:**
- Understand the iterative approach of exploratory analysis.
- Recognize the role of multiple data types/sources and/or methods in eliciting ‘information’ from ‘data’.
- Demonstrate use of analytic methods introduced throughout the course.
- Understand the importance of clearly labeling analysis and figures and reporting sources/types of uncertainty.
- Appreciate the significance of individual judgment in appraising the relevance of the reported analysis.
- Use visualization to effectively communicate analytic insights.

**Feedback Structure:**

<h1> Feedback:[total marking score here]</h1>
**Positive Feedback and Recommendations:**
- Use the "Assignment Feedback Summary" document to provide specific positive feedback and recommendations.
- Select appropriate points from the summary document to integrate into your feedback based on the student's work.
- Ensure the positive feedback highlights strengths related to the assignment guidelines and the recommendations are actionable and clear.
return two paragraphs in the following format:
<p>For part A,[Insert positive feedback from the summary document that aligns with the student's work with 250 words as a limit.this paragraph should be stricly related to the assingment and every key point should be supported with direct quotes as stated below. it should contain highest accucary.]:</p>
<blockquote>[direct quote from the assignment to support the  Positive Feedback]</blockquote>
<p>[Insert recommendations from the summary document that are relevant to the student's work.this paragraph should be stricly related to the assingment and every recommendatoin should be supported with direct quotes with the passage in the assingment that triggers it. it should contain highest accucary.]:</p>
<blockquote>[direct quote from the assignment to support the need for Recommendations ]</blockquote>
before returning the two paragraphs, check accuracy to make sure that every fact stated is consistent with the assigment. For example, it should not be stated a type of analysis, if not found in the assingment. similarly, it should not recommended something if weekness not observed in the assignment.
{note_assign}\nnote3:direct citation within blockquote should be exactly as it is in the student assignment and the size should be one direct citation sentence. \nnote4: make sure that positive and recommendations are tailored specifically to my assignment and are not general, but specific for me to acknowledge whaat I did well and how/where to improve.""",
f"""Feedback for Part B:
You are tasked with evaluating the student's assignment on informing policy decisions concerning air quality and citizen health. Your feedback should be detailed, specific, directly tied to the student's submission, not exceed 250 words, and match the style from the provided feedback examples document. Follow the structured feedback format below, ensuring to cite relevant parts of the assignment. Avoid generic comments and focus on the content provided. Know that the first document is  the student assignment entitled anonymous. Read the later line by line before providing feedback. the second is the Assignment Feedback Summary document containing positive feedback and recommendations.

**Assignment Expectations and Feedback Points:**

**What was asked:**
- Evaluate two air quality mitigation options and provide recommendations to the mayor.
- Address additional advice the mayor might need before making a final decision.
- Provide a detailed analysis of the expert advisory board's role in informing the mayor’s decision.
- Offer a summary of key points regarding embedded values in analysis, use of scenarios, and other relevant considerations.

**Guidelines for Specific Feedback:**
- Ensure the student addresses all parts of the questions comprehensively.
- Provide specific examples and cite relevant parts of the assignment to support your feedback.
- Offer constructive criticism to guide improvements in future assignments.

**Intended Learning Reinforcement:**
- Use and reflect upon multiple analytic methods.
- Judge the suitability of analytic methods used for analysis.
- Design and undertake an analytic process to inform complex decisions (consider participatory value and exploration of uncertainties).
return two paragraphs in the following format:

<p>For part B,[Insert positive feedback from the summary document that aligns with the student's work with 250 words as a limit.this paragraph should be stricly related to the assingment and every key point should be supported with direct quotes as stated below. it should contain highest accucary.]:</p>
<blockquote>[direct quote from the assignment to support the  Positive Feedback]</blockquote>
<p>[Insert recommendations from the summary document that are relevant to the student's work.this paragraph should be stricly related to the assingment and every recommendatoin should be supported with direct quotes with the passage in the assingment that triggers it. it should contain highest accucary.]:</p>
<blockquote>[direct quote from the assignment to support the need for Recommendations ]</blockquote>
before returning the two paragraphs, check accuracy to make sure that every fact stated is consistent with the assigment. For example, it should not be stated a type of analysis, if not found in the assingment. similarly, it should not recommended something if weekness not observed in the assignment.
{note_assign}\nnote3:direct citation within blockquote should be exactly as it is in the student assignment and the size should be one direct citation sentence. \nnote4: make sure that positive and recommendations are tailored specifically to my assignment and are not general, but specific for me to acknowledge what I did well and where/how to improve."""]



initial_prompt =' Your response should always be formatted in HTML block code with no exception. '




stop_words = """
 [
    "intricacies",
    "complexities",
    "nuance",
    "sophisticated",
    "multifaceted",
    "complicated",
    "intricate",
    "complex",
    "nuanced",
    "sophistication",
    "comprehensive",
    "dynamic",
    "innovative",
    "advanced",
    "challenging",
    "revolutionary",
    "cutting-edge",
    "pioneering",
    "state-of-the-art",
    "groundbreaking",
    "meticulous",
    "rigorous",
    "exhaustive",
    "in-depth",
    "thorough",
    "detailed",
    "elaborate",
    "extensive"
]

"""
note="the output should be complete with no placeholders or comments for instance '<!-- Additional sections and subsections follow the same structure -->'. provide the whole detailed structure\noutput:HTML in a code block."
initial_book =f"Instructions:Please create a book divided into 5 chapters. Each chapter should include 3 sections, and each section should consist of 3 subsections. The subsections should be structured to include placeholders for content, represented by f-string placeholders like '{{}}'. Please format the response in a HTML div structure.\n\nExample:\n<div><h1>[Book Title]</h1><div><h2>Chapter {{}}: [Chapter Title]</h2><p>[Chapter Overview]</p><div><h3>Section {{}}: [Section Title]</h3><p>[Section Overview]</p><div><h4>Subsection {{}}: [Subsection Title]</h4><p>[Detailed Content]</p></div></div></div></div></div>{note}"
book_titles = [
  {"title": "Cyber-Diplomacy: The New Frontier in International Relations", "references": ["Andrew N. Liaropoulos (2017)", "Milton L. Mueller (2020)", "A. Aydin, Türksel Kaya Bensghir (2019)", "S. Korostelev (2020)", "D. Antonov (2022)"]},
  {"title": "The Architecture of Cyber Security: International Law Perspectives", "references": ["Eneken Tikk-Ringas (2015)", "Laurie R. Blank (2012)", "K. Mačák (2016)", "Vanshika Shukla (2023)", "Sean Kanuck (2010)"]},
  {"title": "Digital Sovereignty: Cyberspace and State Power", "references": ["Liudmila Terentieva (2021)", "Andrew N. Liaropoulos (2017)", "Milton L. Mueller (2020)", "A. Aydin, Türksel Kaya Bensghir (2019)", "S. Korostelev (2020)"]},
  {"title": "Global Cyber Conflicts: Securing the 5th Domain", "references": ["T. Tuukkanen (2011)", "R. Darby (2012)", "A. Kosenkov (2016)", "Jerónimo Domínguez-Bascoy, Bartolomé Bauzá-Abril (2017)", "Ehab Khalifa (2021)"]}
]

book=[
  {
    "type": "chapter",
    "prompt": f"Outline the chapter, focusing on its: 1. research problem, 2.key research questions, and 3. hypothesis in prose. Provide a compelling introduction that encourages further reading.\nExample:\n<div><h2>Chapter [Chapter Number]: [Chapter Title]</h2><p>[1. research problem, 2.key research questions, and 3. hypothesis in prose]</p></div>{note}"
  },
  {
    "type": "section",
    "prompt": f"Introduce the section by detailing the specific aspect of the chapter's theme it will explore. Mention its importance and what readers can expect to learn from it.\n\nExample:\n<div><h3>[Section Number]: [Section Title]</h3><p>[Provide a detailed introduction to this section, explaining the specific aspects of the chapter's theme it will explore. Highlight its importance and what new knowledge or insights readers can expect to gain.]</p></div>{note}"
  },
  {
    "type": "subsection",
    "prompt": f"Dive into the details of the subsection’s topic. Provide thorough explanations, examples, or analyses that enrich the reader's understanding of the section's overall theme.\n\nExample:\n<div><h4>Subsection {{}}: [Subsection Title]</h4><p>[Delve into the details of this subsection's topic. Provide in-depth explanations, relevant examples, and thorough analyses to enrich the reader's understanding. Explain how this subsection contributes to the section's and chapter's themes.]</p></div>{note}"
  }
]

