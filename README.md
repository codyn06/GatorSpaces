# GatorSpaces

## Clone the Repository

First, clone the repository from GitHub:

```powershell
git clone https://github.com/codyn06/GatorSpaces
cd GatorSpaces
```

## Setup (Python virtual environment)

These steps create and activate a Python virtual environment, install required packages, and install Playwright browsers. The examples assume PowerShell on Windows; Unix/macOS shells are noted as well.

Windows (PowerShell):

1. Create the venv (runs in the repository root):

```powershell
python -m venv .venv
```

2. Activate the venv:

```powershell
& '.\.venv\Scripts\Activate.ps1'
```

3. Install packages (example):

```powershell
python -m pip install --upgrade pip
python -m pip install flask playwright
# If you have a requirements.txt: python -m pip install -r requirements.txt
```

4. Install Playwright browsers (required by playwright):

```powershell
python -m playwright install chromium
```

Unix / macOS (bash / zsh):

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install flask playwright
python -m playwright install chromium
```

Notes:

- After activating the venv, run the app with: `python tester.py`.
- After running, you will see an IP address in the console (something like http://127.0.0.1:5000). Click on this IP link to open the app in your browser.
- Keep Playwright browser installation on systems that will actually run the scraper (server or local dev). Serverless platforms may not support large browser binaries.
