import sys
import argparse
import pandas as pd
import os
from pathlib import Path

def check_output_directory(dir_path):
    """Check if directory exists and contains CIF files."""
    if not os.path.exists(dir_path):
        return False
    cif_files = list(Path(dir_path).glob('*.cif'))
    return len(cif_files) > 0

def process_formulas(csv_file, output_base_dir, force=False):
    """Process formulas from CSV and track progress."""
    # Read formulas from CSV
    df = pd.read_csv(csv_file)['full_formula']
    total_formulas = len(df)
    print(f"Total formulas to process: {total_formulas}")
    
    # Initialize counters and error tracking
    processed = []
    skipped = []
    errors = []
    
    for formula in df:
        output_dir = os.path.join(output_base_dir, formula)
        
        try:
            # Skip if already processed and force is False
            if not force and check_output_directory(output_dir):
                print(f"Skipping formula {formula} as results already exist.")
                skipped.append(formula)
                continue
            
            # Create output directory
            os.makedirs(output_dir, exist_ok=True)
            
            # Run prediction command
            command = f'python3 ./main.py --input "{formula}" --outputdir "{output_dir}" --topn 5'
            print(f"Running command: {command}")
            
            if os.system(command) == 0:
                processed.append(formula)
            else:
                errors.append((formula, "Command execution failed"))
                
        except Exception as e:
            errors.append((formula, str(e)))
    
    return {
        'processed': processed,
        'skipped': skipped,
        'errors': errors,
        'total': total_formulas
    }

def main():
    parser = argparse.ArgumentParser(description="Process multiple formulas from a CSV file")
    parser.add_argument('--force', action='store_true', help="Force reprocessing of all formulas")
    parser.add_argument('--csv', default='data/180_testdata.csv', 
                      help="Path to CSV file containing formulas")
    parser.add_argument('--output', default='TCSP_180data',
                      help="Base output directory")
    args = parser.parse_args()

    # Process formulas
    results = process_formulas(args.csv, args.output, args.force)
    
    # Print summary
    print("\nProcessing Summary:")
    print(f"Total formulas: {results['total']}")
    print(f"Successfully processed: {len(results['processed'])}")
    print(f"Skipped: {len(results['skipped'])}")
    print(f"Errors: {len(results['errors'])}")
    
    # Print errors if any
    if results['errors']:
        print("\nErrors encountered:")
        for formula, error in results['errors']:
            print(f"{formula}: {error}")
            
    # Check for missing formulas
    missing = results['total'] - (len(results['processed']) + len(results['skipped']))
    if missing > 0:
        print(f"\nWARNING: {missing} formulas were not processed or skipped!")

if __name__ == "__main__":
    main()