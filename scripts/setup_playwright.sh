#!/bin/bash
# Setup script for Playwright browser automation in WSL/Linux

echo "Installing Playwright system dependencies..."
echo "This script requires sudo access to install system packages."
echo ""

# Check if running in WSL
if grep -qi microsoft /proc/version; then
    echo "Detected WSL environment"
fi

# Install system dependencies required by Playwright
echo "Installing required system libraries..."
sudo apt-get update
sudo apt-get install -y libnspr4 libnss3 libasound2t64 libatk1.0-0 libatk-bridge2.0-0 \
    libcups2 libdrm2 libxkbcommon0 libxcomposite1 libxdamage1 libxfixes3 \
    libxrandr2 libgbm1 libpango-1.0-0 libcairo2

# Install Playwright browsers
echo ""
echo "Installing Playwright browsers..."
playwright install chromium

echo ""
echo "Setup complete! You can now run E2E tests with Playwright."
