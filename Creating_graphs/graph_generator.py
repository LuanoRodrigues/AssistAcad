import ast
import json

import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
from scipy.cluster.hierarchy import dendrogram, linkage
import plotly.graph_objects as go
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import plotly.express as px
from collections import Counter
import pandas as pd
from scipy.stats import zscore

# # Load data
# with open(r"C:\Users\luano\Downloads\AcAssitant\Files\Cache\keywords.txt", encoding="utf-8") as net:
#     keywords = ast.literal_eval(net.read())
#
# with open(r"C:\Users\luano\Downloads\AcAssitant\Files\Cache\keywords_categorised.json", encoding="utf-8") as net2:
#     categories_keywords= json.load(net2)
output_folder = r"C:\Users\luano\Downloads\AcAssitant\Files\Keywords_Canvas"
#
#
# keywords_counts = Counter([kw.lower() for kw in keywords])
# print(keywords_counts)
# print(keyword_counts.most_common(1200))
keywords=""
categories_keywords= ""

def plot_word_frequency():
    """
    Plots a vertical bar chart of the top 100 word frequencies.
    """
    words = [word.lower() for word in keywords]
    word_counts = Counter(words)
    df = pd.DataFrame(word_counts.items(), columns=['Word', 'Frequency']).sort_values(by='Frequency', ascending=False)
    df = df.head(100)  # Select top 100 words

    fig = px.bar(df, x='Word', y='Frequency', title='Top 100 Word Frequencies', orientation='v',
                 labels={'Word': 'Word', 'Frequency': 'Frequency'})
    fig.update_layout(xaxis_tickangle=-90, xaxis={'categoryorder':'total descending'})
    fig.write_html(f'{output_folder}\\word_frequency.html')

def plot_treemap():
    """
    Plots a treemap of the top 100 word frequencies.
    """
    words = [word.lower() for word in keywords]
    word_counts = Counter(words)
    df = pd.DataFrame(word_counts.items(), columns=['Word', 'Frequency']).sort_values(by='Frequency', ascending=False)
    df = df.head(100)  # Select top 100 words

    fig = px.treemap(df, path=['Word'], values='Frequency', title='Treemap of Top 100 Word Frequencies',
                     labels={'Word': 'Word', 'Frequency': 'Frequency'})
    fig.write_html(f'{output_folder}\\treemap.html')

def plot_pie_chart():
    """
    Plots a pie chart of the top 10 word frequencies.
    """
    words = [word.lower() for word in keywords]
    word_counts = Counter(words)
    df = pd.DataFrame(word_counts.items(), columns=['Word', 'Frequency']).sort_values(by='Frequency', ascending=False)
    df = df.head(10)  # Pie charts work best with a small number of categories

    fig = px.pie(df, names='Word', values='Frequency', title='Pie Chart of Top 10 Word Frequencies',
                 labels={'Word': 'Word', 'Frequency': 'Frequency'})
    fig.write_html(f'{output_folder}\\pie_chart.html')




def plot_line_distribution():
    """
    Plots a line graph of word frequency distribution after removing outliers.
    Corrects the axes to accurately represent the data.
    """
    words = [word.lower() for word in keywords]
    word_counts = Counter(words)
    df = pd.DataFrame(word_counts.items(), columns=['Word', 'Frequency'])

    # Sort by frequency descending and reset index for plotting
    df_sorted = df.sort_values(by='Frequency', ascending=False).reset_index(drop=True)

    # Calculate z-scores and filter out outliers
    df_sorted['Z-Score'] = zscore(df_sorted['Frequency'])
    df_filtered = df_sorted[(df_sorted['Z-Score'] > -3) & (df_sorted['Z-Score'] < 3)]  # Keeping data within 3 standard deviations

    # Plotting the line distribution with correct axes
    fig = px.line(df_filtered, x=df_filtered.index + 1, y='Frequency', title='Word Frequency Distribution (Filtered)',
                  labels={'x': 'Word Rank', 'Frequency': 'Frequency'})
    fig.write_html(f'{output_folder}\\line_distribution.html')

def plot_pareto_chart():
    """
    Plots a Pareto chart of the top 100 words.
    A Pareto chart combines a bar chart with a line graph showing cumulative percentages.
    """
    words = [word.lower() for word in keywords]
    word_counts = Counter(words)
    df = pd.DataFrame(word_counts.items(), columns=['Word', 'Frequency']).sort_values(by='Frequency', ascending=False)
    df = df.head(100)  # Select top 100 words

    df['Cumulative Frequency'] = df['Frequency'].cumsum()
    df['Cumulative Percentage'] = 100 * df['Cumulative Frequency'] / df['Frequency'].sum()

    fig = go.Figure()

    # Bar chart for frequencies
    fig.add_trace(go.Bar(x=df['Word'], y=df['Frequency'], name='Frequency', marker_color='lightskyblue'))

    # Line for cumulative percentage
    fig.add_trace(go.Scatter(x=df['Word'], y=df['Cumulative Percentage'], name='Cumulative Percentage',
                             yaxis='y2', mode='lines+markers', line=dict(color='firebrick')))
    fig.write_html(f'{output_folder}\\pareto_chart.html')

    # Create axis objects
    fig.update_layout(
        title='Pareto Chart of Top 100 Word Frequencies',
        xaxis=dict(tickangle=-90, title='Word'),
        yaxis=dict(title='Frequency'),
        yaxis2=dict(title='Cumulative Percentage', overlaying='y', side='right', range=[0, 100]),
        legend=dict(x=0.01, y=0.99, bgcolor='rgba(255,255,255,0)', bordercolor='rgba(255,255,255,0)'),
        margin=dict(b=200)  # Increase bottom margin to accommodate rotated x-axis labels
    )

    fig.write_html(f'{output_folder}\\pareto_chart.html')


