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

# Load pristine subjects
with open('/Users/marg0tm/rdoc-beh/qa/pristine_subjects.json', 'r') as f:
    pristine_data = json.load(f)
pristine_ids = set(pristine_data['ids'])

# Create output directory if it doesn't exist
if not os.path.exists(output_directory):
    os.makedirs(output_directory)

# List all CSV files in both directories
new_csv_filenames = [f for f in os.listdir(input_directory) if f.endswith('.csv') and not f.endswith('_screener_time_averaged.csv')]
old_csv_filenames = [f for f in os.listdir(old_matrix_directory) if f.endswith('.csv')]

# First, collect all existing sub_ids from old matrix files
existing_sub_ids = set()
for old_filename in old_csv_filenames:
    try:
        old_file_path = os.path.join(old_matrix_directory, old_filename)
        old_data = pd.read_csv(old_file_path)
        
        # Remove any existing summary statistics and column names rows
        if not old_data.empty and 'sub_id' in old_data.columns:
            # Remove rows with summary statistics
            old_data = old_data[~old_data['sub_id'].isin(['Mean', 'SD', 'Max', 'Min'])]
            
            # Remove any row that matches column names (except header)
            for idx, row in old_data.iterrows():
                if idx > 0 and all(str(col) in map(str, row.values) for col in old_data.columns):
                    old_data = old_data.drop(idx)
            
            # Remove rows where sub_id is empty or NaN
            old_data = old_data.dropna(subset=['sub_id'])
            old_data = old_data[old_data['sub_id'].str.strip() != '']
            
            # Exclude specific subject ID
            old_data = old_data[old_data['sub_id'] != '665368b3a0704ee687e448a0']
            
            existing_sub_ids.update(old_data['sub_id'].unique())
    except Exception as e:
        print(f"Error reading {old_filename}: {str(e)}")
        continue

print(f"Found {len(existing_sub_ids)} existing subject IDs")

# Dictionary to store all processed dataframes
processed_dataframes = {}

