import json
import urllib.parse
import re
from bs4 import BeautifulSoup


def convert_zotero_to_md_with_id(html_paragraph, item_id, keywords,paragraph_id):
    # Decode the HTML-encoded string
    decoded_paragraph = urllib.parse.unquote(html_paragraph)

    # Parse the HTML with BeautifulSoup
    soup = BeautifulSoup(decoded_paragraph, 'html.parser')

    # Extract the text from the paragraph, removing tags like blockquote and span
    paragraph_text = soup.get_text(strip=True)

    # Extract citation details from span.citation
    citation_span = soup.find('span', class_='citation-item')
    if citation_span:
        citation_text = citation_span.get_text(strip=True)
        # Find the pattern like "Author, Year, p. Page"
        author_year_match = re.search(r'(.*?), (\d{4}), p\. (\d+)', citation_text)
        if author_year_match:
            author = author_year_match.group(1)
            year = author_year_match.group(2)
            page_number = author_year_match.group(3)
        else:
            author = "Unknown author"
            year = "Unknown year"
            page_number = "Unknown page"
    else:
        author = "Unknown author"
        year = "Unknown year"
        page_number = "Unknown page"

    # Format the APA reference with a clickable Zotero link
    apa_reference = f"([{author}, {year}, p. {page_number}](zotero://select/library/items/{item_id}))"

    # Replace the citation pattern (author, year, page) in the text
    citation_pattern = re.escape(f"({author}, {year}, p. {page_number})")
    paragraph_text = re.sub(citation_pattern, '', paragraph_text).strip()

    # Combine the paragraph text and citation in the desired markdown format
    md_output = f'<div id="{paragraph_id}">\n\n> [!quote] \n>{paragraph_text}{apa_reference}\n^{paragraph_id}\n\n> [!info]\n> **Keywords:** {keywords}\n</div>'

    return md_output

def insert_callout(type):
    callout_types = {
        "note": ["note", "seealso"],
        "abstract": ["abstract", "summary", "tldr"],
        "info": ["info", "todo"],
        "tip": ["tip", "hint", "important"],
        "success": ["success", "check", "done"],
        "question": ["question", "help", "faq"],
        "warning": ["warning", "caution", "attention"],
        "failure": ["failure", "fail", "missing"],
        "danger": ["danger", "error"],
        "bug": ["bug"],
        "example": ["example"],
        "quote": ["quote", "cite"]
    }
    return callout_types.get(type, "Type not supported")

def add_aliases(note_name, aliases_list):
    aliases_dict = {
        note_name: aliases_list
    }
    return aliases_dict

# Example usage

def embed_file(file_name, embed_type="note", options=None):
    embeds = {
        "note": f"![[{file_name}]]",
        "image": f"![[{file_name}|{options['width']}x{options['height']}]]" if options else f"![[{file_name}]]",
        "pdf": f"![[{file_name}#page={options['page']}]]" if options and "page" in options else f"![[{file_name}]]",
        "audio": f"![[{file_name}]]"
    }
    return embeds.get(embed_type, "Embed type not supported")

# Example usage
def create_internal_link(note_title, display_text=None, heading=None, block_id=None):
    if heading:
        return f"[[{note_title}#{heading}|{display_text}]]" if display_text else f"[[{note_title}#{heading}]]"
    elif block_id:
        return f"[[{note_title}#^{block_id}|{display_text}]]" if display_text else f"[[{note_title}#^{block_id}]]"
    else:
        return f"[[{note_title}|{display_text}]]" if display_text else f"[[{note_title}]]"

# Example usage
def create_external_link(link_url, display_text=None):
    if display_text:
        return f"[{display_text}]({link_url})"
    else:
        return f"[{link_url}]"

# Example usage
def create_task_list(tasks):
    task_list = ""
    for task in tasks:
        task_list += f"- [{'x' if task['completed'] else ' '}] {task['name']}\n"
    return task_list

def embed_search_results(query):
    return f"```query\n{query}\n```"

# Example usage
def create_table(headers, rows):
    table = "| " + " | ".join(headers) + " |\n"
    table += "| " + " | ".join(["---"] * len(headers)) + " |\n"
    for row in rows:
        table += "| " + " | ".join(row) + " |\n"
    return table

