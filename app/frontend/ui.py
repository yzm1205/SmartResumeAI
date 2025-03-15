import os
import streamlit as st
import logging
import time
from datetime import datetime
import pandas as pd
import json
from app.utils.file_parser import save_uploaded_file, extract_text_from_file
from app.core.ai_manager import (
    parse_resume, analyze_job_description, optimize_resume_for_job,
    list_available_models, set_model_provider, get_llm
)
from app.database.db_manager import get_session, User, Experience, Education, Skill, Certification, Project, Publication, Achievement
from app.pdf_generation.resume_generator import generate_pdf_resume, generate_docx_resume

logger = logging.getLogger(__name__)

# Session state initialization
def init_session_state():
    """Initialize session state variables."""
    if "user_id" not in st.session_state:
        st.session_state.user_id = None
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "resume_data" not in st.session_state:
        st.session_state.resume_data = {}
    if "job_description" not in st.session_state:
        st.session_state.job_description = ""
    if "job_analysis" not in st.session_state:
        st.session_state.job_analysis = {}
    if "optimized_resume" not in st.session_state:
        st.session_state.optimized_resume = {}
    if "model_provider" not in st.session_state:
        st.session_state.model_provider = os.getenv("MODEL_PROVIDER", "openai")
    if "selected_model" not in st.session_state:
        if st.session_state.model_provider == "openai":
            st.session_state.selected_model = os.getenv("LLM_MODEL", "gpt-4-turbo")
        else:
            st.session_state.selected_model = os.getenv("OLLAMA_MODEL", "mistral")

def render_ui():
    """Render the Streamlit UI."""
    # Initialize session state
    init_session_state()
    
    # App header
    st.title("SmartResumeAI")
    st.subheader("AI-Powered Resume Tailoring for Job Success")
    
    # Sidebar
    with st.sidebar:
        st.header("Options")
        
        # Display username if available
        if st.session_state.user_id:
            session = get_session()
            user = session.query(User).filter(User.id == st.session_state.user_id).first()
            if user and user.name:
                st.success(f"Logged in as: {user.name}")
        
        # Navigation
        page = st.radio("Navigation", [
            "🏠 Home", 
            "📄 Resume Upload", 
            "💬 Resume Chat", 
            "🔍 Job Matching", 
            "📊 Resume Analysis",
            "⬇️ Generate Resume",
            "⚙️ Settings"
        ])
        
        # Clear data button
        if st.button("Clear All Data"):
            # Reset session state
            st.session_state.user_id = None
            st.session_state.chat_history = []
            st.session_state.resume_data = {}
            st.session_state.job_description = ""
            st.session_state.job_analysis = {}
            st.session_state.optimized_resume = {}
            st.success("All data cleared!")
            
            # Wait for a moment and then rerun the app
            time.sleep(1)
            st.experimental_rerun()
    
    # Main content based on selected page
    if page == "🏠 Home":
        render_home_page()
    elif page == "📄 Resume Upload":
        render_resume_upload_page()
    elif page == "💬 Resume Chat":
        render_resume_chat_page()
    elif page == "🔍 Job Matching":
        render_job_matching_page()
    elif page == "📊 Resume Analysis":
        render_resume_analysis_page()
    elif page == "⬇️ Generate Resume":
        render_generate_resume_page()
    elif page == "⚙️ Settings":
        render_settings_page()

