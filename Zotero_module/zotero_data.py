
# note= "\nNote:\n Focus on direct information from the article but if indirect evidence is found, provide an interpretation based on the above instructions and the paper content. if no relevant information is found, return a None div. output:HTML div in a code block"
note= "Take your time, review the final output for accuracy and consistency in HTML formatting and citation-context alignment.\n\nnote1:Direct quotes format must be in form of one full sentence. The full sentence must be exactly as it is in the document, strictly unmodified. before getting it, check if there is a full match in the sentence and the word text. After getting the exacly quote that supports you analysis, reference with the author name between () like (author)\nnote:2output format:html in a code block."
note_assign= "Take your time, review the final output for accuracy and consistency in HTML formatting and citation-context alignment.\n \nnote1: output format:html in one single code block.\nnote2:Act like a Professor talking to the student, then use the second person(You demonstrate) instead of third(the student demonstrates). "
summary_note = "\nnote:1 do not write additional information, all the information must be found and referenced in the document, if no reference is found, skip the task and go to the next.\nnote 2: follow the citation apa format:author,year,page. author and year was already provided, you should identify the page.\nnote3:output format: code block html```"



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
        # "<h2>1.5 Structure and Keywords</h2>": [
        #     "Guidelines: 1. Analyze the Document: Extract the Table of Contents (TOC) using common formatting cues in academic papers. 2. Formatting Cues: Look for numbered headings (e.g., 1, 2, 3; 1.1, 1.2; A., B., C...), bold, italic, or larger font sizes. Main headings are usually larger and left-aligned, subheadings might be indented. 3. Verify Accuracy: Cross-reference with the document. 4. HTML Output Example: Provide the TOC in the following HTML format: <h3>TOC:</h3><ul><li>[Main Heading 1]</li><li>[Main Heading 1: Subheading 1.1]</li><li>[Main Heading 1: Subheading 1.2]</li><li>[Main Heading 1: Subheading 1.2: subheading 1.2.1]</li><!-- Additional headings and subheadings as found --></ul>. For headings, use: <li>Main Heading</li>. For subheadings, use: <li>Main Heading: Subheading</li>. if more than one subheadings, continue with main:subheading:subheading:subheading.  Ensure the TOC titles  accurately reflects the structure of the document and subheadings are preceded by its parents headings separated by ':'.\noutput format: code block html```",
        #     "Guidelines: Analyze the document and extract: 1. Bibliographic information: <h4> Bibliographical Information</h4><ul> <li>Citation style: [analyse the whole document and search for intext citations. if numerical citations like \"cyberspace can be dangerous5\" are found return here numerical. if APA style like author year (Smith, 2022), return APA]</li> <li>Bibliographic position: [In-text or End]</li> </ul> 2. Academic fields (list three primary disciplines with at least two of each): <h4>Academic Fields</h4><ul> <li>Field: [Field found in the article]</li> <li>Research area: [Research area found in the article]</li> </ul> 3. Topics (list up to seven themes, each up to four words): <h4>Themes and Topics:</h4> <ul> <li>Topic: [Theme or Topic found in the article, list up to seven themes, each up to four words]</li> </ul> 4. Research information: <h4>Research information</h4><ul> <li>Research type: [The research type, e.g., Qualitative, Quantitative, Mixed Methods, Experimental, Longitudinal]</li> <li>Research design: [The research design, e.g., Treaty Analysis, Comparative Policy Analysis, Normative Legal Analysis]</li> <li>Data type: [The data type found in the text]</li> 5. Data Collection Methods:<h4>Data Collection Methods</h4> <li>Method:[Method used by the author, e.g., Archival Research, Structured Interviews, Policy Review. If more than one method, create another list in the same format data collection method[method]]</li> </ul>note1 . [] are commands, do not print []. note 2 output in a code block"

# ]
    }

note_api = [
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

