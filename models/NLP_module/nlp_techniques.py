import ast

# Sample text data
texts = [
    "Natural language processing is a field of artificial intelligence that deals with the interaction between computers and humans through natural language.",
    "Machine learning is the scientific study of algorithms and statistical models that computer systems use to perform a specific task without using explicit instructions.",
    "Deep learning is a subset of machine learning in artificial intelligence that has networks capable of learning unsupervised from data that is unstructured or unlabeled.",
    "Computer vision is an interdisciplinary field that deals with how computers can gain high-level understanding from digital images or videos.",
    "Reinforcement learning is an area of machine learning concerned with how software agents ought to take actions in an environment to maximize some notion of cumulative reward."
]

from collections import Counter


def analyze_keywords_comprehensive(top_n=20, unique_threshold=1):
    """
    Comprehensive analysis of keywords including frequency, categorization,
    thematic analysis, visualization, and deep analysis using OpenAI GPT.

    Parameters:
    - keywords (list): List of keyword strings.
    - top_n (int): Number of top frequent keywords to return.
    - unique_threshold (int): Frequency threshold to consider a keyword as unique.

    Returns:
    - summary (dict): Dictionary containing top keywords, unique keywords,
                      category distribution, theme distribution, and deep analysis.
    - Displays interactive Plotly charts.
    """
    with open(r"/Files/Cache/keyowrds.txt", "r", encoding="utf-8") as f:
        keywords= ast.literal_eval(f.read())
    # 1. Preprocessing: Normalize keywords to lowercase
    normalized_keywords = [kw.lower().strip() for kw in keywords]

    # 2. Keyword Frequency Analysis
    keyword_counts = Counter(normalized_keywords)

    # 3. Top N Keywords
    top_keywords = keyword_counts.most_common(top_n)

    # 4. Unique Keywords (frequency <= unique_threshold)
    unique_keywords = [kw for kw, count in keyword_counts.items() if count <= unique_threshold]

    # 5. Categorization using OpenAI
    # categories = categorize_keywords_openai(normalized_keywords)

    # 6. Thematic Analysis using OpenAI
    # themes = identify_themes_openai(categories)
    #
    # # 7. Visualization with Plotly
    # visualize_analysis(top_keywords, unique_keywords, categories, themes)
    #
    # # 8. Deep Analysis using OpenAI
    # deep_analysis = generate_deep_analysis(keyword_counts, categories, themes, top_keywords)
    #
    # # 9. Summary Compilation
    summary = {
        'Top Keywords': top_keywords,
        'Unique Keywords': unique_keywords,
        # 'Category Distribution': categories['category_counts'],
        # 'Theme Distribution': themes['theme_counts'],
        # 'Deep Analysis': deep_analysis
    }

    return summary

# def categorize_keywords_openai(keywords):
#     """
#     Categorizes keywords into predefined or dynamically generated categories
#     using OpenAI's GPT.
#
#     Parameters:
#     - keywords (list): List of normalized keyword strings.
#
#     Returns:
#     - dict: Dictionary containing category assignments and counts.
#     """
#
#     # Define initial prompt for categorization
#     prompt = """
#             I have a list of keywords related to international law, cyber operations, and related fields.
#             Categorize each keyword into one of the following categories: Organizations, People, Legal Concepts, Cyber Terms, Mechanisms, Other.
#             Provide the categorization in a JSON format with each keyword mapped to its category.
#
#             Keywords:
#             {}
#
#             Example Output:
#             {
#                 "keyword1": "Category1",
#                 "keyword2": "Category2",
#                 ...
#             } """.format(", ".join(keywords[:100]))  # Limit to first 100 keywords for prompt size
#
#     # Handle large keyword lists by processing in batches
#     keyword_categories = {}
#     batch_size = 100  # Adjust based on OpenAI's token limits
#
#     for i in range(0, len(keywords), batch_size):
#         batch = keywords[i:i+batch_size]
#         prompt = f"""
#         I have a list of keywords related to international law, cyber operations, and related fields.
#         Categorize each keyword into one of the following categories: Organizations, People, Legal Concepts, Cyber Terms, Mechanisms, Other.
#         Provide the categorization in a JSON format with each keyword mapped to its category.
#
#         Keywords:
#         {", ".join(batch)}
#
#         Example Output:
#         {{
#             "keyword1": "Category1",
#             "keyword2": "Category2",
#             ...
#         }}
#         """
#
#         try:
#             response = call_openai_api(data=prompt,function=)
#             result = response['choices'][0]['message']['content']
#             # Attempt to parse JSON from response
#             parsed = eval(result)  # Note: Using eval can be risky; ensure trusted input
#             keyword_categories.update(parsed)
#         except Exception as e:
#             print(f"Error during categorization with OpenAI: {e}")
#             # Assign 'Other' category in case of error
#             for kw in batch:
#                 keyword_categories[kw] = 'Other'
#
#     # Count categories
#     category_counts = Counter(keyword_categories.values())
#
#     return {
#         'keyword_categories': keyword_categories,
#         'category_counts': category_counts
#     }

