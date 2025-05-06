#!/usr/bin/env python3

# CSS styles for the Gradio interface

gradio_css = """
        /* Main styling for the entire interface */
        .gradio-container {
            background-color: white;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
        }
        
        /* Login container styling */
        #login-container {
            background-color: white;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
            padding: 20px;
            max-width: 800px;
            margin: 50px auto;
        }
        
        /* Card styling for components */
        .card {
            background-color: white;
            border-radius: 8px;
            box-shadow: 0 2px 5px rgba(0, 0, 0, 0.05);
            padding: 15px;
            margin-bottom: 15px;
        }
        
        /* Header styling */
        h1, h2, h3 {
            font-weight: 600;
            color: #333;
        }
        
        /* Button styling */
        button.primary {
            background-color: #0078d4 !important;
            border: none;
            color: white;
        }
        
        /* Secondary buttons */
        .secondary-button {
            border: 1px solid #0078d4 !important;
            color: #0078d4 !important;
            background-color: white !important;
        }
        
        /* Chat interface styling */
        #chat-interface {
            background-color: white;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
            padding: 20px;
        }
        
        /* Message container */
        .message {
            padding: 10px 15px;
            border-radius: 8px;
            margin-bottom: 10px;
        }
        
        /* User message */
        .user-message {
            background-color: #e6f2ff;
            color: #333;
            margin-left: 20%;
        }
        
        /* Bot message */
        .bot-message {
            background-color: #f5f5f7;
            color: #333;
            margin-right: 20%;
        }
        
        /* Sidebar with symptoms */
        .sidebar {
            background-color: white;
            border-radius: 8px;
            padding: 15px;
        }
        
        /* Improve textbox appearance */
        .gr-box {
            border-radius: 8px !important;
            border: 1px solid #ddd !important;
        }
        
        /* Conversation container */
        .gr-chatbox {
            border: 1px solid #eee;
            border-radius: 10px;
            overflow: hidden;
        }
    """
