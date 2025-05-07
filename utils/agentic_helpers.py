import os
import tempfile
import webbrowser


# Visualize the workflow
def display_workflow():
    """Display the workflow as a Mermaid diagram."""
    # Get the Mermaid markdown content directly
    mermaid_code = conversation_graph.get_graph(xray=1).draw_mermaid()

    # Save to a temporary file
    temp_dir = tempfile.gettempdir()
    mermaid_path = os.path.join(temp_dir, "workflow_diagram.mmd")
    html_path = os.path.join(temp_dir, "workflow_diagram.html")

    # Write the Mermaid markdown to the file
    with open(mermaid_path, "w") as f:
        f.write(mermaid_code)

    # Create an HTML file with embedded Mermaid that works offline
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Workflow Diagram</title>
        <script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
        <script>
            mermaid.initialize({{ startOnLoad: true }});
        </script>
    </head>
    <body>
        <div class="mermaid">
        {mermaid_code}
        </div>
    </body>
    </html>
    """

    with open(html_path, "w") as f:
        f.write(html_content)

    # Open the HTML file with the default web browser
    print(f"Opening workflow diagram at: {html_path}")
    try:
        os.startfile(html_path)  # This works on Windows
    except AttributeError:
        # Fallback for non-Windows systems
        try:
            webbrowser.open(f"file://{html_path}")
        except Exception as e:
            print(f"Could not open the HTML file: {e}")
            print(f"The diagram has been saved to: {mermaid_path}")
            print(f"The HTML viewer has been saved to: {html_path}")

    # Also print the Mermaid code to console for reference
    print("\nMermaid diagram code:")
    print(mermaid_code)

    return mermaid_code
