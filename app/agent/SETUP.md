# Setup Guide - Virtual Environment

This guide shows how to set up a virtual environment to avoid interfering with other projects.

## Quick Setup (Recommended)

### For Windows:
```powershell
# Navigate to agent directory
cd app\agent

# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Run the agent
python simple_agent.py dev
```

### For Linux/Mac:
```bash
# Navigate to agent directory
cd app/agent

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the agent
python simple_agent.py dev
```

## Detailed Steps

### 1. Create Virtual Environment

**Windows (PowerShell):**
```powershell
python -m venv venv
```

**Linux/Mac:**
```bash
python3 -m venv venv
```

This creates a `venv` folder with an isolated Python environment.

### 2. Activate Virtual Environment

**Windows (PowerShell):**
```powershell
.\venv\Scripts\Activate.ps1
```

**Windows (Command Prompt):**
```cmd
venv\Scripts\activate.bat
```

**Linux/Mac:**
```bash
source venv/bin/activate
```

You should see `(venv)` in your terminal prompt when activated.

### 3. Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**Note:** This will download models on first use (~800MB total).

### 4. Run the Agent

```bash
python simple_agent.py dev
```

### 5. Deactivate (when done)

```bash
deactivate
```

## Troubleshooting

### PowerShell Execution Policy Error (Windows)

If you get an execution policy error, run:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

Or use Command Prompt instead:
```cmd
venv\Scripts\activate.bat
```

### Python Not Found

Make sure Python 3.8+ is installed:
```bash
python --version  # or python3 --version
```

If needed, install Python from [python.org](https://www.python.org/downloads/)

### Permission Denied (Linux/Mac)

You may need to make the script executable:
```bash
chmod +x venv/bin/activate
```

### Install Specific Versions (if needed)

If you encounter compatibility issues, hover install specific versions:
```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

## Directory Structure

After setup, your directory should look like:
```
app/agent/
├── venv/              # Virtual environment (created)
├── requirements.txt
├── simple_agent.py
├── hf_stt.py
├── hf_llm.py
├── hf_tts.py
└── ...
```

**Note:** Add `venv/` to `.gitignore` if using git.

## Environment Variables

Create a `.env.local` file in the `app/agent` directory (optional):

```env
LIVEKIT_URL=your_livekit_url
LIVEKIT_API_KEY=your_api_key
LIVEKIT_API_SECRET=your_api_secret
AGENT_NAME=simple-voice-agent
```

## One-Time Setup Script (Optional)

**Windows (PowerShell):**
```powershell
# setup.ps1
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install -r requirements.txt
```

**Linux/Mac:**
```bash
# setup.sh
#!/bin/bash
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

Make executable: `chmod +x setup.sh`

## Notes

- Virtual environment keeps dependencies isolated from other projects
- You need to activate the venv each time you open a new terminal
- All dependencies install only in the venv (not system-wide)
- Model downloads (~800MB) happen on first run

