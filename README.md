# SmartResumeAI: AI-Powered Resume Tailoring for Job Success

## **Framework Overview**
- Developed an AI-powered resume optimization assistant leveraging GPT-4-turbo and LangChain for personalized resume modifications based on job descriptions.
- Implemented a vector-based job matching system using ChromaDB and LangChain VectorDB, enhancing resume relevance through NLP-based keyword alignment.
- Built an interactive chatbot interface in Streamlit, allowing users to iteratively modify resumes and generate ATS-friendly one-page resumes in PDF/DOCX format.
- Supports both OpenAI's API models and free open source models (like Mistral, Llama 2, Phi) via Ollama for local inference.

## **Features**

- **AI-Powered Resume Parsing**: Extract structured data from resumes in PDF, DOCX, or TXT formats.
- **Interactive Resume Chat**: Refine your resume through natural language conversation.
- **Job Description Analysis**: Extract key requirements and skills from job listings.
- **Resume Optimization**: Tailor your resume for specific job descriptions.
- **ATS-Friendly Resume Generation**: Create optimized PDF/DOCX resumes for applicant tracking systems.
- **Resume Analysis**: Get insights and improvement suggestions for your resume.
- **Open Source Model Support**: Choose between OpenAI API or free local open source models via Ollama.

## **Installation**

### Prerequisites

- Python 3.9 or higher
- OpenAI API key (only if using OpenAI models)
- Ollama (only if using open source models)

### Setup Instructions

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/SmartResumeAI.git
   cd SmartResumeAI
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Install spaCy model**:
   ```bash
   python -m spacy download en_core_web_md
   ```

4. **Set up environment variables**:
   Create a `.env` file in the root directory with the following:
   ```
   # Choose your model provider
   MODEL_PROVIDER=openai  # or ollama for open source models
   
   # OpenAI configuration (if using OpenAI)
   OPENAI_API_KEY=your_openai_api_key_here
   LLM_MODEL=gpt-4-turbo
   
   # Ollama configuration (if using open source models)
   OLLAMA_MODEL=mistral  # options: mistral, llama2, phi, neural-chat, etc.
   OLLAMA_HOST=http://localhost:11434
   ```

