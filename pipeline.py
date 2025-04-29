import subprocess

# Step 1: Run data sync
print("🔁 Running copy_data.py...")
copy_result = subprocess.run(["python", "copy_data.py"])

if copy_result.returncode != 0:
    print("❌ copy_data.py failed. Stopping.")
    exit(1)
else:
    print("✅ Data updated successfully.")

# Step 2: Launch dashboard
print("🚀 Launching Streamlit dashboard...")
subprocess.run(["python", "launch_dashboard.py"])

