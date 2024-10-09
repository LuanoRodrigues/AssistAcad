import re
import uuid
from pyjsoncanvas import Canvas, TextNode, GroupNode, Edge, Color
import re
import uuid

import re
import uuid

def parse_markdown(md_content):
    """
    Parses the markdown content and returns a hierarchical structure.
    Each heading level is represented as a nested dictionary.
    Also captures blockquote content under each heading.
    """
    lines = md_content.split('\n')
    hierarchy = []
    stack = []
    current_node = None

    # Regular expressions to identify headings and blockquotes
    heading_regex = re.compile(r'^(#{1,6})\s+(.*)')
    # Updated blockquote regex to handle multiple '>' and extract text within '** **'
    blockquote_regex = re.compile(r'^>+\s*\[!important\]\s*>\s*\*\*(.*?)\*\*$')

    for line in lines:
        heading_match = heading_regex.match(line)
        if heading_match:
            hashes, title = heading_match.groups()
            level = len(hashes)
            node = {
                "level": level,
                "title": title.strip(),
                "quotes": []
            }

            if not stack:
                hierarchy.append(node)
                stack.append(node)
            else:
                # Pop from stack until finding a parent with a lower level
                while stack and stack[-1]["level"] >= level:
                    stack.pop()
                if stack:
                    stack[-1].setdefault("children", []).append(node)
                else:
                    hierarchy.append(node)
                stack.append(node)
            current_node = node
        else:
            blockquote_match = blockquote_regex.match(line)
            if blockquote_match and current_node:
                quote = blockquote_match.group(1).strip()
                # Append the quote to the current node's quotes list
                current_node["quotes"].append(quote)

    return hierarchy

