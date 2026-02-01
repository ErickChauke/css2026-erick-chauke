# Helper script: runs the main app
import subprocess

# Use this script to run the active app: app.py
subprocess.Popen(["streamlit", "run", "app.py"], shell=True)
