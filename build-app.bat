call Env/Scripts/activate.bat
python -m PyInstaller --clean --onefile  --icon=.\Doc\logo2.ico NexusPackagerApp.py
rem robocopy /S /E ./App  dist/App