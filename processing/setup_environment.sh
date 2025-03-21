#!/bin/bash
# Setup environment for Tolkien ePub processing

# Colors for pretty output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Setting up environment for Tolkien ePub processing...${NC}"

# Create necessary directories
echo -e "${YELLOW}Creating necessary directories...${NC}"
mkdir -p processing/logs
mkdir -p processing/schemas/entity_lists
mkdir -p processing/temp
mkdir -p processing/epub_content
mkdir -p processing/json_output
mkdir -p processing/consolidated
mkdir -p processing/checkpoints
mkdir -p .memory-bank

# Install Python dependencies
echo -e "${YELLOW}Installing Python dependencies...${NC}"
pip install -r processing/requirements.txt

# Check installation success
if [ $? -eq 0 ]; then
    echo -e "${GREEN}Python dependencies installed successfully.${NC}"
else
    echo -e "${RED}Failed to install Python dependencies. Exiting.${NC}"
    exit 1
fi

# Run NLP setup
echo -e "${YELLOW}Running NLP setup...${NC}"
python processing/setup_nlp.py

# Check setup success
if [ $? -eq 0 ]; then
    echo -e "${GREEN}NLP setup completed successfully.${NC}"
else
    echo -e "${RED}NLP setup failed. Exiting.${NC}"
    exit 1
fi

# Run setup tests
echo -e "${YELLOW}Running setup tests...${NC}"
python processing/test_setup.py

# Check test success
if [ $? -eq 0 ]; then
    echo -e "${GREEN}Setup tests passed successfully.${NC}"
else
    echo -e "${RED}Setup tests failed. Please check the output above.${NC}"
    exit 1
fi

echo -e "${GREEN}Environment setup completed successfully!${NC}"
echo -e "${GREEN}You can now run the Tolkien ePub processing pipeline.${NC}" 