import pandas as pd
import os
import shutil

# Paths
merged_data_folder = r"C:\Users\a1d3r\source\repos\Merged_NRFI-Innings_1-5\data"
nrfi_source_folder = r"C:\Users\a1d3r\source\repos\ScratchModelV3-5\data"
innings_source_folder = r"C:\Users\a1d3r\source\repos\Merged_NRFI-Innings_1-5\data"

# Files to process
files = [
    ("mlb_nrfi_predictions.csv", nrfi_source_folder),
    ("mlb_nrfi_results_full.csv", nrfi_source_folder),
    ("mlb_boxscores_1to5_model_full_predictions.csv", innings_source_folder)
]

for filename, source_folder in files:
    dest_file = os.path.join(merged_data_folder, filename)
    source_file = os.path.join(source_folder, filename)

    # Load source and destination
    if os.path.exists(dest_file):
        df_dest = pd.read_csv(dest_file)
    else:
        df_dest = pd.DataFrame()

    df_source = pd.read_csv(source_file)

    # Decide how to match rows
    if 'Game Date' in df_source.columns and 'Away Team' in df_source.columns and 'Home Team' in df_source.columns:
        merge_keys = ['Game Date', 'Away Team', 'Home Team']
    else:
        merge_keys = df_source.columns.tolist()  # fallback: all columns

    # Find new rows
if not df_dest.empty:
    # Merge to find truly new rows
    merged = df_dest.merge(df_source, on=merge_keys, how='right', indicator=True)
    new_rows = merged[merged['_merge'] == 'right_only'].drop(columns=['_merge'])

    # Align columns safely
    if not new_rows.empty:
        for col in df_dest.columns:
            if col not in new_rows.columns:
                new_rows[col] = pd.NA
        new_rows = new_rows[df_dest.columns]
    else:
        new_rows = pd.DataFrame(columns=df_dest.columns)
else:
    new_rows = df_source


    # Append new rows
    if not new_rows.empty:
        updated_df = pd.concat([df_dest, new_rows], ignore_index=True)
        # Optional: Backup before saving
        backup_file = dest_file.replace(".csv", "_backup.csv")
        shutil.copy2(dest_file, backup_file) if os.path.exists(dest_file) else None
        # Save
        updated_df.to_csv(dest_file, index=False)
        print(f"✅ {filename}: {len(new_rows)} new rows appended. Backup created as {backup_file if os.path.exists(backup_file) else 'None'}")
    else:
        print(f"ℹ️ {filename}: No new rows to append. Already up to date.")

print("\n🎯 Data update completed.")
