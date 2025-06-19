import pandas as pd
import glob
import os

def check_sub_id_counts(directory):
    # Get all CSV files in the directory
    csv_files = glob.glob(os.path.join(directory, "*.csv"))
    
    results = {}
    
    for file_path in csv_files:
        file_name = os.path.basename(file_path)
        print(f"\nAnalyzing {file_name}...")
        
        # Read the CSV file
        df = pd.read_csv(file_path)
        
        # Count occurrences of each sub_id
        sub_id_counts = df['sub_id'].value_counts()
        
        # Check if all counts are exactly 5
        all_five = all(count == 5 for count in sub_id_counts)
        
        # Get sub_ids that don't have exactly 5 rows
        if not all_five:
            incorrect_counts = sub_id_counts[sub_id_counts != 5]
            print(f"Found {len(incorrect_counts)} sub_ids with incorrect counts:")
            for sub_id, count in incorrect_counts.items():
                print(f"  sub_id {sub_id}: {count} rows")
        else:
            print("All sub_ids have exactly 5 rows")
        
        # Store results
        results[file_name] = {
            'total_sub_ids': len(sub_id_counts),
            'all_five': all_five,
            'incorrect_counts': incorrect_counts if not all_five else None
        }
    
    return results

if __name__ == "__main__":
    directory = "new_rdoc_behavioral_matrix"
    results = check_sub_id_counts(directory) 