def create_comprehensive_mind_map_from_md(
        md_file_path,
        file_name=r'C:\Users\luano\OneDrive - University College London\Obsidian\Thesis\comprehensive_mind_map_3.canvas'
                              ):

    try:
        # Read the Markdown file
        with open(md_file_path, 'r', encoding='utf-8') as f:
            md_content = f.read()

        # Parse the Markdown content into a hierarchical structure
        hierarchy = parse_markdown(md_content)

        # Create a new canvas with empty nodes and edges
        canvas = Canvas(nodes=[], edges=[])

        # Positioning parameters
        base_x, base_y = 100, 100
        x_offset_h1 = 5000    # Increased horizontal spacing between h1 nodes (doubled from 2300)
        y_offset = 1000       # Vertical spacing between regular child nodes (unchanged)
        node_width, node_height = 800, 70  # Reduced node width to 600 units
        quote_width, quote_height = 800, 120  # Fixed height for consolidated quotes
        child_x_offset = 2000  # Horizontal offset for child nodes (unchanged)

        # Define color mapping for heading levels
        level_colors = {
            1: "#000000",  # Black for H1
            2: "#0000FF",  # Blue for H2
            3: "#008000",  # Green for H3
            4: "#FF0000",  # Red for H4
            5: "#FFC0CB"   # Pink for H5
            # Extend if needed for levels 6+
        }

        # Set to track used IDs to ensure uniqueness
        used_ids = set()

        def generate_unique_id():
            """Generates a unique UUID and ensures it's not already used."""
            while True:
                unique_id = str(uuid.uuid4())
                if unique_id not in used_ids:
                    used_ids.add(unique_id)
                    return unique_id

        # Initialize h1_counter as a list to allow modification inside nested function
        h1_counter = [0]

        def add_nodes(node, parent_id=None, x=base_x, y=base_y, level=1):
            title = node['title']
            quotes = node.get('quotes', [])
            children = node.get('children', [])

            # Generate a unique ID for the node
            node_id = generate_unique_id()

            if level == 1:
                # For each h1, position them far apart horizontally
                node_x = base_x + h1_counter[0] * x_offset_h1
                node_y = base_y
                node_x = int(node_x)
                node_y = int(node_y)
                # Create a GroupNode for h1 with specific color
                group_node = GroupNode(
                    id=node_id,
                    x=node_x,
                    y=node_y,
                    width=node_width+100,
                    height=node_height,
                    label=title,
                    color=Color(level_colors.get(level, "#000000"))  # Default to black if level not in mapping
                )
                canvas.add_node(group_node)
                print(f"Added GroupNode: '{title}' at ({node_x}, {node_y}) with ID {node_id}")
                # Increment h1_counter
                h1_counter[0] += 1
            else:
                
                # Position child nodes below their parent
                node_x = x
                node_y = y + y_offset
                node_x = int(node_x)
                node_y = int(node_y)
                # Determine color based on level
                node_color = Color("#FFFFFF")  # Default white text
                if isinstance(level, int) and level in level_colors:
                    node_color = Color(level_colors.get(level))  # White text on colored backgrounds
                # Create a TextNode for subheadings
                text_node = TextNode(
                    id=node_id,
                    x=node_x,
                    y=node_y,
                    width=node_width,
                    height=node_height,
                    text=title,
                    color=node_color
                )
                canvas.add_node(text_node)
                node_type = "GroupNode" if level == 1 else "TextNode"
                print(f"Added {node_type}: '{title}' at ({node_x}, {node_y}) with ID {node_id}")

                # Create an edge from parent to this node
                if parent_id:
                    edge = Edge(
                        fromNode=parent_id,
                        fromSide="bottom",
                        toNode=node_id,
                        toSide="top",
                        color=Color("#000000"),  # Black for regular edges
                        label=""  # Optional label
                    )
                    canvas.add_edge(edge)
                    print(f"Added Edge from '{parent_id}' to '{node_id}'")

            # If there are quotes and the current node is a heading, create a consolidated quote node
            if quotes and level != "quote":
                consolidated_quotes = "\n".join([f"> [!important] > **{quote}**\n\n" for quote in quotes])
                quote_id = generate_unique_id()
                quote_x = node_x
                quote_y = node_y + 200  # Reduced distance to 200
                # Create a consolidated quote TextNode with dynamic height
                quote_node = TextNode(
                    id=quote_id,
                    x=quote_x,
                    y=quote_y,
                    width=quote_width,
                    height=120 * len(quotes),  # Dynamic height based on number of quotes
                    text=consolidated_quotes,
                    color=Color("#FFD700")  # Gold text for quotes
                )
                canvas.add_node(quote_node)
                print(f"Added Consolidated Quote TextNode at ({quote_x}, {quote_y}) with ID {quote_id}")
                # Create Edge from the parent to the consolidated quote node
                quote_edge = Edge(
                    fromNode=node_id,
                    fromSide="bottom",
                    toNode=quote_id,
                    toSide="top",
                    color=Color("#FF4500"),  # Orange-red edge color for quotes
                    label=""
                )
                canvas.add_edge(quote_edge)
                print(f"Added Edge from '{node_id}' to '{quote_id}' for consolidated quotes")

                # Calculate the new y position for child nodes based on quote height
                child_y = quote_y + (120 * len(quotes)) + 200  # quote_y + quote_height + 200
            else:
                child_y = y + y_offset  # Regular y offset

            # Recursively add child nodes
            num_children = len(children)
            if num_children > 0:
                # Total width occupied by children
                total_width = (num_children - 1) * child_x_offset
                # Starting x position for the first child to center the children under the parent
                start_x = node_x - total_width / 2
                for i, child in enumerate(children):
                    child_level = child['level']
                    child_title = child['title']
                    # Calculate child_x and child_y
                    child_x = start_x + i * child_x_offset
                    child_y_position = child_y  # Use the calculated child_y
                    child_x = int(child_x)
                    child_y_position = int(child_y_position)
                    # Recursively add child nodes
                    add_nodes(child, parent_id=node_id, x=child_x, y=child_y_position, level=child_level)

        # Iterate over all top-level nodes (h1 headings)
        for top_node in hierarchy:
            add_nodes(top_node)

        # Validate the canvas before exporting
        try:
            canvas.validate()
            print("Canvas validation successful.")
        except Exception as ve:
            print(f"Canvas validation failed: {ve}")
            return

        # Dynamically calculate canvas size based on node positions
        if canvas.nodes:
            max_x = max(node.x for node in canvas.nodes) + 1000
            max_y = max(node.y for node in canvas.nodes) + 1000
            canvas.canvas_size = {"width": max_x, "height": max_y}
            print(f"Canvas size set to width: {max_x}, height: {max_y}")
        else:
            # Default size if no nodes are present
            canvas.canvas_size = {"width": 1000, "height": 1000}
            print("Canvas size set to default 1000x1000.")

        # Save the canvas as JSON with a .canvas extension
        canvas.export(file_name)

        print(f"Comprehensive mind map created and saved as {file_name}")

    except Exception as e:
        print(f"An error occurred: {e}")

# Example usage:
# create_comprehensive_mind_map_from_md('path_to_your_markdown_file.md')


# Ensure that the JSON structure matches the one provided in your message
create_comprehensive_mind_map_from_md(r"C:\Users\luano\OneDrive - University College London\Obsidian\Thesis\Reviews\cyber evidence review.md")
