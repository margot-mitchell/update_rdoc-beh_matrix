# Iterative RDoC Behavioral QC Matrix  

This script updates the quality control matrix of RDoC behavioral tasks in large (n=500) online data aquisition. It updates each of the 12 files (one per cognitive task) to include new subjects and metrics in line with changes made to the rdoc-beh repo. 

## Features

- Processes multiple behavioral tasks
- Includes new data from pristine subjects
- Excludes specific subjects as needed
- Calculates summary statistics
- Retains all comments from previous matrix file
- Updates values that have changed for existing subjects

## Configuration

The script uses the following paths:
- Input directory: `/path/to/rdoc_beh/results/wide`
- Old matrix directory: `~/Desktop/rdoc_behavioral_matrix_old/`
- Output directory: `new_rdoc_behavioral_matrix`
- Desktop output directory: `~/Desktop/new_rdoc_behavioral_matrix`

## Prerequisites

1. Python 3.x
2. Required Python packages:
   - pandas
   - numpy
   - shutil
   - json

## Setup Instructions

### 1. Data Preparation

1. Follow the instructions in the `rdoc-beh` project README to:
   - Download the raw data
   - Run preprocessing scripts
   - Generate QC files

2. Verify that the processed data is in the correct location:
   - The script expects QC files to be in `/path/to/rdoc_beh/results/wide/`
   - If your data is in a different location, update the `input_directory` path in `main.py`

### 2. Existing Matrix Files

1. Download all tabs from the RDoC behavioral matrix Google Sheets
2. Save each tab as a separate CSV file with the naming format:
   - `rdoc behavioral matrix - [task_name]_with_notes.csv`
   - Example: `rdoc behavioral matrix - go_nogo_rdoc_time_averaged_with_notes.csv`

3. Create a folder on your desktop named `rdoc_behavioral_matrix_old/`
   - Place all downloaded CSV files in this folder
   - If you use a different location, update the `old_matrix_directory` path in `main.py`

### 3. Environment Setup

1. Create a new Python virtual environment:
   ```bash
   python -m venv update_rdoc-beh_matrix
   ```

2. Activate the virtual environment:
   - On macOS/Linux:
     ```bash
     source update_rdoc-beh_matrix/bin/activate
     ```
   - On Windows:
     ```bash
     update_rdoc-beh_matrix\Scripts\activate
     ```

3. Install required packages:
   ```bash
   pip install pandas numpy
   ```

## Running the Script

1. Ensure all prerequisites are met:
   - Data is properly processed and in the correct location
   - Existing matrix files are downloaded and in the correct folder
   - Virtual environment is activated

2. Run the script:
   ```bash
   python main.py
   ```

3. The script will:
   - Process all task files
   - Add new data from pristine subjects
   - Format numbers consistently
   - Calculate summary statistics
   - Save updated files to `new_rdoc_behavioral_matrix/`
   - Copy the updated files to your desktop

## Output

The script generates updated CSV files in two locations:
1. `new_rdoc_behavioral_matrix/` (in the script directory)
2. `~/Desktop/new_rdoc_behavioral_matrix/` (on your desktop)

Each file will contain:
- All existing subject data and QC notes
- New data from pristine subjects
- Summary statistics (Mean, SD, Max, Min)
- Column names at the top and bottom

## Troubleshooting

If you encounter any issues:
1. Verify all file paths in `main.py` are correct
2. Ensure all required packages are installed
3. Check that input files are in the correct format
4. Make sure the pristine subjects JSON file exists at `/path/to/rdoc_beh/qa/pristine_subjects.json`







## License

This project is licensed under the MIT License - see the LICENSE file for details. 
