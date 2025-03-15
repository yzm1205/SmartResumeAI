import os
import logging
import tempfile
from pathlib import Path
from PyPDF2 import PdfReader
import docx2txt

logger = logging.getLogger(__name__)

def extract_text_from_pdf(file_path):
    """
    Extract text from PDF file
    
    Args:
        file_path (str): Path to PDF file
        
    Returns:
        str: Extracted text
    """
    try:
        text = ""
        with open(file_path, "rb") as f:
            pdf_reader = PdfReader(f)
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                text += page.extract_text()
        return text
    except Exception as e:
        logger.error(f"Error extracting text from PDF: {str(e)}")
        return ""

def extract_text_from_docx(file_path):
    """
    Extract text from DOCX file
    
    Args:
        file_path (str): Path to DOCX file
        
    Returns:
        str: Extracted text
    """
    try:
        text = docx2txt.process(file_path)
        return text
    except Exception as e:
        logger.error(f"Error extracting text from DOCX: {str(e)}")
        return ""

def extract_text_from_txt(file_path):
    """
    Extract text from TXT file
    
    Args:
        file_path (str): Path to TXT file
        
    Returns:
        str: Extracted text
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            text = f.read()
        return text
    except Exception as e:
        logger.error(f"Error extracting text from TXT: {str(e)}")
        return ""

def save_uploaded_file(uploaded_file, upload_dir="data/uploads"):
    """
    Save uploaded file to disk
    
    Args:
        uploaded_file: Streamlit uploaded file object
        upload_dir (str): Directory to save file
        
    Returns:
        str: Path to saved file
    """
    try:
        # Create upload directory if it doesn't exist
        os.makedirs(upload_dir, exist_ok=True)
        
        # Save file
        file_path = os.path.join(upload_dir, uploaded_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        logger.info(f"Saved uploaded file to {file_path}")
        return file_path
    except Exception as e:
        logger.error(f"Error saving uploaded file: {str(e)}")
        return None

def extract_text_from_file(file_path):
    """
    Extract text from file based on extension
    
    Args:
        file_path (str): Path to file
        
    Returns:
        str: Extracted text
    """
    # Get file extension
    file_ext = os.path.splitext(file_path)[1].lower()
    
    # Extract text based on file extension
    if file_ext == ".pdf":
        return extract_text_from_pdf(file_path)
    elif file_ext == ".docx":
        return extract_text_from_docx(file_path)
    elif file_ext == ".txt":
        return extract_text_from_txt(file_path)
    else:
        logger.error(f"Unsupported file extension: {file_ext}")
        return "" 