#!/bin/bash

# Exit on error
set -e

# Check if pyenv is installed
if ! command -v pyenv &> /dev/null; then
    echo "Installing pyenv..."
    curl https://pyenv.run | bash
    echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.bashrc
    echo 'command -v pyenv >/dev/null || export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.bashrc
    echo 'eval "$(pyenv init -)"' >> ~/.bashrc
    source ~/.bashrc
fi

# Install Python 3.11.0 if not already installed
if ! pyenv versions | grep -q "3.11.0"; then
    echo "Installing Python 3.11.0..."
    pyenv install 3.11.0
fi

# Set local Python version
pyenv local 3.11.0

# Install pipenv if not already installed
if ! command -v pipenv &> /dev/null; then
    echo "Installing pipenv..."
    pip install pipenv
fi

# Install dependencies
echo "Installing dependencies..."
pipenv install

echo "Setup complete! You can now run the script using:"
echo "pipenv run python url2markdown.py [URL]" 