import pandas as pd
import os
import shutil

# Paths
merged_data_folder = r"C:\Users\a1d3r\source\repos\Merged_NRFI-Innings_1-5\data"
nrfi_source_folder = r"C:\Users\a1d3r\source\repos\ScratchModelV3-5\data"
innings_source_folder = r"C:\Users\a1d3r\source\repos\MLB-Innings-1-5\data"  # ✅ Your live prediction source

# Files to process
files = [
    ("mlb_nrfi_predictions.csv", nrfi_source_folder),
    ("mlb_nrfi_results_full.csv", nrfi_source_folder),
    ("mlb_boxscores_1to5_model_full_predictions.csv", innings_source_folder)
]

for filename, source_folder in files:
    dest_file = os.path.join(merged_data_folder, filename)
    source_file = os.path.join(source_folder, filename)

    if not os.path.exists(source_file):
        print(f"⚠️ Skipping {filename}: source file does not exist.")
        continue

    df_source = pd.read_csv(source_file)
    df_dest = pd.read_csv(dest_file) if os.path.exists(dest_file) else pd.DataFrame()

    # Normalize Game Date format
    if 'Game Date' in df_source.columns:
        df_source['Game Date'] = pd.to_datetime(df_source['Game Date']).dt.strftime('%Y-%m-%d')
    if not df_dest.empty and 'Game Date' in df_dest.columns:
        df_dest['Game Date'] = pd.to_datetime(df_dest['Game Date']).dt.strftime('%Y-%m-%d')

    # Merge keys
    if all(col in df_source.columns for col in ['Game Date', 'Away Team', 'Home Team']):
        merge_keys = ['Game Date', 'Away Team', 'Home Team']
    else:
        merge_keys = df_source.columns.tolist()

    # Remove matching rows in destination so source rows override them
    if not df_dest.empty:
        df_dest = df_dest.merge(
            df_source[merge_keys],
            on=merge_keys,
            how='left',
            indicator=True
        )
        df_dest = df_dest[df_dest['_merge'] == 'left_only'].drop(columns=['_merge'])

    # Append updated source rows
    final_df = pd.concat([df_dest, df_source], ignore_index=True)

    # Backup and save
    backup_file = dest_file.replace(".csv", "_backup.csv")
    if os.path.exists(dest_file):
        shutil.copy2(dest_file, backup_file)

    final_df.to_csv(dest_file, index=False)
    print(f"✅ {filename}: Overwrote {len(df_source)} rows from source. Backup saved to {backup_file}")

print("\n🎯 Data sync complete.")
