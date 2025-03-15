#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if running on macOS, Linux, or Windows
OS="unknown"
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    OS="linux"
elif [[ "$OSTYPE" == "darwin"* ]]; then
    OS="macos"
elif [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    OS="windows"
fi

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}SmartResumeAI - Ollama Setup Helper${NC}"
echo -e "${GREEN}========================================${NC}"
echo

# Check if Ollama is installed
check_ollama() {
    if command -v ollama &> /dev/null; then
        echo -e "${GREEN}✓ Ollama is installed!${NC}"
        return 0
    else
        echo -e "${RED}✗ Ollama is not installed${NC}"
        return 1
    fi
}

# Install Ollama based on OS
install_ollama() {
    echo -e "${YELLOW}Installing Ollama...${NC}"
    
    case $OS in
        linux)
            echo -e "${YELLOW}Running Linux installation command...${NC}"
            curl -fsSL https://ollama.com/install.sh | sh
            ;;
        macos)
            echo -e "${YELLOW}For macOS, please download and install Ollama from the website:${NC}"
            echo -e "${YELLOW}https://ollama.com/download${NC}"
            echo -e "${YELLOW}Would you like to open the download page now? (y/n)${NC}"
            read -r open_browser
            if [[ $open_browser == "y" || $open_browser == "Y" ]]; then
                open "https://ollama.com/download"
            fi
            ;;
        windows)
            echo -e "${YELLOW}For Windows, please download and install Ollama from the website:${NC}"
            echo -e "${YELLOW}https://ollama.com/download${NC}"
            echo -e "${YELLOW}Unable to automatically install on Windows.${NC}"
            ;;
        *)
            echo -e "${RED}Unknown operating system. Please visit https://ollama.com/download${NC}"
            ;;
    esac
}

# Pull models
pull_models() {
    if ! check_ollama; then
        echo -e "${RED}Ollama is not installed. Cannot pull models.${NC}"
        return 1
    fi
    
    echo -e "${YELLOW}Which model would you like to pull?${NC}"
    echo "1) mistral (Recommended for good balance of performance and quality)"
    echo "2) llama2 (Meta's LLama 2 model)"
    echo "3) phi (Microsoft's small but capable model)"
    echo "4) neural-chat (Qualcomm's Neural Chat)"
    echo "5) gemma (Google's Gemma model)"
    echo "6) All of the above"
    echo "7) Skip"
    
    read -r choice
    
    case $choice in
        1)
            echo -e "${YELLOW}Pulling mistral model...${NC}"
            ollama pull mistral
            ;;
        2)
            echo -e "${YELLOW}Pulling llama2 model...${NC}"
            ollama pull llama2
            ;;
        3)
            echo -e "${YELLOW}Pulling phi model...${NC}"
            ollama pull phi
            ;;
        4)
            echo -e "${YELLOW}Pulling neural-chat model...${NC}"
            ollama pull neural-chat
            ;;
        5)
            echo -e "${YELLOW}Pulling gemma model...${NC}"
            ollama pull gemma
            ;;
        6)
            echo -e "${YELLOW}Pulling all models... This will download several GB of data.${NC}"
            ollama pull mistral
            ollama pull llama2
            ollama pull phi
            ollama pull neural-chat
            ollama pull gemma
            ;;
        7)
            echo -e "${YELLOW}Skipping model pull.${NC}"
            ;;
        *)
            echo -e "${RED}Invalid choice. Skipping model pull.${NC}"
            ;;
    esac
}

# Start Ollama
start_ollama() {
    if ! check_ollama; then
        echo -e "${RED}Ollama is not installed. Cannot start service.${NC}"
        return 1
    fi
    
    echo -e "${YELLOW}Starting Ollama service...${NC}"
    
    case $OS in
        linux)
            # For systemd-based systems
            if command -v systemctl &> /dev/null; then
                sudo systemctl start ollama
            else
                # Direct start on other Linux systems
                ollama serve &
                echo "Started Ollama in background"
            fi
            ;;
        macos)
            # On macOS, Ollama should be started via the app
            echo -e "${YELLOW}Please start Ollama by opening the application.${NC}"
            echo -e "${YELLOW}Would you like to open Ollama now? (y/n)${NC}"
            read -r open_app
            if [[ $open_app == "y" || $open_app == "Y" ]]; then
                open -a Ollama
            fi
            ;;
        windows)
            echo -e "${YELLOW}Please start Ollama by running the application from the Start menu.${NC}"
            ;;
        *)
            echo -e "${RED}Unknown operating system. Please start Ollama manually.${NC}"
            ;;
    esac
}