def render_home_page():
    """Render the home page."""
    st.markdown("""
    ## Welcome to SmartResumeAI!
    
    SmartResumeAI helps you create tailored resumes that are optimized for specific job descriptions.
    
    ### How it works:
    
    1. **Upload your resume** - Upload your existing resume in PDF, DOCX, or TXT format.
    2. **Chat with the AI** - Refine your resume through natural conversation with our AI assistant.
    3. **Add job descriptions** - Paste job descriptions to optimize your resume for specific opportunities.
    4. **Generate optimized resume** - Create an ATS-friendly resume tailored to your target job.
    5. **Download as PDF or DOCX** - Get your polished resume ready for submission.
    
    ### Get started:
    
    - Navigate to "Resume Upload" in the sidebar to begin.
    - Already uploaded a resume? Head to "Resume Chat" to refine it.
    - Have a job target? Visit "Job Matching" to optimize your resume.
    
    ### Why SmartResumeAI?
    
    ✅ **AI-Powered Personalization**: Automatically adapts resumes to match job descriptions.  
    ✅ **High ATS Score Optimization**: Ensures job applications pass automated screenings.  
    ✅ **User-Friendly Interface**: Provides real-time feedback and edits.  
    ✅ **Efficient Job Matching**: Uses NLP to align resumes with job requirements.  
    ✅ **Professional Resume Formatting**: Generates polished, ATS-compatible documents.
    ✅ **Open-Source Model Support**: Use free, open-source models locally with Ollama.
    """)

    # Display current model info
    st.info(f"Currently using: **{st.session_state.model_provider.upper()}** model - **{st.session_state.selected_model}**")
    
    # If using Ollama, show a note about local installation
    if st.session_state.model_provider == "ollama":
        st.warning("""
        **Note:** You're using Ollama for local model inference. Make sure Ollama is installed and running on your system.
        
        To install Ollama, visit [ollama.ai](https://ollama.ai) and follow the installation instructions.
        After installation, start Ollama and pull your chosen model with: `ollama pull {model_name}`
        """)

def render_settings_page():
    """Render the settings page for model selection."""
    st.header("⚙️ Settings")
    
    # Get available models
    available_models = list_available_models()
    
    with st.form("model_settings"):
        st.subheader("Model Selection")
        st.markdown("""
        Choose between OpenAI's API models (requires API key) or free open-source models via Ollama (local inference).
        
        **OpenAI models:**
        - Require an API key and may incur costs
        - Generally higher quality responses
        - No local setup required
        
        **Ollama models (open-source):**
        - Completely free to use
        - Run locally on your computer
        - Require Ollama installation ([ollama.ai](https://ollama.ai))
        - Performance depends on your hardware
        """)
        
        # Model provider selection
        model_provider = st.radio(
            "Model Provider", 
            ["openai", "ollama"],
            index=0 if st.session_state.model_provider == "openai" else 1
        )
        
        # Model selection based on provider
        if model_provider == "openai":
            selected_model = st.selectbox(
                "OpenAI Model", 
                available_models["openai"],
                index=available_models["openai"].index(st.session_state.selected_model) 
                if st.session_state.selected_model in available_models["openai"] else 0
            )
            
            st.text_input(
                "OpenAI API Key", 
                value=os.getenv("OPENAI_API_KEY", ""),
                type="password",
                key="openai_api_key"
            )
            
        else:  # ollama
            selected_model = st.selectbox(
                "Ollama Model", 
                available_models["ollama"],
                index=available_models["ollama"].index(st.session_state.selected_model) 
                if st.session_state.selected_model in available_models["ollama"] else 0
            )
            
            ollama_host = st.text_input(
                "Ollama Host", 
                value=os.getenv("OLLAMA_HOST", "http://localhost:11434"),
                key="ollama_host"
            )
            
            st.markdown("""
            **Ollama Installation Instructions:**
            1. Download and install Ollama from [ollama.ai](https://ollama.ai)
            2. Start Ollama on your system
            3. Pull your chosen model: `ollama pull {model_name}`
            """)
        
        # Submit button
        submit_button = st.form_submit_button("Save Settings")
        
        if submit_button:
            try:
                # Update environment variables and session state
                os.environ["MODEL_PROVIDER"] = model_provider
                
                if model_provider == "openai":
                    os.environ["LLM_MODEL"] = selected_model
                    if st.session_state.openai_api_key:
                        os.environ["OPENAI_API_KEY"] = st.session_state.openai_api_key
                else:  # ollama
                    os.environ["OLLAMA_MODEL"] = selected_model
                    os.environ["OLLAMA_HOST"] = st.session_state.ollama_host
                
                # Update session state
                st.session_state.model_provider = model_provider
                st.session_state.selected_model = selected_model
                
                # Update model in AI manager
                success = set_model_provider(model_provider, selected_model)
                
                if success:
                    st.success(f"Successfully switched to {model_provider.upper()} model: {selected_model}")
                    
                    # Additional message for Ollama users
                    if model_provider == "ollama":
                        st.info("""
                        Make sure Ollama is running and the selected model is installed.
                        If you haven't pulled the model yet, open a terminal and run:
                        ```
                        ollama pull {model_name}
                        ```
                        """.format(model_name=selected_model))
                else:
                    st.error("Failed to switch model. Please check your settings and try again.")
            except Exception as e:
                st.error(f"Error updating model settings: {str(e)}")
    
    # Show current model status
    st.subheader("Current Model Status")
    
    try:
        # Try to get LLM to check if it's working
        llm = get_llm()
        st.success(f"✅ Using {st.session_state.model_provider.upper()} model: {st.session_state.selected_model}")
    except Exception as e:
        st.error(f"❌ Error connecting to model: {str(e)}")
        
        if st.session_state.model_provider == "openai":
            st.warning("Please check your OpenAI API key.")
        else:  # ollama
            st.warning("""
            Issues with Ollama? Try:
            1. Make sure Ollama is installed and running
            2. Check if you've pulled the model with `ollama pull {model_name}`
            3. Verify the Ollama host address (default: http://localhost:11434)
            """.format(model_name=st.session_state.selected_model))

