# Stride Task Manager - Installation Guide

## Quick Install (Recommended)

1. **Extract the Files**
   - Extract all files from the ZIP archive to a folder of your choice
   - Example: `C:\Program Files\Stride` or `C:\Users\YourName\Stride`

2. **Run the Installer**
   - Double-click `INSTALL.bat`
   - If you see a Windows security warning, click "More info" → "Run anyway"

3. **Follow the Setup**
   - The installer will check for Python
   - Install required packages
   - Prompt for your OpenAI API Key (if not already set)
   - Create desktop and Start Menu shortcuts

4. **Launch Stride**
   - Double-click the "Stride" icon on your desktop
   - Or find it in your Start Menu

## Requirements

- **Windows 10 or later**
- **Python 3.8 or higher** - [Download here](https://www.python.org/downloads/)
- **OpenAI API Key** - [Get one here](https://platform.openai.com/api-keys)

## Manual Installation

If the automated installer doesn't work:

1. **Install Python packages:**
   ```powershell
   pip install openai pillow
   ```

2. **Set your API Key:**
   ```powershell
   setx OPENAI_API_KEY "your-api-key-here"
   ```

3. **Create a shortcut manually:**
   - Right-click on `main.py`
   - Select "Create shortcut"
   - Move shortcut to Desktop
   - Rename to "Stride"
   - Right-click shortcut → Properties
   - Change "Target" to: `pythonw.exe "C:\path\to\Final_Project\main.py"`
   - Change "Start in" to: `C:\path\to\Final_Project`
   - Click "Change Icon" and select `desktop_icon.png`

## Troubleshooting

### Python Not Found
- Download Python from [python.org](https://www.python.org/downloads/)
- During installation, check "Add Python to PATH"
- Restart your computer after installing

### API Key Issues
- Make sure you have an active OpenAI account
- Get your API key from [platform.openai.com/api-keys](https://platform.openai.com/api-keys)
- Set it as an environment variable or the installer will prompt you

### Shortcut Not Working
- Make sure all files are in the same folder
- Check that `main.py` exists in the installation folder
- Try running `main.py` directly with Python first

## Uninstallation

1. Delete the desktop shortcut
2. Delete the Start Menu shortcut from `%APPDATA%\Microsoft\Windows\Start Menu\Programs`
3. Delete the installation folder
4. (Optional) Remove the API key: `setx OPENAI_API_KEY ""`

## Support

For issues or questions, refer to the main README.md file.
