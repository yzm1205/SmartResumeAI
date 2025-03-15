#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if Python is installed
if ! command -v python3 &>/dev/null; then
    echo -e "${RED}Python 3 is not installed. Please install Python 3 and try again.${NC}"
    exit 1
fi

# Check if virtualenv is installed
if ! command -v python3 -m pip show virtualenv &>/dev/null; then
    echo -e "${YELLOW}Installing virtualenv...${NC}"
    python3 -m pip install virtualenv
fi

# Create and activate virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}Creating virtual environment...${NC}"
    python3 -m virtualenv venv
fi

# Activate virtual environment
echo -e "${YELLOW}Activating virtual environment...${NC}"
source venv/bin/activate || source venv/Scripts/activate

# Install requirements
echo -e "${YELLOW}Installing requirements...${NC}"
pip install -r requirements.txt

# Install spacy model
echo -e "${YELLOW}Installing spaCy model...${NC}"
python -m spacy download en_core_web_md

# Check if .env file exists, create if not
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}Creating .env file...${NC}"
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo -e "${YELLOW}Please edit the .env file and set your model preferences.${NC}"
    else
        echo "OPENAI_API_KEY=your_openai_api_key_here" > .env
        echo "MODEL_PROVIDER=openai" >> .env
        echo "LLM_MODEL=gpt-4-turbo" >> .env
        echo "OLLAMA_MODEL=mistral" >> .env
        echo "OLLAMA_HOST=http://localhost:11434" >> .env
        echo -e "${YELLOW}Created .env file with default settings.${NC}"
    fi
    
    # Ask if user wants to use Ollama
    echo
    echo -e "${YELLOW}Would you like to use free open source models via Ollama? (y/n)${NC}"
    read -r use_ollama
    
    if [[ $use_ollama == "y" || $use_ollama == "Y" ]]; then
        # Check if Ollama is installed
        if ! command -v ollama &>/dev/null; then
            echo -e "${YELLOW}Ollama is not installed. Would you like to set it up now? (y/n)${NC}"
            read -r setup_ollama
            
            if [[ $setup_ollama == "y" || $setup_ollama == "Y" ]]; then
                # Run the Ollama setup script
                if [ -f "./setup_ollama.sh" ]; then
                    chmod +x ./setup_ollama.sh
                    ./setup_ollama.sh
                else
                    echo -e "${RED}setup_ollama.sh not found. Please install Ollama manually from ollama.ai${NC}"
                fi
            else
                echo -e "${YELLOW}You can set up Ollama later by running ./setup_ollama.sh${NC}"
            fi
        else
            echo -e "${GREEN}Ollama is already installed.${NC}"
            
            # Update .env to use Ollama
            if [ -f ".env" ]; then
                # Set MODEL_PROVIDER to ollama
                sed -i.bak 's/MODEL_PROVIDER=.*/MODEL_PROVIDER=ollama/' .env
                echo -e "${GREEN}Updated .env to use Ollama.${NC}"
                
                # Check if the model is installed
                echo -e "${YELLOW}Checking if the Mistral model is installed...${NC}"
                if ! ollama list | grep -q "mistral"; then
                    echo -e "${YELLOW}Mistral model not found. Would you like to download it now? (y/n)${NC}"
                    read -r download_model
                    
                    if [[ $download_model == "y" || $download_model == "Y" ]]; then
                        echo -e "${YELLOW}Downloading Mistral model (this may take a while)...${NC}"
                        ollama pull mistral
                    fi
                else
                    echo -e "${GREEN}Mistral model is already installed.${NC}"
                fi
            fi
        fi
    else
        echo -e "${YELLOW}You will use OpenAI models. Please set your OPENAI_API_KEY in the .env file.${NC}"
    fi
fi

# Run the application
echo -e "${GREEN}Starting SmartResumeAI...${NC}"
streamlit run main.py 