def render_resume_upload_page():
    """Render the resume upload page."""
    st.header("Resume Upload")
    
    # Show currently uploaded resume data if available
    if st.session_state.resume_data:
        st.success("✅ Resume data available")
        if st.checkbox("Show currently parsed resume data"):
            st.json(st.session_state.resume_data)
    
    # File upload
    st.markdown("### Upload your resume")
    uploaded_file = st.file_uploader("Choose a file", type=["pdf", "docx", "txt"])
    
    if uploaded_file is not None:
        # Save the uploaded file
        with st.spinner("Uploading resume..."):
            file_path = save_uploaded_file(uploaded_file)
            
            if file_path:
                st.success(f"File uploaded successfully: {uploaded_file.name}")
                
                # Extract text from file
                with st.spinner("Extracting text from resume..."):
                    resume_text = extract_text_from_file(file_path)
                    
                    if resume_text:
                        st.success("Text extracted successfully")
                        
                        # Parse resume text
                        with st.spinner("Parsing resume with AI..."):
                            resume_data = parse_resume(resume_text)
                            
                            if resume_data:
                                st.success("Resume parsed successfully")
                                
                                # Save to session state
                                st.session_state.resume_data = resume_data
                                
                                # Create or update user in database
                                create_or_update_user(resume_data)
                                
                                # Display parsed data
                                st.subheader("Parsed Resume Data")
                                st.json(resume_data)
                            else:
                                st.error("Error parsing resume. Please try again.")
                    else:
                        st.error("Error extracting text from file. Please try another file format.")
            else:
                st.error("Error uploading file. Please try again.")
    
    # Manual input option
    st.markdown("### Or enter resume data manually")
    
    if st.checkbox("Enter resume data manually"):
        with st.form("manual_resume_form"):
            # Basic info
            st.subheader("Basic Information")
            name = st.text_input("Name")
            email = st.text_input("Email")
            phone = st.text_input("Phone")
            
            # Summary
            st.subheader("Professional Summary")
            summary = st.text_area("Summary")
            
            # Submit button
            submit_button = st.form_submit_button("Save Resume Data")
            
            if submit_button:
                # Create basic resume data
                resume_data = {
                    "basic_info": {
                        "name": name,
                        "email": email,
                        "phone": phone,
                        "summary": summary
                    },
                    "experiences": [],
                    "educations": [],
                    "skills": []
                }
                
                # Save to session state
                st.session_state.resume_data = resume_data
                
                # Create or update user in database
                create_or_update_user(resume_data)
                
                st.success("Resume data saved successfully")

