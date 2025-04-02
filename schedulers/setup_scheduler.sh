#!/bin/bash
# Setup script for Canvas API Scheduler

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Setting up Canvas API Scheduler...${NC}"

# Get the current directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
PROJECT_DIR="$( cd "$( dirname "${SCRIPT_DIR}" )" &> /dev/null && pwd )"
echo -e "Project directory: ${PROJECT_DIR}"

# Create .env file if it doesn't exist
if [ ! -f "${PROJECT_DIR}/config/.env" ]; then
    echo -e "Creating .env file from example..."
    cp "${PROJECT_DIR}/config/.env.example" "${PROJECT_DIR}/config/.env"
    echo -e "${YELLOW}Please edit the config/.env file with your email settings.${NC}"
fi

# Check if python3 is installed
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: Python 3 is not installed. Please install Python 3 first.${NC}"
    exit 1
fi

# Check if pip3 is installed
if ! command -v pip3 &> /dev/null; then
    echo -e "${RED}Error: pip3 is not installed. Please install pip3 first.${NC}"
    exit 1
fi

# Install required packages
echo -e "Installing required Python packages..."
pip3 install -r "${PROJECT_DIR}/requirements.txt"

# Create logs directory if it doesn't exist
mkdir -p "${PROJECT_DIR}/logs"

# Update the plist file with the correct paths
echo -e "Configuring LaunchAgent..."
PLIST_FILE="${PROJECT_DIR}/schedulers/com.bcm.canvas.grades.plist"
TEMP_PLIST="${PROJECT_DIR}/temp_plist.plist"

# Make a copy of the original plist
cp "${PLIST_FILE}" "${TEMP_PLIST}"

# Replace placeholder paths with actual paths
sed -i.bak "s|REPLACE_WITH_FULL_PATH_TO_PROJECT|${PROJECT_DIR}|g" "${TEMP_PLIST}"

# Create LaunchAgents directory if it doesn't exist
LAUNCH_AGENTS_DIR="${HOME}/Library/LaunchAgents"
mkdir -p "${LAUNCH_AGENTS_DIR}"

# Copy the plist file to LaunchAgents directory
cp "${TEMP_PLIST}" "${LAUNCH_AGENTS_DIR}/com.bcm.canvas.grades.plist"
rm "${TEMP_PLIST}" "${TEMP_PLIST}.bak"

# Set permissions
chmod 644 "${LAUNCH_AGENTS_DIR}/com.bcm.canvas.grades.plist"

# Load the LaunchAgent
echo -e "Loading LaunchAgent..."
launchctl unload "${LAUNCH_AGENTS_DIR}/com.bcm.canvas.grades.plist" 2>/dev/null
launchctl load "${LAUNCH_AGENTS_DIR}/com.bcm.canvas.grades.plist"

echo -e "${GREEN}Setup complete!${NC}"
echo -e "The Canvas API will now run:"
echo -e "  1. Daily at 8:00 AM"
echo -e "  2. When you log in (if it didn't run in the last 20 hours)"
echo -e ""
echo -e "${YELLOW}To uninstall:${NC}"
echo -e "  1. Run: ${GREEN}launchctl unload ~/Library/LaunchAgents/com.bcm.canvas.grades.plist${NC}"
echo -e "  2. Delete: ${GREEN}rm ~/Library/LaunchAgents/com.bcm.canvas.grades.plist${NC}"
echo -e ""
echo -e "${YELLOW}Don't forget to:${NC}"
echo -e "  1. Edit the ${GREEN}config/.env${NC} file with your email settings"
echo -e "  2. For Gmail, you'll need to use an app password: https://support.google.com/accounts/answer/185833"
echo -e ""
echo -e "To run a test now, execute: ${GREEN}python3 ${PROJECT_DIR}/main.py${NC}" 