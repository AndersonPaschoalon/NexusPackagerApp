call Env/Scripts/activate.bat

echo Generating requirements.txt file...
pip freeze > requirements.txt

echo Building project
python -m PyInstaller --clean --onefile  --icon=.\Doc\logo2.ico NexusPackagerApp.py
