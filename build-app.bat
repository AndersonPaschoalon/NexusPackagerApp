call Env/Scripts/activate.bat
python -m PyInstaller --onefile  --icon=.\Doc\logo2.ico NexusBuildApp.py
rem robocopy /S /E ./App  dist/App