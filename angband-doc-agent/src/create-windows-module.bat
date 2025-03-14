@echo off
echo Activating virtual environment...
cd ..
call venv\Scripts\activate

echo Creating Windows module documentation...
cd src
python windows-module-creator.py