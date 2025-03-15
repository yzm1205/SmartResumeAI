import os
import logging
from pathlib import Path
from app.database.db_manager import init_database
from app.database.vector_store import init_vector_store
from app.core.ai_manager import set_model_provider

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

def initialize_model():
    """Initialize the AI model based on environment settings."""
    model_provider = os.getenv("MODEL_PROVIDER", "openai")
    model = None
    
    if model_provider == "openai":
        model = os.getenv("LLM_MODEL", "gpt-4-turbo")
    else:  # ollama
        model = os.getenv("OLLAMA_MODEL", "mistral")
    
    logger.info(f"Initializing AI with provider: {model_provider}, model: {model}")
    
    try:
        set_model_provider(model_provider, model)
        logger.info("AI model initialized successfully")
        return True
    except Exception as e:
        logger.error(f"Error initializing AI model: {str(e)}")
        logger.warning("Reverting to OpenAI as fallback. Check your model settings.")
        
        # Try to fallback to OpenAI if Ollama fails
        if model_provider != "openai":
            try:
                set_model_provider("openai", "gpt-4-turbo")
                logger.info("Fallback to OpenAI successful")
            except Exception as e2:
                logger.error(f"Fallback initialization failed: {str(e2)}")
        
        return False

def initialize_app():
    """Initialize the SmartResumeAI application."""
    logger.info("Initializing SmartResumeAI application...")
    
    # Create directory structure
    create_directory_structure()
    
    # Initialize databases
    init_database()
    init_vector_store()
    
    # Initialize AI model
    initialize_model()
    
    logger.info("Application initialization complete.") 