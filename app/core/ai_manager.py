import os
import logging
import json
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain_community.llms import Ollama
from app.database.vector_store import search_resume_data, search_job_descriptions
from app.database.db_manager import get_session, User, Experience, Education, Skill

logger = logging.getLogger(__name__)

# Get model configuration from environment variables
LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4-turbo")
MODEL_PROVIDER = os.getenv("MODEL_PROVIDER", "openai")  # 'openai' or 'ollama'
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "mistral")  # Default Ollama model
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")  # Default Ollama host

# List of available open source models for Ollama (models under 10B parameters)
AVAILABLE_OLLAMA_MODELS = [
    "mistral",  # Mistral 7B
    "mistral-openorca",  # Mistral 7B tuned on OpenOrca dataset
    "llama2",  # Llama 2 7B
    "llama2-uncensored",  # Llama 2 7B uncensored variant
    "phi",  # Microsoft Phi models (small but powerful)
    "neural-chat",  # Qualcomm's Neural Chat model
    "orca-mini",  # Orca mini models
    "tinyllama",  # Tiny Llama model
    "gemma",  # Google's Gemma model
    "stablelm-zephyr",  # StableLM Zephyr model
    "codellama",  # Code Llama, optimized for code
]

def get_llm():
    """Get LLM instance based on chosen provider."""
    try:
        if MODEL_PROVIDER.lower() == "ollama":
            # Use Ollama for open source models
            return Ollama(
                model=OLLAMA_MODEL,
                base_url=OLLAMA_HOST,
                temperature=0.2
            )
        else:
            # Use OpenAI by default
            return ChatOpenAI(model_name=LLM_MODEL, temperature=0.2)
    except Exception as e:
        logger.error(f"Error initializing LLM with provider {MODEL_PROVIDER}: {str(e)}")
        raise

def list_available_models():
    """
    List available models for selection.
    
    Returns:
        dict: Dictionary with model providers and their models
    """
    return {
        "openai": ["gpt-3.5-turbo", "gpt-4-turbo"],
        "ollama": AVAILABLE_OLLAMA_MODELS
    }

def set_model_provider(provider, model=None):
    """
    Set the model provider and optionally the model.
    
    Args:
        provider (str): The provider ('openai' or 'ollama')
        model (str, optional): The specific model to use
    
    Returns:
        bool: Success status
    """
    global MODEL_PROVIDER, LLM_MODEL, OLLAMA_MODEL
    
    try:
        if provider.lower() not in ["openai", "ollama"]:
            logger.error(f"Invalid model provider: {provider}")
            return False
        
        MODEL_PROVIDER = provider.lower()
        
        if model:
            if MODEL_PROVIDER == "openai":
                LLM_MODEL = model
            else:  # ollama
                OLLAMA_MODEL = model
        
        # Test the model connection
        _ = get_llm()
        
        logger.info(f"Set model provider to {MODEL_PROVIDER} with model {model if model else 'default'}")
        return True
    except Exception as e:
        logger.error(f"Error setting model provider: {str(e)}")
        return False

def parse_resume(resume_text):
    """
    Parse resume text and extract structured information.
    
    Args:
        resume_text (str): Raw resume text
        
    Returns:
        dict: Structured resume data
    """
    try:
        llm = get_llm()
        
        prompt = PromptTemplate(
            input_variables=["resume_text"],
            template="""
            You are an expert resume parser. Your task is to extract structured information from the following resume.
            Extract the information in JSON format with the following structure:
            
            ```json
            {
                "basic_info": {
                    "name": "",
                    "email": "",
                    "phone": "",
                    "address": "",
                    "linkedin": "",
                    "github": "",
                    "website": "",
                    "summary": ""
                },
                "experiences": [
                    {
                        "company": "",
                        "title": "",
                        "location": "",
                        "start_date": "",
                        "end_date": "",
                        "description": "",
                        "achievements": []
                    }
                ],
                "educations": [
                    {
                        "institution": "",
                        "degree": "",
                        "field_of_study": "",
                        "location": "",
                        "start_date": "",
                        "end_date": "",
                        "gpa": "",
                        "description": ""
                    }
                ],
                "skills": [
                    {
                        "name": "",
                        "category": "",
                        "proficiency": ""
                    }
                ],
                "certifications": [
                    {
                        "name": "",
                        "issuer": "",
                        "date": "",
                        "description": ""
                    }
                ],
                "projects": [
                    {
                        "name": "",
                        "description": "",
                        "technologies": "",
                        "url": "",
                        "start_date": "",
                        "end_date": ""
                    }
                ],
                "publications": [
                    {
                        "title": "",
                        "publisher": "",
                        "date": "",
                        "url": "",
                        "description": ""
                    }
                ],
                "achievements": [
                    {
                        "title": "",
                        "date": "",
                        "description": ""
                    }
                ]
            }
            ```
            
            Resume:
            {resume_text}
            
            Respond ONLY with the JSON object. No other text before or after.
            """
        )
        
        chain = LLMChain(llm=llm, prompt=prompt)
        result = chain.invoke({"resume_text": resume_text})
        
        # Extract JSON from result
        try:
            # Parse the JSON response
            result_text = result.get('text', '')
            # Extract the JSON part if there are other text markers
            if '```json' in result_text:
                json_str = result_text.split('```json')[1].split('```')[0].strip()
            elif '```' in result_text:
                json_str = result_text.split('```')[1].split('```')[0].strip()
            else:
                json_str = result_text
            
            parsed_data = json.loads(json_str)
            return parsed_data
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing JSON from LLM response: {str(e)}")
            logger.error(f"Raw response: {result}")
            return {}
            
    except Exception as e:
        logger.error(f"Error parsing resume: {str(e)}")
        return {}