# Process each CSV file
for old_filename in old_csv_filenames:
    # Get the task name from the old filename
    task_name = old_filename.replace('rdoc behavioral matrix - ', '').replace('_with_notes.csv', '')
    
    # Find corresponding new file
    new_filename = None
    for f in new_csv_filenames:
        if task_name in f:
            new_filename = f
            break
    
    if new_filename is None:
        print(f"No new data file found for: {old_filename}")
        continue
        
    try:
        # Read both old and new files
        old_file_path = os.path.join(old_matrix_directory, old_filename)
        new_file_path = os.path.join(input_directory, new_filename)
        
        old_data = pd.read_csv(old_file_path)
        new_data = pd.read_csv(new_file_path)
        
        # Remove any existing summary statistics and column names from old data
        if not old_data.empty and 'sub_id' in old_data.columns:
            # Remove rows with summary statistics
            old_data = old_data[~old_data['sub_id'].isin(['Mean', 'SD', 'Max', 'Min'])]
            
            # Remove any row that matches column names (except header)
            for idx, row in old_data.iterrows():
                if idx > 0 and all(str(col) in map(str, row.values) for col in old_data.columns):
                    old_data = old_data.drop(idx)
            
            # Remove rows where sub_id is empty or NaN
            old_data = old_data.dropna(subset=['sub_id'])
            old_data = old_data[old_data['sub_id'].str.strip() != '']
            
            # Exclude specific subject ID
            old_data = old_data[old_data['sub_id'] != '665368b3a0704ee687e448a0']
        
        # Format numeric columns in both dataframes
        for col in old_data.columns:
            try:
                # Try to convert to numeric, if successful, format the numbers
                numeric_col = pd.to_numeric(old_data[col], errors='coerce')
                if not numeric_col.isna().all():  # If at least some values are numeric
                    old_data[col] = old_data[col].apply(lambda x: format_number(pd.to_numeric(x, errors='coerce')) if pd.notna(x) else x)
            except:
                continue
                
        for col in new_data.columns:
            try:
                numeric_col = pd.to_numeric(new_data[col], errors='coerce')
                if not numeric_col.isna().all():
                    new_data[col] = new_data[col].apply(lambda x: format_number(pd.to_numeric(x, errors='coerce')) if pd.notna(x) else x)
            except:
                continue
        
        # Remove rows where sub_id is empty or NaN from new data
        new_data = new_data.dropna(subset=['sub_id'])
        new_data = new_data[new_data['sub_id'].str.strip() != '']
        
        # Exclude specific subject ID from new data
        new_data = new_data[new_data['sub_id'] != '665368b3a0704ee687e448a0']
        
        # Find existing subjects in new data
        existing_in_new = new_data[new_data['sub_id'].isin(existing_sub_ids)]
        
        # Update values for existing subjects
        if not existing_in_new.empty:
            print(f"Found {len(existing_in_new)} existing subjects with updated values for {task_name}")
            # Remove old rows for these subjects
            old_data = old_data[~old_data['sub_id'].isin(existing_in_new['sub_id'])]
            # Add the updated rows
            old_data = pd.concat([old_data, existing_in_new], ignore_index=True)
        
        # Find new subjects (not in existing_sub_ids)
        new_subjects = new_data[~new_data['sub_id'].isin(existing_sub_ids)]
        # Filter to only include pristine subjects
        new_subjects = new_subjects[new_subjects['sub_id'].isin(pristine_ids)]
        
        print(f"Found {len(new_subjects)} new rows for {task_name}")
        
        # If there are new subjects, append them to the old data
        if not new_subjects.empty:
            updated_data = pd.concat([old_data, new_subjects], ignore_index=True)
        else:
            updated_data = old_data
            
        # Check for new columns and position them correctly
        new_columns = new_data.columns.difference(old_data.columns.tolist())
        
        if not new_columns.empty:
            # Add new columns from new_data to updated_data
            for col in new_columns:
                updated_data[col] = new_data[col]
        
        # Handle attention check columns
        # 1. Delete attention_check accuracy if it exists
        if 'attention_check accuracy' in updated_data.columns:
            updated_data = updated_data.drop(columns=['attention_check accuracy'])
        
        # 2. Delete attention_check_mean_response_time if it exists
        if 'attention_check_mean_response_time' in updated_data.columns:
            updated_data = updated_data.drop(columns=['attention_check_mean_response_time'])
        
        # 3. Reorder columns to place attention_check_mean_accuracy and attention_check_mean_rt
        # between proportion_feedback and session
        if 'proportion_feedback' in updated_data.columns and 'session' in updated_data.columns:
            columns = updated_data.columns.tolist()
            prop_feedback_idx = columns.index('proportion_feedback')
            session_idx = columns.index('session')
            
            attention_cols = ['attention_check_mean_accuracy', 'attention_check_mean_rt']
            for col in attention_cols:
                if col in columns:
                    columns.remove(col)
            
            new_columns = (
                columns[:prop_feedback_idx + 1] +
                attention_cols +
                columns[prop_feedback_idx + 1:]
            )
            
            updated_data = updated_data[new_columns]
        
        # Store the processed dataframe
        processed_dataframes[task_name] = updated_data
    except Exception as e:
        print(f"Error processing {task_name}: {str(e)}")
        continue

# Process each task's dataframe
for task_name, df in processed_dataframes.items():
    try:
        # Get all columns between date_time and session (excluding both)
        all_columns = df.columns.tolist()
        date_time_idx = all_columns.index('date_time')
        session_idx = all_columns.index('session')
        target_columns = all_columns[date_time_idx + 1:session_idx]
        
        # Create summary rows
        summary_rows = pd.DataFrame(index=['Mean', 'SD', 'Max', 'Min'])
        
        # Initialize all columns with empty strings
        for col in all_columns:
            summary_rows[col] = ''
        
        # Set sub_id column
        summary_rows['sub_id'] = ['Mean', 'SD', 'Max', 'Min']
        
        # Calculate statistics for target columns
        for col in target_columns:
            try:
                numeric_data = pd.to_numeric(df[col], errors='coerce')
                if not numeric_data.isna().all():
                    mean_val = numeric_data.mean()
                    std_val = numeric_data.std()
                    max_val = numeric_data.max()
                    min_val = numeric_data.min()
                    
                    summary_rows.loc['Mean', col] = format_number(mean_val)
                    summary_rows.loc['SD', col] = format_number(std_val)
                    summary_rows.loc['Max', col] = format_number(max_val)
                    summary_rows.loc['Min', col] = format_number(min_val)
            except:
                pass
        
        # Create column names row
        column_names_row = pd.DataFrame([all_columns], columns=all_columns)
        
        # Append summary rows and column names to the DataFrame
        df = pd.concat([df, summary_rows, column_names_row], ignore_index=True)
        
        # Save the updated DataFrame to a new CSV file
        output_file_path = os.path.join(output_directory, f'{task_name}_with_notes.csv')
        df.to_csv(output_file_path, index=False)
    except Exception as e:
        print(f"Error saving {task_name}: {str(e)}")
        continue

