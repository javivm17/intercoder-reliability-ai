#!/bin/bash

cat << "EOF"
              _     _     __  __       ____                     _                  
             | |   | |   |  \/  |     | __ )  __ _ ___  ___  __| |                 
             | |   | |   | |\/| |_____|  _ \ / _` / __|/ _ \/ _` |                 
             | |___| |___| |  | |_____| |_) | (_| \__ \  __/ (_| |                 
  ____       |_____|_____|_|__|_|     |____/ \__,_|___/\___|\__,_|   _             
 |  _ \  __ _| |_ __ _   / ___| | __ _ ___ ___(_)/ _(_) ___ __ _| |_(_) ___  _ __  
 | | | |/ _` | __/ _` | | |   | |/ _` / __/ __| | |_| |/ __/ _` | __| |/ _ \| '_ \ 
 | |_| | (_| | || (_| | | |___| | (_| \__ \__ \ |  _| | (_| (_| | |_| | (_) | | | |
 |____/ \__,_|\__\__,_|  \____|_|\__,_|___/___/_|_| |_|\___\__,_|\__|_|\___/|_| |_|
                                                                                   
EOF

# Step 1: Set up the virtual environment
echo "Setting up the virtual environment..."
python3 -m venv env

# Step 2: Activate the virtual environment
echo "Activating the virtual environment..."
source env/bin/activate

# Step 3: Install the required dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Step 4: Copy the .env.template to .env
echo "Creating .env file from template..."
cp .env.template .env

# Step 5: Replace placeholder in .env with user-provided API key
read -p "Please enter your GROQ API Key: " GROQ_API_KEY
sed -i '' "s/your_groq_api_key_here/$GROQ_API_KEY/" .env

echo "Setup complete!"
