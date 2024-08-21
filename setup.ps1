Write-Host @"
              _     _     __  __       ____                     _                  
             | |   | |   |  \/  |     | __ )  __ _ ___  ___  __| |                 
             | |   | |   | |\/| |_____|  _ \ / _` / __|/ _ \/ _` |                 
             | |___| |___| |  | |_____| |_) | (_| \__ \  __/ (_| |                 
  ____       |_____|_____|_|__|_|     |____/ \__,_|___/\___|\__,_|   _             
 |  _ \  __ _| |_ __ _   / ___| | __ _ ___ ___(_)/ _(_) ___ __ _| |_(_) ___  _ __  
 | | | |/ _` | __/ _` | | |   | |/ _` / __/ __| | |_| |/ __/ _` | __| |/ _ \| '_ \ 
 | |_| | (_| | || (_| | | |___| | (_| \__ \__ \ |  _| | (_| (_| | |_| | (_) | | | |
 |____/ \__,_|\__\__,_|  \____|_|\__,_|___/___/_|_| |_|\___\__,_|\__|_|\___/|_| |_|

"@

# Step 1: Set up the virtual environment
Write-Host "Setting up the virtual environment..."
python -m venv env

# Step 2: Activate the virtual environment
Write-Host "Activating the virtual environment..."
.\env\Scripts\Activate

# Step 3: Install the required dependencies
Write-Host "Installing dependencies..."
pip install -r requirements.txt

# Step 4: Copy the .env.template to .env
Write-Host "Creating .env file from template..."
Copy-Item .env.template .env

# Step 5: Replace placeholder in .env with user-provided API key
$groqApiKey = Read-Host "Please enter your GROQ API Key"
(Get-Content .env) -replace 'your_groq_api_key_here', $groqApiKey | Set-Content .env

Write-Host "Setup complete!"