def render_resume_chat_page():
    """Render the resume chat page."""
    st.header("Resume Chat")
    
    # Check if resume data is available
    if not st.session_state.resume_data:
        st.warning("Please upload your resume first.")
        return
    
    # Initialize OpenAI client if not already done
    if "chat_initialized" not in st.session_state:
        try:
            # Just a placeholder to check if we can initialize LLM
            from app.core.ai_manager import get_llm
            llm = get_llm()
            st.session_state.chat_initialized = True
        except Exception as e:
            st.error(f"Error initializing chat: {str(e)}")
            st.error("Please make sure your OpenAI API key is set correctly.")
            return
    
    # Display chat history
    st.subheader("Chat with AI about your resume")
    
    # Display chat messages
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("How can I improve my resume?"):
        # Add user message to chat history
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Generate AI response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                # Here we would normally call the AI to generate a response
                # For now, we'll just generate a mock response
                try:
                    from app.core.ai_manager import get_llm
                    from langchain.chains import LLMChain
                    from langchain.prompts import PromptTemplate
                    
                    llm = get_llm()
                    
                    # Prepare context from resume data
                    resume_context = json.dumps(st.session_state.resume_data, indent=2)
                    
                    # Prepare chat history
                    chat_history_text = ""
                    for msg in st.session_state.chat_history:
                        chat_history_text += f"{msg['role']}: {msg['content']}\n\n"
                    
                    # Create prompt
                    prompt_template = PromptTemplate(
                        input_variables=["resume_data", "chat_history", "user_message"],
                        template="""
                        You are an AI resume assistant helping a user improve their resume.
                        
                        Here is the user's resume data:
                        {resume_data}
                        
                        Chat history:
                        {chat_history}
                        
                        The user's latest message is:
                        {user_message}
                        
                        Provide a helpful response that helps the user improve their resume.
                        If they ask for improvements, be specific about how they can enhance their resume.
                        If they want to add or modify information, explain how to do that effectively.
                        Be concise but thorough in your advice.
                        """
                    )
                    
                    # Create chain
                    chain = LLMChain(llm=llm, prompt=prompt_template)
                    
                    # Generate response
                    response = chain.invoke({
                        "resume_data": resume_context,
                        "chat_history": chat_history_text,
                        "user_message": prompt
                    })
                    
                    ai_response = response.get("text", "I'm sorry, I couldn't generate a response.")
                    
                except Exception as e:
                    logger.error(f"Error generating AI response: {str(e)}")
                    ai_response = "I'm sorry, I encountered an error. Please try again."
                
                # Display AI response
                st.markdown(ai_response)
                
                # Add AI response to chat history
                st.session_state.chat_history.append({"role": "assistant", "content": ai_response})

def render_job_matching_page():
    """Render the job matching page."""
    st.header("Job Matching")
    
    # Check if resume data is available
    if not st.session_state.resume_data:
        st.warning("Please upload your resume first.")
        return
    
    # Job description input
    st.subheader("Enter Job Description")
    job_description = st.text_area("Paste job description here", st.session_state.job_description, height=300)
    
    if st.button("Analyze Job Description"):
        if job_description:
            # Save job description to session state
            st.session_state.job_description = job_description
            
            # Analyze job description
            with st.spinner("Analyzing job description..."):
                job_analysis = analyze_job_description(job_description)
                
                if job_analysis:
                    # Save job analysis to session state
                    st.session_state.job_analysis = job_analysis
                    
                    # Display job analysis
                    st.subheader("Job Analysis")
                    st.json(job_analysis)
                    
                    # Match with resume
                    st.subheader("Resume Match")
                    
                    # Extract required skills from job
                    required_skills = job_analysis.get("required_skills", [])
                    preferred_skills = job_analysis.get("preferred_skills", [])
                    all_skills = required_skills + preferred_skills
                    
                    # Extract skills from resume
                    resume_skills = [skill.get("name", "") for skill in st.session_state.resume_data.get("skills", [])]
                    
                    # Find matching skills
                    matching_skills = [skill for skill in resume_skills if any(job_skill.lower() in skill.lower() for job_skill in all_skills)]
                    missing_skills = [skill for skill in all_skills if not any(skill.lower() in resume_skill.lower() for resume_skill in resume_skills)]
                    
                    # Display skills match
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("#### Matching Skills")
                        for skill in matching_skills:
                            st.success(skill)
                    
                    with col2:
                        st.markdown("#### Missing Skills")
                        for skill in missing_skills:
                            st.warning(skill)
                    
                    # Generate resume optimization button
                    if st.button("Optimize Resume for This Job"):
                        with st.spinner("Optimizing resume..."):
                            # Here we would normally call the AI to optimize the resume
                            optimized_resume = optimize_resume_for_job(
                                st.session_state.user_id, 
                                job_description, 
                                job_analysis
                            )
                            
                            if optimized_resume:
                                # Save optimized resume to session state
                                st.session_state.optimized_resume = optimized_resume
                                
                                # Display success message
                                st.success("Resume optimized successfully! Go to the 'Generate Resume' page to download.")
                            else:
                                st.error("Error optimizing resume. Please try again.")
                else:
                    st.error("Error analyzing job description. Please try again.")
        else:
            st.error("Please enter a job description.")

