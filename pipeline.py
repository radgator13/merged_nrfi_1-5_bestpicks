import subprocess

# Step 1: Run data sync
print("🔁 Running copy_data.py...")
copy_result = subprocess.run(["python", "copy_data.py"])

if copy_result.returncode != 0:
    print("❌ copy_data.py failed. Stopping.")
    exit(1)
else:
    print("✅ Data updated successfully.")

# Step 2: Launch dashboard (non-blocking)
print("🚀 Launching Streamlit dashboard...")
subprocess.Popen(["python", "launch_dashboard.py"])

# Step 3: Set GitHub remote (just in case)
print("🔧 Setting Git remote to radgator13/merged_nrfi_1-5_bestpicks.git...")
try:
    subprocess.run([
        "git", "remote", "set-url", "origin",
        "https://github.com/radgator13/merged_nrfi_1-5_bestpicks.git"
    ], check=True)
except subprocess.CalledProcessError:
    print("⚠️ Failed to set Git remote. Skipping Git push.")
    exit(1)

# Step 4: Push to GitHub
print("🚀 Pushing updates to GitHub...")
try:
    subprocess.run(["git", "add", "."], check=True)
    subprocess.run(["git", "commit", "-m", "Automated dashboard sync and launch"], check=True)
    subprocess.run(["git", "push"], check=True)
    print("✅ GitHub push successful!")
except subprocess.CalledProcessError:
    print("⚠️ GitHub push failed (maybe no changes to commit or auth issue).")
