import os
import logging
import chromadb
from chromadb.config import Settings
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings

logger = logging.getLogger(__name__)

# Get vector database path from environment variables
VECTOR_DB_PATH = os.getenv("VECTOR_DB_PATH", "data/vectordb")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-ada-002")

# Initialize embeddings
embeddings = None

def get_embeddings():
    """Get OpenAI embeddings instance."""
    global embeddings
    
    if embeddings is None:
        try:
            embeddings = OpenAIEmbeddings(model=EMBEDDING_MODEL)
        except Exception as e:
            logger.error(f"Error initializing OpenAI embeddings: {str(e)}")
            raise
    
    return embeddings

def init_vector_store():
    """Initialize ChromaDB vector store."""
    try:
        # Create vector database directory if it doesn't exist
        os.makedirs(VECTOR_DB_PATH, exist_ok=True)
        
        # Initialize ChromaDB client
        client = chromadb.PersistentClient(path=VECTOR_DB_PATH)
        
        # Ensure collections exist
        if "resume_data" not in client.list_collections():
            client.create_collection(name="resume_data")
        
        if "job_descriptions" not in client.list_collections():
            client.create_collection(name="job_descriptions")
        
        logger.info(f"Vector store initialized successfully at {VECTOR_DB_PATH}")
        return True
    
    except Exception as e:
        logger.error(f"Error initializing vector store: {str(e)}")
        return False

def get_resume_vector_db():
    """Get the resume data vector store."""
    try:
        return Chroma(
            collection_name="resume_data", 
            embedding_function=get_embeddings(),
            persist_directory=VECTOR_DB_PATH
        )
    except Exception as e:
        logger.error(f"Error getting resume vector DB: {str(e)}")
        raise

def get_job_vector_db():
    """Get the job descriptions vector store."""
    try:
        return Chroma(
            collection_name="job_descriptions", 
            embedding_function=get_embeddings(),
            persist_directory=VECTOR_DB_PATH
        )
    except Exception as e:
        logger.error(f"Error getting job vector DB: {str(e)}")
        raise

def add_resume_data(data_id, text, metadata=None):
    """Add resume data to vector store."""
    try:
        db = get_resume_vector_db()
        db.add_texts(texts=[text], metadatas=[metadata or {}], ids=[str(data_id)])
        return True
    except Exception as e:
        logger.error(f"Error adding resume data to vector store: {str(e)}")
        return False

def add_job_description(job_id, text, metadata=None):
    """Add job description to vector store."""
    try:
        db = get_job_vector_db()
        db.add_texts(texts=[text], metadatas=[metadata or {}], ids=[str(job_id)])
        return True
    except Exception as e:
        logger.error(f"Error adding job description to vector store: {str(e)}")
        return False

def search_resume_data(query, limit=5):
    """Search resume data in vector store."""
    try:
        db = get_resume_vector_db()
        results = db.similarity_search_with_score(query, k=limit)
        return results
    except Exception as e:
        logger.error(f"Error searching resume data: {str(e)}")
        return []

def search_job_descriptions(query, limit=5):
    """Search job descriptions in vector store."""
    try:
        db = get_job_vector_db()
        results = db.similarity_search_with_score(query, k=limit)
        return results
    except Exception as e:
        logger.error(f"Error searching job descriptions: {str(e)}")
        return [] 