def render_resume_analysis_page():
    """Render the resume analysis page."""
    st.header("Resume Analysis")
    
    # Check if resume data is available
    if not st.session_state.resume_data:
        st.warning("Please upload your resume first.")
        return
    
    # Resume data
    resume_data = st.session_state.resume_data
    
    # Basic info
    st.subheader("Basic Information")
    basic_info = resume_data.get("basic_info", {})
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"**Name:** {basic_info.get('name', 'N/A')}")
        st.markdown(f"**Email:** {basic_info.get('email', 'N/A')}")
        st.markdown(f"**Phone:** {basic_info.get('phone', 'N/A')}")
    
    with col2:
        st.markdown(f"**LinkedIn:** {basic_info.get('linkedin', 'N/A')}")
        st.markdown(f"**GitHub:** {basic_info.get('github', 'N/A')}")
        st.markdown(f"**Website:** {basic_info.get('website', 'N/A')}")
    
    # Summary
    st.subheader("Professional Summary")
    st.markdown(basic_info.get("summary", "No summary provided."))
    
    # Experience
    st.subheader("Experience")
    experiences = resume_data.get("experiences", [])
    
    if experiences:
        for exp in experiences:
            with st.expander(f"{exp.get('title', 'Role')} at {exp.get('company', 'Company')}"):
                st.markdown(f"**Company:** {exp.get('company', 'N/A')}")
                st.markdown(f"**Title:** {exp.get('title', 'N/A')}")
                st.markdown(f"**Location:** {exp.get('location', 'N/A')}")
                st.markdown(f"**Period:** {exp.get('start_date', 'N/A')} - {exp.get('end_date', 'N/A')}")
                st.markdown(f"**Description:** {exp.get('description', 'N/A')}")
                
                # Achievements
                achievements = exp.get("achievements", [])
                if achievements:
                    st.markdown("**Achievements:**")
                    for achievement in achievements:
                        st.markdown(f"- {achievement}")
    else:
        st.markdown("No experience data available.")
    
    # Education
    st.subheader("Education")
    educations = resume_data.get("educations", [])
    
    if educations:
        for edu in educations:
            with st.expander(f"{edu.get('degree', 'Degree')} from {edu.get('institution', 'Institution')}"):
                st.markdown(f"**Institution:** {edu.get('institution', 'N/A')}")
                st.markdown(f"**Degree:** {edu.get('degree', 'N/A')}")
                st.markdown(f"**Field of Study:** {edu.get('field_of_study', 'N/A')}")
                st.markdown(f"**Location:** {edu.get('location', 'N/A')}")
                st.markdown(f"**Period:** {edu.get('start_date', 'N/A')} - {edu.get('end_date', 'N/A')}")
                st.markdown(f"**GPA:** {edu.get('gpa', 'N/A')}")
                st.markdown(f"**Description:** {edu.get('description', 'N/A')}")
    else:
        st.markdown("No education data available.")
    
    # Skills
    st.subheader("Skills")
    skills = resume_data.get("skills", [])
    
    if skills:
        # Group skills by category
        skill_categories = {}
        for skill in skills:
            category = skill.get("category", "Other")
            if category not in skill_categories:
                skill_categories[category] = []
            skill_categories[category].append(skill.get("name", ""))
        
        # Display skills by category
        for category, skills in skill_categories.items():
            st.markdown(f"**{category}:** {', '.join(skills)}")
    else:
        st.markdown("No skills data available.")
    
    # Resume gaps and suggestions
    st.subheader("Resume Analysis")
    
    # Check for missing sections
    missing_sections = []
    if not experiences:
        missing_sections.append("Experience")
    if not educations:
        missing_sections.append("Education")
    if not skills:
        missing_sections.append("Skills")
    if not resume_data.get("projects", []):
        missing_sections.append("Projects")
    if not resume_data.get("certifications", []):
        missing_sections.append("Certifications")
    
    if missing_sections:
        st.warning(f"Missing sections: {', '.join(missing_sections)}")
    else:
        st.success("All key sections are present in your resume.")
    
    # Check for potential improvements
    improvements = []
    
    # Check if summary is missing or too short
    if not basic_info.get("summary") or len(basic_info.get("summary", "")) < 100:
        improvements.append("Add a more detailed professional summary (aim for 100-200 characters)")
    
    # Check if experiences have achievements
    if experiences:
        for i, exp in enumerate(experiences):
            if not exp.get("achievements") or (isinstance(exp.get("achievements"), list) and len(exp.get("achievements", [])) == 0):
                improvements.append(f"Add achievements for your {exp.get('title')} role at {exp.get('company')}")
    
    # Check if contact info is complete
    if not basic_info.get("email") or not basic_info.get("phone"):
        improvements.append("Add complete contact information (email and phone)")
    
    # Check if LinkedIn profile is present
    if not basic_info.get("linkedin"):
        improvements.append("Add your LinkedIn profile URL")
    
    # Display improvement suggestions
    if improvements:
        st.subheader("Suggested Improvements")
        for improvement in improvements:
            st.info(improvement)

