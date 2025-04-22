# RDoC Behavioral Matrix Updater

This script processes and updates behavioral matrix files for RDoC (Research Domain Criteria) tasks. It handles multiple tasks including go/nogo, stop signal, visual search, and others.

## Features

- Processes multiple behavioral tasks
- Filters data based on pristine subjects
- Excludes specific subjects as needed
- Calculates summary statistics
- Maintains data integrity across sessions

## Requirements

- Python 3.x
- pandas
- numpy

## Usage

1. Place input CSV files in the specified input directory
2. Run the script:
   ```bash
   python main.py
   ```
3. Output files will be saved in the `new_rdoc_behavioral_matrix` directory

## Configuration

The script uses the following paths:
- Input directory: `/Users/marg0tm/rdoc-beh/results/wide`
- Old matrix directory: `~/Desktop/rdoc_behavioral_matrix_old/`
- Output directory: `new_rdoc_behavioral_matrix`
- Desktop output directory: `~/Desktop/new_rdoc_behavioral_matrix`

## Notes

- The script excludes specific subjects as configured
- Summary statistics are calculated after filtering
- All numeric values are formatted to 4 decimal places

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
   - The script expects QC files to be in `/Users/marg0tm/rdoc-beh/results/wide/`
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
- All existing subject data
- New data from pristine subjects
- Summary statistics (Mean, SD, Max, Min)
- Column names at the top and bottom

## Troubleshooting

If you encounter any issues:
1. Verify all file paths in `main.py` are correct
2. Ensure all required packages are installed
3. Check that input files are in the correct format
4. Make sure the pristine subjects JSON file exists at `/Users/marg0tm/rdoc-beh/qa/pristine_subjects.json`

## Notes

- The script preserves existing data while adding new rows
- Numbers are formatted to show whole numbers without decimals and decimal numbers with up to 4 decimal places
- Summary statistics are calculated only once at the end
- Column names appear only at the top (header) and bottom of each file 