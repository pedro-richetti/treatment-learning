@echo off

call Scripts\activate.bat

python convertLogs.py

python treatmentLearner.py

python exportResults.py