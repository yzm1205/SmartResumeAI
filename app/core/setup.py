import os
import logging
from pathlib import Path
from app.database.db_manager import init_database
from app.database.vector_store import init_vector_store

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def create_directory_structure():
    """Creates the necessary directory structure for the application."""
    dirs = [
        "data",
        "data/vectordb",
        "data/uploads",
        "data/generated_resumes"
    ]
    
    for dir_path in dirs:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
        logger.info(f"Created directory: {dir_path}")

def initialize_app():
    """Initialize the SmartResumeAI application."""
    logger.info("Initializing SmartResumeAI application...")
    
    # Create directory structure
    create_directory_structure()
    
    # Initialize databases
    init_database()
    init_vector_store()
    
    logger.info("Application initialization complete.") 