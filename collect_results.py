import os
import glob
import shutil
import pandas as pd
from pathlib import Path
import sys
import argparse


class ResultCollector:
    def __init__(self, input_dir, output_dir):
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.results_data = []

    def extract_info(self, filename):
        """Extract score and energy from filename."""
        parts = filename.stem.split('_')
        try:
            score = float(parts[0])
            energy = float(parts[1])
            space_group = parts[2].replace('sg', '')
            template = parts[3]
            return {
                'score': score,
                'energy': energy,
                'space_group': space_group,
                'template': template
            }
        except (IndexError, ValueError) as e:
            print(f"Error parsing filename {filename}: {e}")
            return None

    def find_best_cif(self, directory):
        """Find the best CIF file in a directory based on score and energy."""
        cif_files = list(directory.glob('*.cif'))
        if not cif_files:
            return None

        best_file = None
        best_info = None
        best_score = float('inf')
        best_energy = float('inf')

        for file in cif_files:
            info = self.extract_info(file)
            if info is None:
                continue

            if (best_file is None or 
                info['score'] < best_score or 
                (info['score'] == best_score and info['energy'] < best_energy)):
                best_file = file
                best_info = info
                best_score = info['score']
                best_energy = info['energy']

        return best_file, best_info

    def collect_results(self):
        """Collect and organize results from all formula directories."""
        self.output_dir.mkdir(exist_ok=True)
        
        for formula_dir in self.input_dir.iterdir():
            if not formula_dir.is_dir():
                continue

            formula = formula_dir.name
            best_cif, info = self.find_best_cif(formula_dir)
            
            if best_cif and info:
                # Create new filename and copy file
                new_filename = f'TCSP_{formula}.cif'
                new_path = self.output_dir / new_filename
                shutil.copy(best_cif, new_path)
                
                # Store result data
                self.results_data.append({
                    'formula': formula,
                    'score': info['score'],
                    'energy': info['energy'],
                    'space_group': info['space_group'],
                    'template': info['template'],
                    'original_file': str(best_cif),
                    'new_file': str(new_path)
                })
                print(f"Best CIF file for {formula} copied to: {new_path}")
            else:
                print(f"No valid CIF files found for {formula}")

    def save_summary(self):
        """Save results summary to CSV."""
        if self.results_data:
            df = pd.DataFrame(self.results_data)
            summary_file = self.output_dir / 'results_summary.csv'
            df.to_csv(summary_file, index=False)
            print(f"\nResults summary saved to: {summary_file}")
            
            print("\nSummary Statistics:")
            print(f"Total formulas processed: {len(self.results_data)}")
            print(f"Average score: {df['score'].mean():.4f}")
            print(f"Average energy: {df['energy'].mean():.4f}")
        else:
            print("No results data to summarize")

def main():
    parser = argparse.ArgumentParser(description="Collect and organize TCSP results")
    parser.add_argument('--input', default='TCSP_180data',
                      help="Input directory containing formula subdirectories")
    parser.add_argument('--output', default='TCSP_180data_top5_clean',
                      help="Output directory for organized results")
    args = parser.parse_args()

    collector = ResultCollector(args.input, args.output)
    collector.collect_results()
    collector.save_summary()

if __name__ == "__main__":
    main()