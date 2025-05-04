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

# Function to remove empty columns and rows
def remove_empty(df):
    # Remove columns that are entirely empty or contain only NaN/None/empty strings
    df = df.dropna(axis=1, how='all')
    df = df.loc[:, ~(df.astype(str) == '').all()]
    
    # Remove rows that are entirely empty or contain only NaN/None/empty strings
    df = df.dropna(axis=0, how='all')
    df = df.loc[~(df.astype(str) == '').all(axis=1)]
    
    return df

# Function to format numbers
def format_number(x):
    if pd.isna(x) or isinstance(x, str):
        return x
    # Round to 4 decimal places
    x = round(x, 4)
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
    
    # Add any columns from new_df that don't exist in old_df
    for col in new_df.columns:
        if col not in updated_df.columns:
            # Find the position of 'session' column
            session_idx = updated_df.columns.get_loc('session')
            # Insert the new column before 'session'
            updated_df.insert(session_idx, col, None)
    
    # Iterate through each row in the new dataframe
    for _, new_row in new_df.iterrows():
        # Find matching rows in the old dataframe based on sub_id and date_time
        mask = (updated_df['sub_id'] == new_row['sub_id']) & (updated_df['date_time'] == new_row['date_time'])
        
        if mask.any():
            # Update all columns that exist in both dataframes
            for col in new_row.index:
                if col in updated_df.columns:
                    # Skip updating RC comments if the new value is empty
                    if col == 'RC comments' and (pd.isna(new_row[col]) or new_row[col] == ''):
                        continue
                    updated_df.loc[mask, col] = new_row[col]
    
    # Format all numerical columns to 4 decimal places
    for col in updated_df.columns:
        if updated_df[col].dtype in [np.float64, np.int64]:
            updated_df[col] = updated_df[col].apply(format_number)
    
    return updated_df

def reorder_columns(df):
    # Define the columns that should come at the end
    end_metrics = ['proportion_feedback']
    end_check_cols = ['attention_check_mean_accuracy', 'session']
    comment_columns = [col for col in df.columns if 'comment' in col.lower() or col in ['PB', 'RC notes', 'checked', 'pb checked', 'MM follow up', 'PB notes']]
    
    # Get all columns that are not in special columns
    metric_columns = [col for col in df.columns if col not in end_metrics + end_check_cols + comment_columns]
    
    # Ensure sub_id and date_time are first
    if 'sub_id' in metric_columns:
        metric_columns.remove('sub_id')
    if 'date_time' in metric_columns:
        metric_columns.remove('date_time')
    
    # Combine all columns in the desired order
    ordered_columns = ['sub_id', 'date_time'] + metric_columns + end_metrics + end_check_cols + comment_columns
    
    # Only include columns that exist in the dataframe
    ordered_columns = [col for col in ordered_columns if col in df.columns]
    
    # Reorder the dataframe
    return df[ordered_columns]

# Load pristine subjects
with open('/Users/marg0tm/rdoc-beh/qa/pristine_subjects.json', 'r') as f:
    pristine_subjects = json.load(f)
pristine_ids = set(pristine_subjects['ids'])

# Load excluded subjects
excluded_ids = set()
if os.path.exists('excluded_subjects.json'):
    with open('excluded_subjects.json', 'r') as f:
        excluded_subjects = json.load(f)
        excluded_ids = set(excluded_subjects.get('ids', []))

# Create output directory if it doesn't exist
os.makedirs(output_directory, exist_ok=True)

# Define expected task names
expected_tasks = [
    'spatial_task_switching',
    'stop_signal',
    'go_nogo',
    'visual_search',
    'simple_span',
    'cued_task_switching',
    'flanker',
    'stroop',
    'n_back',
    'spatial_cueing',
    'operation_span',
    'ax_cpt'
]

# Check files in old matrix directory
old_matrix_files = [f for f in os.listdir(old_matrix_directory) if f.endswith('.csv')]
if len(old_matrix_files) > 12:
    raise ValueError("too many files")

# Check that each task has exactly one corresponding file
for task in expected_tasks:
    matching_files = [f for f in old_matrix_files if task in f.lower()]
    if len(matching_files) == 0:
        raise ValueError(f"missing {task}")

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

