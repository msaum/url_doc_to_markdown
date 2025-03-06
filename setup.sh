#!/bin/bash

# Exit on error
set -e

# Check if conda is installed
if ! command -v conda &> /dev/null; then
    echo "Installing Anaconda..."
    # Download Anaconda installer
    wget https://repo.anaconda.com/archive/Anaconda3-2024.02-1-Linux-x86_64.sh -O anaconda.sh
    # Install Anaconda silently
    bash anaconda.sh -b -p $HOME/anaconda3
    # Add conda to PATH
    echo 'export PATH="$HOME/anaconda3/bin:$PATH"' >> ~/.bashrc
    # Initialize conda
    $HOME/anaconda3/bin/conda init bash
    source ~/.bashrc
    # Clean up installer
    rm anaconda.sh
else
    echo "Anaconda is already installed"
fi

# Create or activate url2md environment
if ! conda env list | grep -q "url2md"; then
    echo "Creating url2md environment..."
    conda create -n url2md python=3.11 -y
else
    echo "url2md environment already exists"
fi

# Activate the environment
echo "Activating url2md environment..."
conda activate url2md

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

echo "Setup complete! You can now run the script using:"
echo "conda activate url2md && python url2md.py [URL]" 