# Copy all files to desktop
try:
    if os.path.exists(desktop_output_directory):
        shutil.rmtree(desktop_output_directory)
    shutil.copytree(output_directory, desktop_output_directory)
    print(f"Files have been copied to {desktop_output_directory}")
except Exception as e:
    print(f"Error copying files to desktop: {str(e)}")

print("Processing complete. New files have been saved.")

def process_csv_file(input_file, old_matrix_file, output_file, pristine_subjects):
    # Read input CSV file
    df = pd.read_csv(input_file)
    
    # Read old matrix file if it exists
    old_df = None
    if os.path.exists(old_matrix_file):
        old_df = pd.read_csv(old_matrix_file)
        # Drop any rows that don't have a sub_id
        old_df = old_df.dropna(subset=['sub_id'])
        # Exclude specific subject ID from old data
        old_df = old_df[old_df['sub_id'] != '665368b3a0704ee687e448a0']
        # Get unique subjects from old matrix
        existing_subjects = old_df['sub_id'].unique()
        print(f"Found {len(existing_subjects)} existing subject IDs")
    else:
        existing_subjects = []
    
    # Drop any rows that don't have a sub_id
    df = df.dropna(subset=['sub_id'])
    # Exclude specific subject ID from new data
    df = df[df['sub_id'] != '665368b3a0704ee687e448a0']
    
    # Get unique subjects from new data
    new_subjects = df['sub_id'].unique()
    
    # Filter for pristine subjects
    pristine_new_subjects = [s for s in new_subjects if s in pristine_subjects]
    
    # For each existing subject, check if they have new data
    updated_rows = []
    for subject in existing_subjects:
        subject_data = df[df['sub_id'] == subject]
        if not subject_data.empty:
            # Take the last session for this subject
            last_session = subject_data.sort_values('session').iloc[-1:]
            updated_rows.append(last_session)
    
    # For each new pristine subject, add their data
    new_rows = []
    for subject in pristine_new_subjects:
        if subject not in existing_subjects:
            subject_data = df[df['sub_id'] == subject]
            # Take the last session for this subject
            last_session = subject_data.sort_values('session').iloc[-1:]
            new_rows.append(last_session)
    
    # Combine updated and new rows
    if updated_rows:
        updated_df = pd.concat(updated_rows, ignore_index=True)
        print(f"Found {len(updated_rows)} subjects with updated values")
    else:
        updated_df = pd.DataFrame()
    
    if new_rows:
        new_df = pd.concat(new_rows, ignore_index=True)
        print(f"Found {len(new_rows)} new rows")
    else:
        new_df = pd.DataFrame()
    
    # If we have an old matrix, start with it (excluding updated subjects)
    if old_df is not None:
        # Remove subjects that have updates
        old_df = old_df[~old_df['sub_id'].isin(updated_df['sub_id'])]
        # Combine with updated and new data
        final_df = pd.concat([old_df, updated_df, new_df], ignore_index=True)
    else:
        final_df = pd.concat([updated_df, new_df], ignore_index=True)
    
    # Calculate summary statistics for numeric columns
    numeric_cols = final_df.select_dtypes(include=[np.number]).columns
    summary_stats = pd.DataFrame()
    for stat in ['Mean', 'SD', 'Max', 'Min']:
        row = pd.Series(index=final_df.columns, name=stat)
        for col in final_df.columns:
            if col in numeric_cols:
                if stat == 'Mean':
                    val = final_df[col].mean()
                elif stat == 'SD':
                    val = final_df[col].std()
                elif stat == 'Max':
                    val = final_df[col].max()
                elif stat == 'Min':
                    val = final_df[col].min()
                row[col] = format_number(val) if pd.notnull(val) else ''
            else:
                row[col] = ''
        summary_stats = pd.concat([summary_stats, pd.DataFrame([row])])
    
    # Add column names as the last row
    column_names = pd.DataFrame([final_df.columns], columns=final_df.columns)
    
    # Combine everything
    final_df = pd.concat([final_df, summary_stats, column_names], ignore_index=True)
    
    # Save to output file
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    final_df.to_csv(output_file, index=False)