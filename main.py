import pandas as pd
import os
import numpy as np
import json
import shutil

# Define the paths
input_directory = '/Users/marg0tm/rdoc-beh/results/wide'  # Directory with updated CSV QC files 
old_matrix_directory = os.path.expanduser('~/Desktop/rdoc_behavioral_matrix_old/')  # Directory with old CSV QC files
output_directory = 'new_rdoc_behavioral_matrix'  # Directory to save the updated CSV files
desktop_output_directory = os.path.expanduser('~/Desktop/new_rdoc_behavioral_matrix')  # Directory on desktop to save the files

# Function to format numbers
def format_number(x):
    if pd.isna(x) or isinstance(x, str):
        return x
    # Check if the number is effectively a whole number
    if abs(x - round(x)) < 1e-10:
        return f"{int(round(x))}"
    else:
        # Format with up to 4 decimal places, removing trailing zeros
        formatted = f"{x:.4f}".rstrip('0').rstrip('.')
        return formatted

def update_values_with_new_data(old_df, new_df):
    # Create a copy of the old dataframe to avoid modifying it directly
    updated_df = old_df.copy()
    
    # Iterate through each row in the new dataframe
    for _, new_row in new_df.iterrows():
        # Find matching rows in the old dataframe based on sub_id and date_time
        mask = (updated_df['sub_id'] == new_row['sub_id']) & (updated_df['date_time'] == new_row['date_time'])
        
        if mask.any():
            # Update all columns that exist in both dataframes
            for col in new_row.index:
                if col in updated_df.columns:
                    updated_df.loc[mask, col] = new_row[col]
    
    return updated_df

# Load pristine subjects
with open('/Users/marg0tm/rdoc-beh/qa/pristine_subjects.json', 'r') as f:
    pristine_subjects = json.load(f)
pristine_ids = set(pristine_subjects['ids'])

# Define subject to exclude
excluded_subject = '665368b3a0704ee687e448a0'

# Create output directory if it doesn't exist
os.makedirs(output_directory, exist_ok=True)

# Collect existing subject IDs from old matrix files
existing_subjects = set()
for file in os.listdir(old_matrix_directory):
    if file.endswith('.csv'):
        try:
            df = pd.read_csv(os.path.join(old_matrix_directory, file))
            if 'sub_id' in df.columns:
                existing_subjects.update(df['sub_id'].unique())
        except Exception as e:
            print(f"Warning: Could not read {file}: {str(e)}")
            continue

# Exclude the specified subject
existing_subjects.discard(excluded_subject)

# Process each CSV file
for file in os.listdir(input_directory):
    if file.endswith('.csv'):
        print(f"Processing {file}...")
        
        try:
            # Read the new data
            new_data = pd.read_csv(os.path.join(input_directory, file))
            
            # Only exclude the specified subject from new data
            new_data = new_data[new_data['sub_id'] != excluded_subject]
            
            # Find corresponding old matrix file
            task_name = file.replace('.csv', '')
            old_file = f"rdoc behavioral matrix - {task_name}_with_notes.csv"
            old_file_path = os.path.join(old_matrix_directory, old_file)
            
            if os.path.exists(old_file_path):
                # Read the old data
                old_data = pd.read_csv(old_file_path)
                
                # Exclude the specified subject from old data
                old_data = old_data[old_data['sub_id'] != excluded_subject]
                
                # Update values in old dataframe with new data
                updated_data = update_values_with_new_data(old_data, new_data)
                
                # For new subjects (not in existing_subjects), only include pristine ones
                new_rows = new_data[~new_data['sub_id'].isin(existing_subjects)]
                new_rows = new_rows[new_rows['sub_id'].isin(pristine_ids)]
                
                if not new_rows.empty:
                    print(f"Found {len(new_rows)} new rows for {file}")
                    
                    # Calculate summary statistics for new rows
                    summary_stats = new_rows.describe()
                    
                    # Add summary statistics to the updated dataframe
                    updated_data = pd.concat([updated_data, new_rows], ignore_index=True)
                
                # Save the updated dataframe
                output_file = os.path.join(output_directory, old_file)
                updated_data.to_csv(output_file, index=False)
                print(f"Saved updated data to {output_file}")
            else:
                print(f"Warning: Could not find corresponding old matrix file for {file}")
        except Exception as e:
            print(f"Error processing {file}: {str(e)}")
            continue

# Copy all files to desktop
try:
    if os.path.exists(desktop_output_directory):
        shutil.rmtree(desktop_output_directory)
    shutil.copytree(output_directory, desktop_output_directory)
    print(f"Files have been copied to {desktop_output_directory}")
except Exception as e:
    print(f"Error copying files to desktop: {str(e)}")

print("Processing complete. New files have been saved to", output_directory)