def render_generate_resume_page():
    """Render the generate resume page."""
    st.header("Generate Resume")
    
    # Check if resume data is available
    if not st.session_state.resume_data:
        st.warning("Please upload your resume first.")
        return
    
    # Check which resume data to use
    use_optimized = False
    if st.session_state.optimized_resume:
        use_optimized = st.checkbox("Use optimized resume", value=True)
    
    # Get resume data
    resume_data = st.session_state.optimized_resume if use_optimized else st.session_state.resume_data
    
    # Display preview
    st.subheader("Resume Preview")
    
    # Basic info
    basic_info = resume_data.get("basic_info", {})
    st.markdown(f"## {basic_info.get('name', 'Your Name')}")
    
    # Contact info
    contact_parts = []
    if basic_info.get("email"):
        contact_parts.append(basic_info["email"])
    if basic_info.get("phone"):
        contact_parts.append(basic_info["phone"])
    if basic_info.get("linkedin"):
        contact_parts.append(basic_info["linkedin"])
    
    st.markdown(f"### {' | '.join(contact_parts)}")
    
    # Summary
    if basic_info.get("summary"):
        st.markdown("### PROFESSIONAL SUMMARY")
        st.markdown(basic_info.get("summary"))
    
    # Experience
    experiences = resume_data.get("experiences", [])
    if experiences:
        st.markdown("### PROFESSIONAL EXPERIENCE")
        
        for exp in experiences:
            st.markdown(f"**{exp.get('title', 'Role')} - {exp.get('company', 'Company')}**")
            st.markdown(f"*{exp.get('start_date', 'Start Date')} - {exp.get('end_date', 'End Date')} | {exp.get('location', 'Location')}*")
            
            if exp.get("description"):
                st.markdown(exp.get("description"))
            
            achievements = exp.get("achievements", [])
            if achievements:
                if isinstance(achievements, str):
                    achievements = achievements.split("\n")
                
                for achievement in achievements:
                    if achievement.strip():
                        st.markdown(f"- {achievement.strip()}")
    
    # Education
    educations = resume_data.get("educations", [])
    if educations:
        st.markdown("### EDUCATION")
        
        for edu in educations:
            st.markdown(f"**{edu.get('degree', 'Degree')} in {edu.get('field_of_study', 'Field of Study')}**")
            st.markdown(f"*{edu.get('institution', 'Institution')} | {edu.get('start_date', 'Start Date')} - {edu.get('end_date', 'End Date')}*")
            
            if edu.get("gpa"):
                st.markdown(f"GPA: {edu.get('gpa')}")
    
    # Skills
    skills = resume_data.get("skills", [])
    if skills:
        st.markdown("### SKILLS")
        
        # Group skills by category
        skill_categories = {}
        for skill in skills:
            category = skill.get("category", "Other")
            if category not in skill_categories:
                skill_categories[category] = []
            skill_categories[category].append(skill.get("name", ""))
        
        # Display skills by category
        for category, skills in skill_categories.items():
            st.markdown(f"**{category}:** {', '.join(skills)}")
    
    # Download options
    st.subheader("Download Resume")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Generate PDF"):
            with st.spinner("Generating PDF..."):
                pdf_path = generate_pdf_resume(resume_data)
                
                if pdf_path:
                    # Read PDF file
                    with open(pdf_path, "rb") as f:
                        pdf_bytes = f.read()
                    
                    # Create download button
                    st.download_button(
                        label="Download PDF",
                        data=pdf_bytes,
                        file_name=f"resume_{datetime.now().strftime('%Y%m%d')}.pdf",
                        mime="application/pdf"
                    )
                else:
                    st.error("Error generating PDF. Please try again.")
    
    with col2:
        if st.button("Generate DOCX"):
            with st.spinner("Generating DOCX..."):
                docx_path = generate_docx_resume(resume_data)
                
                if docx_path:
                    # Read DOCX file
                    with open(docx_path, "rb") as f:
                        docx_bytes = f.read()
                    
                    # Create download button
                    st.download_button(
                        label="Download DOCX",
                        data=docx_bytes,
                        file_name=f"resume_{datetime.now().strftime('%Y%m%d')}.docx",
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                    )
                else:
                    st.error("Error generating DOCX. Please try again.")