5. **Set up Ollama** (Optional - only for open source models):
   
   Install Ollama by following instructions at [ollama.ai](https://ollama.ai)
   
   OR run our helper script:
   ```bash
   ./setup_ollama.sh
   ```
   
   After installing Ollama, pull your preferred model:
   ```bash
   ollama pull mistral  # or llama2, phi, neural-chat, etc.
   ```

## **Usage**

1. **Run the application**:
   ```bash
   streamlit run main.py
   ```

2. **Access the web interface**:
   Open your browser and navigate to `http://localhost:8501`

3. **Choose your AI model**:
   - Go to "Settings" in the sidebar to choose between:
     - **OpenAI models** - Better quality but requires API key and has usage costs
     - **Open source models** - Free but requires local installation of Ollama

4. **Upload your resume**:
   - Navigate to "Resume Upload" in the sidebar
   - Upload your resume in PDF, DOCX, or TXT format
   - Or manually enter your resume information

5. **Optimize for job descriptions**:
   - Go to "Job Matching" in the sidebar
   - Paste a job description
   - Analyze the job requirements
   - Click "Optimize Resume" to tailor your resume for the job

6. **Generate and download your resume**:
   - Navigate to "Generate Resume" in the sidebar
   - Preview your optimized resume
   - Download in PDF or DOCX format

## **Project Structure**

```
SmartResumeAI/
├── app/
│   ├── core/              # Core AI functionality
│   ├── database/          # Database and vector store modules
│   ├── frontend/          # Streamlit UI components
│   ├── pdf_generation/    # PDF and DOCX generation
│   └── utils/             # Utility functions
├── data/
│   ├── sample/            # Sample data for testing
│   ├── uploads/           # Uploaded resumes
│   ├── vectordb/          # Vector database storage
│   └── generated_resumes/ # Generated PDF/DOCX files
├── main.py                # Main application entry point
├── requirements.txt       # Project dependencies
├── setup_ollama.sh        # Helper script for Ollama setup
└── .env.example           # Example environment variables
```

## **Open Source Models vs. OpenAI**

SmartResumeAI supports two types of AI models:

### 1. OpenAI Models (Default)
- **Pros**: Higher quality responses, no local setup, consistent performance
- **Cons**: Requires API key, incurs usage costs, sends data to OpenAI servers
- **Models**: GPT-3.5-Turbo, GPT-4-Turbo

### 2. Open Source Models (via Ollama)
- **Pros**: Completely free, privacy-focused (runs locally), no usage limits
- **Cons**: Requires local installation, performance depends on hardware, somewhat lower quality
- **Models**: 
  - Mistral (7B) - Recommended for best balance
  - Llama 2 (7B) - Meta's open source model
  - Phi - Microsoft's small but capable model
  - Neural-chat - Qualcomm's conversational model
  - Gemma - Google's Gemma model
  - And more...

To switch between model types, go to "Settings" in the app sidebar.

## **Technologies Used**

- **LLM & AI**: OpenAI GPT-4-turbo, Ollama (open source models), LangChain
- **Vector Database**: ChromaDB
- **NLP & Text Processing**: spaCy, PyPDF2, docx2txt
- **PDF/DOCX Generation**: ReportLab, python-docx
- **Web Framework**: Streamlit
- **Database**: SQLAlchemy (SQLite)

## **Contributing**

Contributions are welcome! Please feel free to submit a Pull Request.

## **License**

This project is licensed under the MIT License - see the LICENSE file for details.

## **Acknowledgements**

- OpenAI for providing the GPT API
- The LangChain team for their fantastic framework
- The Streamlit team for making web app development simple and powerful
- The Ollama project for making open source models accessible

---

## **1. Features & Workflow**

### **0. Input & Local Database Creation**
- Users provide their resumes, personal websites, or descriptions via the chat interface.
- The AI agent extracts and structures relevant information.
- A local database is created to store:
  - Work experience
  - Education
  - Skills
  - Certifications
  - Projects
  - Publications
  - Achievements

### **1. Interactive Chatbot for Resume Modification**
- Users interact with an AI chatbot to refine and edit resumes.
- Modifications can include:
  - Rewording achievements
  - Adding quantitative impact
  - Changing tone and format
- The chatbot ensures that the resume remains concise, optimized, and job-relevant.

### **2. Local Database for Resume Enhancement**
- Stores and updates user information dynamically.
- Identifies missing sections and suggests enhancements.
- Ensures ATS compliance by maintaining an optimal resume structure.

### **3. Job Description-Based Resume Customization**
- Users can provide a job description or specify modifications.
- AI extracts key job requirements and compares them with stored user data.
- The resume is optimized by:
  - Aligning keywords with the job description.
  - Highlighting relevant skills and experience.
  - Rephrasing content to emphasize key qualifications.
- Users click the "Generate Resume" button to finalize updates.

### **4. One-Page Resume Generation & Export**
- Generates an **ATS-friendly, concise one-page resume**.
- Allows users to download resumes in **PDF** or **DOCX** format.

---

## **2. Technical Stack (Implementation Possibilities)**

### **1. Chatbot**
- **LLM**: OpenAI **GPT-4-turbo** (for resume modifications and job relevance analysis)
- **Personalization**: RAG-based (Retrieval-Augmented Generation) using **LangChain**
- **Job Matching**: Embedding-based similarity search to enhance resume alignment with job descriptions

### **2. Database**
- **Vector Database**: **ChromaDB** or **LangChain DB** (for storing user profiles and resume embeddings)
- **Structured Data**: **SQLite/PostgreSQL** (for managing job-specific user data)

### **3. Processing**
- **Resume Parsing**:
  - NLP-based: `spaCy`, `PyPDF2`, `docx2txt`
  - AI-Assisted Resume Parsing using **LLMs** for entity recognition and structuring
- **Text Embeddings for Job Matching**:
  - **LangChain VectorDB** (e.g., FAISS, Weaviate, or ChromaDB)
  - **Embedding Model**: OpenAI `text-embedding-ada-002`

### **4. Frontend**
- **Framework**: **Streamlit** (for interactive UI, chatbot, and resume customization)
- **Alternatives**: **Gradio**, **React/Next.js** (for enhanced customization)

### **5. Resume Generation & Export**
- **Formatting & Optimization**: Ensures **ATS-friendly** structure
- **Document Generation**:
  - **PDF Export**: `ReportLab`, `pdfkit`
  - **DOCX Export**: `python-docx`

---

## **3. Why SmartResumeAI?**
✅ **AI-Powered Personalization**: Automatically adapts resumes to match job descriptions.  
✅ **High ATS Score Optimization**: Ensures job applications pass automated screenings.  
✅ **User-Friendly Chatbot Interface**: Provides real-time feedback and edits.  
✅ **Efficient Job Matching**: Uses NLP and vector embeddings to align resumes with job requirements.  
✅ **Professional Resume Formatting**: Generates polished, ATS-compatible documents.  

---

## **4. Future Enhancements**
- **Multi-Language Support**: AI-assisted resume generation for non-English job markets.
- **Cover Letter Generation**: Automated job-specific cover letters.
- **LinkedIn Profile Optimization**: AI-driven suggestions for profile updates.
- **Resume Score Analyzer**: AI-powered scoring and recommendations to improve resume effectiveness.

---

🚀 **SmartResumeAI** is designed to empower job seekers by making resume optimization seamless, effective, and personalized!

