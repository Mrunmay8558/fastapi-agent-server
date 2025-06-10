#!/bin/bash

echo "Setting up FastAPI Agent Server..."

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install core dependencies first
echo "Installing core dependencies..."
pip install fastapi==0.104.1 uvicorn[standard]==0.24.0

# Install database dependencies
echo "Installing database dependencies..."
pip install motor==3.3.2 pymongo==4.6.0

# Install auth and validation dependencies
echo "Installing auth dependencies..."
pip install python-jose[cryptography]==3.3.0 passlib[bcrypt]==1.7.4 python-dotenv==1.0.0

# Install remaining dependencies
echo "Installing remaining dependencies..."
pip install python-multipart==0.0.6 httpx==0.25.2

# Try to install pydantic (may need to use pre-built wheel)
echo "Installing pydantic..."
pip install pydantic pydantic-settings email-validator

# Create .env file from example
if [ ! -f .env ]; then
    cp .env.example .env
    echo "Created .env file from .env.example - please update with your settings"
fi

echo "Setup complete! To start the server:"
echo "1. Activate virtual environment: source venv/bin/activate"
echo "2. Start MongoDB (docker run -d -p 27017:27017 mongo:7)"
echo "3. Run server: python run.py"