def plot_wordcloud():
    """
    Generates and saves a word cloud of the top 100 words.
    """
    words = [word.lower() for word in keywords]
    word_counts = Counter(words)
    top_words = dict(word_counts.most_common(100))  # Top 100 words

    wordcloud = WordCloud(width=1600, height=800, background_color='white').generate_from_frequencies(top_words)

    plt.figure(figsize=(20, 10))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    plt.tight_layout(pad=0)
    plt.savefig(f'{output_folder}\\word_cloud.png', bbox_inches='tight')
    plt.close()




# 1. Interactive Tree Map using Plotly
def create_treemap(categories_keywords, keywords_counts):
    """
    Creates an interactive Tree Map using Plotly.

    Parameters:
        categories_keywords (dict): The hierarchical categories data.
        keywords_counts (dict): A dictionary mapping keywords to their counts.
    """
    data = []
    for category in categories_keywords['categories']:
        for subcategory in category['subcategories']:
            for keyword in subcategory['keywords']:
                count = keywords_counts.get(keyword, 1)  # Default to 1 if not found
                data.append({
                    'Category': category['category_name'],
                    'Subcategory': subcategory['subcategory_name'],
                    'Keyword': keyword,
                    'Count': count
                })

    df = pd.DataFrame(data)
    fig = px.treemap(
        df,
        path=['Category', 'Subcategory', 'Keyword'],
        values='Count',
        color='Count',
        hover_data=['Category', 'Subcategory', 'Keyword', 'Count'],
        title="Interactive Categories Treemap",
        color_continuous_scale='Blues'
    )
    fig.update_traces(root_color="lightgrey")
    fig.show()
    fig.write_html(f'{output_folder}\\treemap_cat.html')



# 2. Interactive Sunburst Chart using Plotly
def create_sunburst(categories_keywords, keywords_counts):
    """
    Creates an interactive Sunburst Chart using Plotly.

    Parameters:
        categories_keywords (dict): The hierarchical categories data.
        keywords_counts (dict): A dictionary mapping keywords to their counts.
    """
    data = []
    for category in categories_keywords['categories']:
        for subcategory in category['subcategories']:
            for keyword in subcategory['keywords']:
                count = keywords_counts.get(keyword, 1)  # Default to 1 if not found
                data.append({
                    'Category': category['category_name'],
                    'Subcategory': subcategory['subcategory_name'],
                    'Keyword': keyword,
                    'Count': count
                })

    df = pd.DataFrame(data)
    fig = px.sunburst(
        df,
        path=['Category', 'Subcategory', 'Keyword'],
        values='Count',
        color='Count',
        hover_data=['Category', 'Subcategory', 'Keyword', 'Count'],
        title="Interactive Sunburst Chart",
        color_continuous_scale='Viridis'
    )
    fig.show()
    fig.write_html(f'{output_folder}\\Sunburst.html')



# 6. Interactive Clustered Bar Chart using Plotly
def create_clustered_bar_chart(categories_keywords, keywords_counts):
    """
    Creates an interactive Clustered Bar Chart using Plotly.

    Parameters:
        categories_keywords (dict): The hierarchical categories data.
        keywords_counts (dict): A dictionary mapping keywords to their counts.
    """
    data = []
    for category in categories_keywords['categories']:
        for subcategory in category['subcategories']:
            total_keywords = sum(keywords_counts.get(keyword, 0) for keyword in subcategory['keywords'])
            data.append({
                'Category': category['category_name'],
                'Subcategory': subcategory['subcategory_name'],
                'Keyword Count': total_keywords
            })

    df = pd.DataFrame(data)
    fig = px.bar(
        df,
        x='Subcategory',
        y='Keyword Count',
        color='Category',
        barmode='group',
        title="Interactive Clustered Bar Chart of Categories and Subcategories",
        labels={'Keyword Count': 'Total Keyword Count'},
        hover_data=['Category', 'Subcategory', 'Keyword Count']
    )
    fig.update_layout(xaxis_title="Subcategory", yaxis_title="Total Keyword Count")
    fig.show()
    fig.write_html(f'{output_folder}\\clustered_bar_chart.html')



# Main Function to Call All Visualizations
def create_all_visualizations(categories_keywords, keywords_counts):
    """
    Calls all visualization functions sequentially.

    Parameters:
        categories_keywords (dict): The hierarchical categories data.
        keywords_counts (dict): A dictionary mapping keywords to their counts.
    """
    create_treemap(categories_keywords, keywords_counts)
    create_sunburst(categories_keywords, keywords_counts)
    create_clustered_bar_chart(categories_keywords, keywords_counts)


def generate_graph():
    """
    Generates all visualizations.
    """
    # Data1 Visualizations
    plot_word_frequency()
    plot_treemap()
    plot_pie_chart()

    plot_line_distribution()
    plot_pareto_chart()
    plot_wordcloud()


