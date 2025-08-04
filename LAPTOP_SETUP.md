# White Raven Pourhouse - Laptop Setup Guide

## System Requirements

### Required Software
1. **Python 3.8 or higher**
   - Download from: https://www.python.org/downloads/
   - During installation, check "Add Python to PATH"

2. **Git (optional but recommended)**
   - Download from: https://git-scm.com/downloads

### Setup Steps

1. **Copy the entire project folder** to your laptop

2. **Open Command Prompt/Terminal** in the project folder

3. **Create virtual environment** (recommended):
   ```bash
   python -m venv venv
   
   # Windows:
   venv\Scripts\activate
   
   # Mac/Linux:
   source venv/bin/activate
   ```

4. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

5. **Test the setup**:
   ```bash
   python manage.py check
   ```

6. **Start the development server**:
   ```bash
   python manage.py runserver 8001
   ```

7. **Visit**: http://127.0.0.1:8001

## Quick Start Script

### Windows (save as `setup_laptop.bat`):
```batch
@echo off
echo Setting up White Raven Pourhouse on laptop...
python -m venv venv
call venv\Scripts\activate
pip install -r requirements.txt
python manage.py check
echo Setup complete! Run 'start_server_8001.bat' to launch the site.
pause
```

### Mac/Linux (save as `setup_laptop.sh`):
```bash
#!/bin/bash
echo "Setting up White Raven Pourhouse on laptop..."
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py check
echo "Setup complete! Run 'python manage.py runserver 8001' to launch."
```

## Troubleshooting

### If you get "python not found":
- Install Python from python.org
- Make sure "Add to PATH" was checked during installation
- Restart command prompt after installation

### If pip install fails:
- Try: `python -m pip install --upgrade pip`
- Then: `pip install -r requirements.txt`

### If Django commands don't work:
- Make sure you're in the project folder
- Activate virtual environment first
- Check that manage.py exists in current directory

## What's Included in Project
- ✅ All source code
- ✅ SQLite database with your data
- ✅ Static files and media uploads
- ✅ All configuration
- ✅ Requirements and documentation

## External Dependencies (Need to Install)
- ❌ Python (install on laptop)
- ❌ Virtual environment packages (pip install)

## File to Transfer
**Copy this entire folder to your laptop:**
```
White  Raven  Pourhouse/
├── All project files
└── (Everything in this directory)
```

The project is completely self-contained once Python is installed!