# Configure .env file for SmartResumeAI
configure_env() {
    if [ -f ".env" ]; then
        echo -e "${YELLOW}Updating .env file for Ollama...${NC}"
        # Check if MODEL_PROVIDER exists in .env
        if grep -q "MODEL_PROVIDER" .env; then
            # Replace the value
            sed -i.bak 's/MODEL_PROVIDER=.*/MODEL_PROVIDER=ollama/' .env
        else
            # Add the value
            echo "MODEL_PROVIDER=ollama" >> .env
        fi
        
        # Check if OLLAMA_MODEL exists in .env
        if grep -q "OLLAMA_MODEL" .env; then
            # Replace the value
            sed -i.bak 's/OLLAMA_MODEL=.*/OLLAMA_MODEL=mistral/' .env
        else
            # Add the value
            echo "OLLAMA_MODEL=mistral" >> .env
        fi
        
        # Check if OLLAMA_HOST exists in .env
        if grep -q "OLLAMA_HOST" .env; then
            # Replace the value
            sed -i.bak 's/OLLAMA_HOST=.*/OLLAMA_HOST=http:\/\/localhost:11434/' .env
        else
            # Add the value
            echo "OLLAMA_HOST=http://localhost:11434" >> .env
        fi
        
        echo -e "${GREEN}✓ .env file updated for Ollama!${NC}"
    elif [ -f ".env.example" ]; then
        echo -e "${YELLOW}Creating .env file from .env.example...${NC}"
        cp .env.example .env
        # Now update it
        configure_env
    else
        echo -e "${YELLOW}Creating new .env file...${NC}"
        cat > .env << EOF
MODEL_PROVIDER=ollama
OLLAMA_MODEL=mistral
OLLAMA_HOST=http://localhost:11434
EOF
        echo -e "${GREEN}✓ .env file created for Ollama!${NC}"
    fi
}

# Display Ollama info and status
show_ollama_info() {
    if ! check_ollama; then
        echo -e "${RED}Ollama is not installed. Cannot show info.${NC}"
        return 1
    fi
    
    echo -e "${GREEN}Ollama Information:${NC}"
    echo -e "${YELLOW}================${NC}"
    
    # Show version
    echo -e "${YELLOW}Version:${NC}"
    ollama --version
    
    # List models
    echo -e "\n${YELLOW}Installed Models:${NC}"
    ollama list
    
    # Check if Ollama is running
    echo -e "\n${YELLOW}Server Status:${NC}"
    curl -s http://localhost:11434/api/version > /dev/null
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Ollama server is running${NC}"
    else
        echo -e "${RED}✗ Ollama server is not running${NC}"
    fi
}

# Main menu
main() {
    while true; do
        echo
        echo -e "${GREEN}What would you like to do?${NC}"
        echo "1) Check if Ollama is installed"
        echo "2) Install Ollama"
        echo "3) Pull models for Ollama"
        echo "4) Start Ollama service"
        echo "5) Configure SmartResumeAI to use Ollama"
        echo "6) Show Ollama information and status"
        echo "7) Exit"
        
        read -r choice
        
        case $choice in
            1)
                check_ollama
                ;;
            2)
                install_ollama
                ;;
            3)
                pull_models
                ;;
            4)
                start_ollama
                ;;
            5)
                configure_env
                ;;
            6)
                show_ollama_info
                ;;
            7)
                echo -e "${GREEN}Exiting...${NC}"
                break
                ;;
            *)
                echo -e "${RED}Invalid choice. Please try again.${NC}"
                ;;
        esac
    done
}

# Run the main function
main 