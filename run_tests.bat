@echo off
cd C:\path\to\your\project
call env\Scripts\activate
pytest > C:\path\to\your\logs\test_results_%DATE%.log 2>&1
