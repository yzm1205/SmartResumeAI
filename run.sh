#!/bin/bash

# Check if Python is installed
if ! command -v python3 &>/dev/null; then
    echo "Python 3 is not installed. Please install Python 3 and try again."
    exit 1
fi

# Check if virtualenv is installed
if ! command -v python3 -m pip show virtualenv &>/dev/null; then
    echo "Installing virtualenv..."
    python3 -m pip install virtualenv
fi

# Create and activate virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m virtualenv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate || source venv/Scripts/activate

# Install requirements
echo "Installing requirements..."
pip install -r requirements.txt

# Install spacy model
echo "Installing spaCy model..."
python -m spacy download en_core_web_md

# Check if .env file exists, create if not
if [ ! -f ".env" ]; then
    echo "Creating .env file..."
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo "Please edit the .env file and set your OpenAI API key."
    else
        echo "OPENAI_API_KEY=your_openai_api_key_here" > .env
        echo "Please edit the .env file and set your OpenAI API key."
    fi
fi

# Run the application
echo "Starting SmartResumeAI..."
streamlit run main.py 