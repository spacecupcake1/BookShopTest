@echo off
cd .
call env\Scripts\activate
pytest > C:\path\to\your\logs\test_results_%DATE%.log 2>&1