# Process each CSV file
for file in os.listdir(input_directory):
    if file.endswith('.csv'):
        print(f"Processing {file}...")
        
        try:
            # Read the new data
            new_data = pd.read_csv(os.path.join(input_directory, file))
            
            # Remove empty columns and rows from new data
            new_data = remove_empty(new_data)
            
            # Format numerical columns in new data
            for col in new_data.columns:
                if new_data[col].dtype in [np.float64, np.int64]:
                    new_data[col] = new_data[col].apply(format_number)
            
            # Find corresponding old matrix file
            task_name = file.replace('.csv', '')
            # Try both naming conventions
            old_file = f"{task_name}_with_notes.csv"
            old_file_path = os.path.join(old_matrix_directory, old_file)
            if not os.path.exists(old_file_path):
                old_file = f"rdoc behavioral matrix - {task_name}_with_notes.csv"
                old_file_path = os.path.join(old_matrix_directory, old_file)
            
            if os.path.exists(old_file_path):
                # Read the old data
                old_data = pd.read_csv(old_file_path)
                
                # Remove empty columns and rows from old data
                old_data = remove_empty(old_data)
                
                # Remove any rows that contain column names
                old_data = old_data[~old_data.apply(lambda row: row.astype(str).isin(old_data.columns).any(), axis=1)]
                
                # Remove summary statistics rows if they exist
                old_data = old_data[~old_data['sub_id'].isin(['Mean', 'SD', 'Max', 'Min'])]
                
                # Remove attention_check_mean_rt column if it exists
                if 'attention_check_mean_rt' in old_data.columns:
                    old_data = old_data.drop(columns=['attention_check_mean_rt'])
                if 'attention_check_mean_rt' in new_data.columns:
                    new_data = new_data.drop(columns=['attention_check_mean_rt'])
                
                # Format numerical columns in old data
                for col in old_data.columns:
                    if old_data[col].dtype in [np.float64, np.int64]:
                        old_data[col] = old_data[col].apply(format_number)
                
                # Update values in old dataframe with new data
                updated_data = update_values_with_new_data(old_data, new_data)
                
                # For new subjects (not in existing_subjects), only include pristine ones and exclude specified subjects
                new_rows = new_data[~new_data['sub_id'].isin(existing_subjects)]
                new_rows = new_rows[new_rows['sub_id'].isin(pristine_ids)]
                new_rows = new_rows[~new_rows['sub_id'].isin(excluded_ids)]
                
                if not new_rows.empty:
                    print(f"Found {len(new_rows)} new rows for {file}")
                    # Add new rows to the updated dataframe
                    updated_data = pd.concat([updated_data, new_rows], ignore_index=True)
                
                # Reorder columns to ensure task-specific metrics are in the correct position
                updated_data = reorder_columns(updated_data)
                
                # Get the columns between date_time and session
                start_col = 'date_time'
                end_col = 'session'
                start_idx = updated_data.columns.get_loc(start_col)
                end_idx = updated_data.columns.get_loc(end_col)
                stats_cols = updated_data.columns[start_idx:end_idx]  # Exclude session column
                
                # Create a temporary dataframe for calculations
                calc_df = updated_data.copy()
                for col in stats_cols:
                    calc_df[col] = pd.to_numeric(calc_df[col], errors='coerce')
                
                # Calculate statistics
                stats_df = pd.DataFrame(index=['Mean', 'SD', 'Max', 'Min'])
                for col in updated_data.columns:
                    if col in stats_cols:
                        stats_df[col] = [
                            format_number(calc_df[col].mean()),
                            format_number(calc_df[col].std()),
                            format_number(calc_df[col].max()),
                            format_number(calc_df[col].min())
                        ]
                    else:
                        stats_df[col] = ['', '', '', '']
                
                # Add row names to the summary statistics
                stats_df['sub_id'] = ['Mean', 'SD', 'Max', 'Min']
                
                # Add summary statistics to the end of the dataframe
                updated_data = pd.concat([updated_data, stats_df], ignore_index=True)
                
                # Add column names as the last row
                column_names = pd.DataFrame([updated_data.columns], columns=updated_data.columns)
                updated_data = pd.concat([updated_data, column_names], ignore_index=True)
                
                # Remove any empty columns and rows from the final output
                updated_data = remove_empty(updated_data)
                
                # Save the updated dataframe with new naming convention
                output_file = os.path.join(output_directory, f"{task_name}_with_notes.csv")
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