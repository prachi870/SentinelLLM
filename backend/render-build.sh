#!/usr/bin/env bash
# exit on error
set -o errexit

# Install system dependencies
apt-get update
apt-get install -y gcc g++ build-essential

# Install Python dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Download spacy model
python -m spacy download en_core_web_sm
