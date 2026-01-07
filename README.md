# DiffAid
[![PyPI version](https://img.shields.io/pypi/v/diffaid)](https://pypi.org/project/diffaid/)
[![Python versions](https://img.shields.io/pypi/pyversions/diffaid)](https://pypi.org/project/diffaid/)
[![License](https://img.shields.io/pypi/l/diffaid)](https://github.com/natetowsley/diffaid/blob/master/LICENSE)

AI-assisted git diff review CLI that catches bugs before you commit.

## Features

- **Smart Analysis** - Uses Gemini AI to review code changes
- **CI Integration** - Exit codes for automated workflows  
- **Fast** - Reviews in seconds with Gemini Flash
- **Clean Output** - Color-coded findings in your terminal

## Setup

1. Get a free Gemini API key: https://aistudio.google.com/apikey

2. Set the environment variable:

<br>

   **Mac/Linux:**
```bash
   export GEMINI_API_KEY="your-key-here"
```

   **Windows (PowerShell):**
```powershell
   $env:GEMINI_API_KEY="your-key-here"
```

   **Permanent Setup (Mac/Linux):**
   Add to `~/.bashrc` or `~/.zshrc`:
```bash
   echo 'export GEMINI_API_KEY="your-key-here"' >> ~/.bashrc
   source ~/.bashrc
```

<br>

## Usage
Stage your changes and run:
```bash
git add .
diffaid
```
DiffAid will analyze your staged changes and report:

- **Errors** - Critical issues that should be fixed
- **Warnings** - Potential problems worth reviewing
- **Notes** - Suggestions for improvement

Example Output

```
Summary: Added user authentication with JWT tokens

ERROR: Hardcoded secret key detected
  → auth.py 15-17

WARNING: Missing error handling for database connection
  → db.py 42

NOTE: Consider adding rate limiting to login endpoint
  → routes.py 28

---
Found: 1 errors, 1 warnings, 1 notes
```
Exit Codes

- 0 - No errors found (warnings are OK)
- 1 - Errors found
- 2 - Tool error (git/API failure)

## Requirements

- Python 3.10+
- Git
- Gemini API key (free tier available)

## License
MIT License - see LICENSE file for details.

## Acknowledgments
Powered by Google Gemini