# def identify_themes_openai(categorization):
#     """
#     Identifies overarching themes based on categorized keywords using OpenAI's GPT.
#
#     Parameters:
#     - categorization (dict): Dictionary containing keyword to category mappings.
#
#     Returns:
#     - dict: Dictionary containing themes and their associated keyword counts.
#     """
#
#     # Extract keywords grouped by categories
#     categories = categorization['keyword_categories']
#     category_groups = {}
#     for kw, cat in categories.items():
#         category_groups.setdefault(cat, []).append(kw)
#
#     # Prepare prompt for theme identification
#     prompt = """
#     Based on the following categorized keywords, identify 5 overarching themes that encapsulate the main topics.
#     Provide the themes and list the keywords that belong to each theme in a JSON format.
#
#     Categories and Keywords:
#     {}
#
#     Example Output:
#     {{
#         "Theme1": ["keyword1", "keyword2", ...],
#         "Theme2": ["keyword3", "keyword4", ...],
#         ...
#     }}
#     """.format("\n".join([f"{cat}: {', '.join(kws[:10])}" for cat, kws in category_groups.items()]))
#
#     try:
#         response = openai.ChatCompletion.create(
#             model="gpt-4",
#             messages=[
#                 {"role": "system", "content": "You are a helpful assistant for identifying themes based on categorized keywords."},
#                 {"role": "user", "content": prompt}
#             ],
#             temperature=0.5,
#             max_tokens=600
#         )
#         result = response['choices'][0]['message']['content']
#         # Attempt to parse JSON from response
#         themes = eval(result)  # Note: Using eval can be risky; ensure trusted input
#     except Exception as e:
#         print(f"Error during theme identification with OpenAI: {e}")
#         themes = {}
#
#     # Count themes
#     theme_counts = {}
#     for theme, kws in themes.items():
#         theme_counts[theme] = len(kws)
#
#     return {
#         'themes': themes,
#         'theme_counts': theme_counts
#     }
#
# def visualize_analysis(top_keywords, unique_keywords, categories, themes):
#     """
#     Generates interactive Plotly visualizations for the keyword analysis.
#
#     Parameters:
#     - top_keywords (list): List of tuples containing top keywords and their counts.
#     - unique_keywords (list): List of unique keywords.
#     - categories (dict): Dictionary containing category counts.
#     - themes (dict): Dictionary containing theme counts.
#     """
#
#     # a. Top Keywords Bar Chart
#     if top_keywords:
#         df_top = pd.DataFrame(top_keywords, columns=['Keyword', 'Frequency'])
#         fig_top = px.bar(
#             df_top,
#             x='Keyword',
#             y='Frequency',
#             title='Top 10 Keywords',
#             text='Frequency',
#             color='Frequency',
#             color_continuous_scale='Viridis'
#         )
#         fig_top.update_traces(textposition='outside')
#         fig_top.update_layout(uniformtext_minsize=8, uniformtext_mode='hide')
#         fig_top.show()
#     else:
#         print("No top keywords to display.")
#
#     # b. Unique Keywords Bar Chart
#     if unique_keywords:
#         df_unique = pd.DataFrame(unique_keywords, columns=['Unique Keywords'])
#         fig_unique = px.bar(
#             df_unique,
#             x='Unique Keywords',
#             title='Unique Keywords (Frequency <= 1)',
#             labels={'Unique Keywords': 'Keywords'},
#             text='Unique Keywords'
#         )
#         fig_unique.update_traces(textposition='outside')
#         fig_unique.update_layout(showlegend=False)
#         fig_unique.show()
#     else:
#         print("No unique keywords to display.")
#
#     # c. Category Distribution Pie Chart
#     if categories['category_counts']:
#         df_cat = pd.DataFrame(list(categories['category_counts'].items()), columns=['Category', 'Count'])
#         fig_cat = px.pie(
#             df_cat,
#             names='Category',
#             values='Count',
#             title='Category Distribution',
#             hole=0.4
#         )
#         fig_cat.update_traces(textposition='inside', textinfo='percent+label')
#         fig_cat.show()
#     else:
#         print("No category distribution to display.")
#
#     # d. Theme Distribution Bar Chart
#     if themes['theme_counts']:
#         df_theme = pd.DataFrame(list(themes['theme_counts'].items()), columns=['Theme', 'Count'])
#         fig_theme = px.bar(
#             df_theme,
#             x='Theme',
#             y='Count',
#             title='Theme Distribution',
#             text='Count',
#             color='Count',
#             color_continuous_scale='Cividis'
#         )
#         fig_theme.update_traces(textposition='outside')
#         fig_theme.update_layout(uniformtext_minsize=8, uniformtext_mode='hide')
#         fig_theme.show()
#     else:
#         print("No theme distribution to display.")
#
# def generate_deep_analysis(keyword_counts, categories, themes, top_keywords):
#     """
#     Generates a deep analysis report based on the keyword statistics,
#     categories, and themes using OpenAI's GPT.
#
#     Parameters:
#     - keyword_counts (Counter): Counter object with keyword frequencies.
#     - categories (dict): Dictionary containing category counts.
#     - themes (dict): Dictionary containing theme counts.
#     - top_keywords (list): List of tuples containing top keywords and their counts.
#
#     Returns:
#     - str: Deep analysis report.
#     """
#
#     # Prepare data for the prompt
#     top_kw_str = "\n".join([f"{kw.capitalize()}: {count}" for kw, count in top_keywords])
#     category_str = "\n".join([f"{cat}: {count}" for cat, count in categories['category_counts'].items()])
#     theme_str = "\n".join([f"{theme}: {count}" for theme, count in themes['theme_counts'].items()])
#
#     prompt = f"""
#     Based on the following keyword analysis, provide a comprehensive deep analysis report.
#
#     **Top 10 Keywords:**
#     {top_kw_str}
#
#     **Category Distribution:**
#     {category_str}
#
#     **Theme Distribution:**
#     {theme_str}
#
#     **Unique Keywords:**
#     {', '.join([kw for kw, count in keyword_counts.items() if count <=1])[:500]}  # Limit to first 500 characters
#
#     **Instructions:**
#     - Analyze the significance of the top keywords.
#     - Discuss the distribution across categories and what it indicates.
#     - Elaborate on the identified themes and their implications.
#     - Highlight any notable patterns, trends, or anomalies.
#     - Provide insights or recommendations based on the analysis.
#
#     **Output:**
#     """
#
#     try:
#         response = openai.ChatCompletion.create(
#             model="gpt-4",
#             messages=[
#                 {"role": "system", "content": "You are a knowledgeable analyst."},
#                 {"role": "user", "content": prompt}
#             ],
#             temperature=0.7,
#             max_tokens=1000
#         )
#         analysis = response['choices'][0]['message']['content']
#     except Exception as e:
#         print(f"Error during deep analysis with OpenAI: {e}")
#         analysis = "Deep analysis could not be generated due to an error."
#
#     return analysis

from difflib import SequenceMatcher


def get_words(lst):
    """
    This function breaks down each element of the list into individual words
    and returns a set of all the words in lowercase.
    """
    return set(word.lower() for item in lst for word in item.split())


def similar(a, b, threshold=0.7):
    """
    This function compares two strings and returns True if they are similar
    based on a given threshold, otherwise False.
    """
    return SequenceMatcher(None, a.lower(), b.lower()).ratio() > threshold


def lists_have_common_words(list1, list2):
    """
    This function checks if the two lists have any common words or similar phrases.
    Returns True if a match is found, otherwise False.
    """
    words_list1 = get_words(list1)
    words_list2 = get_words(list2)

    # Check for any exact word match
    common_words = words_list1 & words_list2
    if common_words:
        return True

    # Check for similarity between individual elements
    for item1 in list1:
        for item2 in list2:
            if similar(item1, item2):
                return True

    return False