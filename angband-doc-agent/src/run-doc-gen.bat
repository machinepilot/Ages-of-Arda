@echo off
REM Run the documentation generator
echo Running Angband Documentation Generator...
python document-angband.py --verbose --max-files 20
echo Documentation generation complete!
pause 