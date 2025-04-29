import os
import subprocess

# Step 1: Run the data updater script
print("Running data updater...")
os.system("python copy_data.py")

# Step 2: Launch the Streamlit dashboard
print("Launching Streamlit dashboard...")
subprocess.run(["streamlit", "run", "app.py"])
