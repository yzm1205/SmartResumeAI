import streamlit as st
import os
from dotenv import load_dotenv
from app.frontend.ui import render_ui
from app.core.setup import initialize_app

# Load environment variables
load_dotenv()

def main():
    """
    Main function to run the SmartResumeAI application.
    """
    # Page configuration
    st.set_page_config(
        page_title="SmartResumeAI",
        page_icon="📄",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Check if API key is set
    if not os.getenv("OPENAI_API_KEY"):
        st.error("⚠️ OpenAI API key not found. Please set your OPENAI_API_KEY in the .env file.")
        st.stop()
    
    # Initialize the application
    initialize_app()
    
    # Render the UI
    render_ui()

if __name__ == "__main__":
    main() 