def analyze_job_description(job_desc_text):
    """
    Analyze job description and extract key requirements.
    
    Args:
        job_desc_text (str): Raw job description text
        
    Returns:
        dict: Structured job requirements
    """
    try:
        llm = get_llm()
        
        prompt = PromptTemplate(
            input_variables=["job_desc"],
            template="""
            You are an expert at analyzing job descriptions. Your task is to extract structured information from the following job description.
            Extract the information in JSON format with the following structure:
            
            ```json
            {
                "job_title": "",
                "company": "",
                "required_skills": [],
                "preferred_skills": [],
                "required_experience": "",
                "required_education": "",
                "job_responsibilities": [],
                "keywords": []
            }
            ```
            
            Job Description:
            {job_desc}
            
            Respond ONLY with the JSON object. No other text before or after.
            """
        )
        
        chain = LLMChain(llm=llm, prompt=prompt)
        result = chain.invoke({"job_desc": job_desc_text})
        
        # Extract JSON from result
        try:
            # Parse the JSON response
            result_text = result.get('text', '')
            # Extract the JSON part if there are other text markers
            if '```json' in result_text:
                json_str = result_text.split('```json')[1].split('```')[0].strip()
            elif '```' in result_text:
                json_str = result_text.split('```')[1].split('```')[0].strip()
            else:
                json_str = result_text
            
            parsed_data = json.loads(json_str)
            return parsed_data
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing JSON from LLM response: {str(e)}")
            logger.error(f"Raw response: {result}")
            return {}
            
    except Exception as e:
        logger.error(f"Error analyzing job description: {str(e)}")
        return {}

def optimize_resume_for_job(user_id, job_description, job_analysis=None):
    """
    Optimize resume for a specific job.
    
    Args:
        user_id (int): User ID
        job_description (str): Raw job description text
        job_analysis (dict, optional): Pre-analyzed job requirements
        
    Returns:
        dict: Optimized resume data
    """
    try:
        # Get user data from database
        session = get_session()
        user = session.query(User).filter(User.id == user_id).first()
        
        if not user:
            logger.error(f"User {user_id} not found")
            return {}
        
        # Analyze job description if not already provided
        if not job_analysis:
            job_analysis = analyze_job_description(job_description)
        
        # Prepare resume data
        resume_data = {
            "basic_info": {
                "name": user.name,
                "email": user.email,
                "phone": user.phone,
                "address": user.address,
                "linkedin": user.linkedin,
                "github": user.github,
                "website": user.website,
                "summary": user.summary
            },
            "experiences": [],
            "educations": [],
            "skills": [],
            "certifications": [],
            "projects": [],
            "publications": [],
            "achievements": []
        }
        
        # Fill in experiences
        for exp in user.experiences:
            resume_data["experiences"].append({
                "company": exp.company,
                "title": exp.title,
                "location": exp.location,
                "start_date": exp.start_date,
                "end_date": exp.end_date,
                "description": exp.description,
                "achievements": exp.achievements.split("\n") if exp.achievements else []
            })
        
        # Fill in educations
        for edu in user.educations:
            resume_data["educations"].append({
                "institution": edu.institution,
                "degree": edu.degree,
                "field_of_study": edu.field_of_study,
                "location": edu.location,
                "start_date": edu.start_date,
                "end_date": edu.end_date,
                "gpa": edu.gpa,
                "description": edu.description
            })
        
        # Fill in skills
        for skill in user.skills:
            resume_data["skills"].append({
                "name": skill.name,
                "category": skill.category,
                "proficiency": skill.proficiency
            })
        
        # Fill in other sections similarly
        # [Code for other sections omitted for brevity]
        
        # Optimize resume using LLM
        llm = get_llm()
        
        prompt = PromptTemplate(
            input_variables=["resume_data", "job_description", "job_analysis"],
            template="""
            You are an expert resume optimizer. Your task is to optimize the resume for the specific job.
            
            Resume Data:
            {resume_data}
            
            Job Description:
            {job_description}
            
            Job Analysis:
            {job_analysis}
            
            Optimize the resume by:
            1. Reordering experiences to highlight the most relevant ones
            2. Rewording achievements to align with job requirements
            3. Highlighting skills that match the job requirements
            4. Ensuring quantitative impact is emphasized
            5. Making sure the resume is ATS-friendly
            6. Ensuring the resume is concise and fits on one page
            
            Provide the optimized resume in JSON format with the same structure as the original resume data.
            Only include the most relevant and impressive achievements, skills, and experiences that align with the job requirements.
            
            Respond ONLY with the JSON object. No other text before or after.
            """
        )
        
        chain = LLMChain(llm=llm, prompt=prompt)
        result = chain.invoke({
            "resume_data": json.dumps(resume_data, indent=2),
            "job_description": job_description,
            "job_analysis": json.dumps(job_analysis, indent=2)
        })
        
        # Extract JSON from result
        try:
            # Parse the JSON response
            result_text = result.get('text', '')
            # Extract the JSON part if there are other text markers
            if '```json' in result_text:
                json_str = result_text.split('```json')[1].split('```')[0].strip()
            elif '```' in result_text:
                json_str = result_text.split('```')[1].split('```')[0].strip()
            else:
                json_str = result_text
            
            optimized_data = json.loads(json_str)
            return optimized_data
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing JSON from LLM response: {str(e)}")
            logger.error(f"Raw response: {result}")
            return resume_data
            
    except Exception as e:
        logger.error(f"Error optimizing resume: {str(e)}")
        return {} 