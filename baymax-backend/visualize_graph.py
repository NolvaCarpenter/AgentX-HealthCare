#!/usr/bin/env python3

import os

# Import the conversation graph from the main module
from conversation_agent import conversation_graph




# Added this because display_workflow() doesn't work in my machine (Ubuntu 22.04)

def save_graph_as_png(output_path=None):
    """
    Generate and save the conversation graph as a PNG file using graphviz.
    
    Args:
        output_path (str, optional): Path to save the PNG file. 
                                    Defaults to conversation_workflow.png in current directory.
    
    Returns:
        str: Path to the generated PNG file
    """
    # Set default output path if not specified
    if not output_path:
        output_path = "conversation_workflow.png"
    
    # Get the graph
    graph = conversation_graph.get_graph()
    
    try:
        # First try to generate the mermaid code (text-only) as a backup
        mermaid_code = graph.draw_mermaid()
        print("Generated Mermaid code successfully")
        
        # Save the mermaid code as a text file for reference
        mmd_path = os.path.splitext(output_path)[0] + ".mmd"
        with open(mmd_path, "w") as f:
            f.write(mermaid_code)
        print(f"Saved Mermaid code to {mmd_path}")
        
        # Try to use graphviz to generate PNG
        print("Attempting to generate PNG using graphviz...")
        png_data = graph.draw_png()
        
        # Save to file
        with open(output_path, "wb") as f:
            f.write(png_data)
        
        print("Conversation_graph.png saved using graphviz")
        return output_path
    
    except Exception as e:
        print(f"Error generating PNG: {str(e)}")
        print("Mermaid code was saved to a .mmd file which can be used with online Mermaid editors")
        return mmd_path


if __name__ == "__main__":
    # Generate and save the PNG
    print("Starting graph visualization...")
    output_file = save_graph_as_png()
    print(f"Graph visualization saved to: {output_file}") 