def create_or_update_user(resume_data):
    """Create or update user in database."""
    try:
        session = get_session()
        
        # Check if user exists
        if st.session_state.user_id:
            user = session.query(User).filter(User.id == st.session_state.user_id).first()
            if not user:
                user = User()
        else:
            user = User()
        
        # Update basic info
        basic_info = resume_data.get("basic_info", {})
        user.name = basic_info.get("name", "")
        user.email = basic_info.get("email", "")
        user.phone = basic_info.get("phone", "")
        user.address = basic_info.get("address", "")
        user.linkedin = basic_info.get("linkedin", "")
        user.github = basic_info.get("github", "")
        user.website = basic_info.get("website", "")
        user.summary = basic_info.get("summary", "")
        
        # If new user, add to database
        if not user.id:
            session.add(user)
            session.commit()
            
            # Save user ID to session state
            st.session_state.user_id = user.id
        else:
            session.commit()
        
        # Update experiences
        if "experiences" in resume_data:
            # Delete existing experiences
            for exp in user.experiences:
                session.delete(exp)
            
            # Add new experiences
            for exp_data in resume_data.get("experiences", []):
                exp = Experience(
                    user_id=user.id,
                    company=exp_data.get("company", ""),
                    title=exp_data.get("title", ""),
                    location=exp_data.get("location", ""),
                    start_date=exp_data.get("start_date", ""),
                    end_date=exp_data.get("end_date", ""),
                    description=exp_data.get("description", ""),
                    achievements="\n".join(exp_data.get("achievements", [])) if isinstance(exp_data.get("achievements", []), list) else exp_data.get("achievements", "")
                )
                session.add(exp)
        
        # Update educations
        if "educations" in resume_data:
            # Delete existing educations
            for edu in user.educations:
                session.delete(edu)
            
            # Add new educations
            for edu_data in resume_data.get("educations", []):
                edu = Education(
                    user_id=user.id,
                    institution=edu_data.get("institution", ""),
                    degree=edu_data.get("degree", ""),
                    field_of_study=edu_data.get("field_of_study", ""),
                    location=edu_data.get("location", ""),
                    start_date=edu_data.get("start_date", ""),
                    end_date=edu_data.get("end_date", ""),
                    gpa=edu_data.get("gpa", ""),
                    description=edu_data.get("description", "")
                )
                session.add(edu)
        
        # Update skills
        if "skills" in resume_data:
            # Delete existing skills
            for skill in user.skills:
                session.delete(skill)
            
            # Add new skills
            for skill_data in resume_data.get("skills", []):
                skill = Skill(
                    user_id=user.id,
                    name=skill_data.get("name", ""),
                    category=skill_data.get("category", ""),
                    proficiency=skill_data.get("proficiency", "")
                )
                session.add(skill)
        
        # Commit all changes
        session.commit()
        
        logger.info(f"User {user.id} created/updated successfully")
        return user.id
        
    except Exception as e:
        logger.error(f"Error creating/updating user: {str(e)}")
        if session:
            session.rollback()
        return None 