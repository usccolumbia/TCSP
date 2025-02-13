import argparse
import os
from pymatgen.core import Structure
from pymatgen.analysis.structure_matcher import StructureMatcher
from pymatgen.symmetry.analyzer import SpacegroupAnalyzer
import pandas as pd

def getSymmetrized(s):
    sga = SpacegroupAnalyzer(s)
    symmetrized_structure = sga.get_symmetrized_structure()
    return symmetrized_structure

def PMD(structure1, structure2):
    sm = StructureMatcher(ltol=0.2, stol=0.3, angle_tol=5)
    fit = rms = rms_anonymous = 'None'
    try:
        rms = sm.get_rms_dist(structure1, structure2)[0]
    except Exception as e:
        rms = f'Error: {str(e)}'
    try:
        rms_anonymous = sm.get_rms_anonymous(structure1, structure2)[0]
    except Exception as e:
        rms_anonymous = f'Error: {str(e)}'
    try:
        fit = sm.fit(structure1, structure2)
    except Exception as e:
        fit = f'Error: {str(e)}'
    return fit, rms, rms_anonymous

def get_spacegroup(s):
    try:
        analyzer = SpacegroupAnalyzer(s, symprec=0.1)
        space_group = analyzer.get_space_group_number()
    except Exception as e:
        space_group = f'Error: {str(e)}'
    return space_group

def main():
    parser = argparse.ArgumentParser(description="Process paths for TCSP analysis.")
    parser.add_argument("--path1", default="TCSP_180data_top5_clean/", help="Path to the directory containing predicted CIF files.")
    parser.add_argument("--path2", default="full_name_ground_truth", help="Path to the ground truth CIF files directory.")
    parser.add_argument("--csv", default="data/180_testdata.csv", help="CSV file containing test data.")
    parser.add_argument("--output", default="success_rate_results.csv", help="Output CSV file to save the results.")
    args = parser.parse_args()

    path1 = args.path1
    path2 = args.path2
    csv_file = args.csv
    output_file = args.output

    # Load the CSV file containing formulas
    df = pd.read_csv(csv_file)
    total_count = 0
    sm_success_count = 0
    sg_success_count = 0
    consensus_success_count = 0

    results = []

    # Loop through each formula
    for index, row in df.iterrows():
        formula = row['full_formula']

        # Look for subdirectories matching the formula name
        formula_dir = os.path.join(path1, formula)
        
        # Ensure the subdirectory exists
        if not os.path.isdir(formula_dir):
            print(f"Directory for formula {formula} does not exist. Skipping...")
            continue

        # Get the list of CIF files in this subdirectory
        predicted_files = [f for f in os.listdir(formula_dir) if f.endswith('.cif')]
        predicted_files.sort()  # Sort files, you can add custom sorting logic if needed

        # Only take the first 5 files
        top_5_files = predicted_files[:5]

        sm_success_found = False
        sg_success_found = False
        consensus_found = False

        # Check if any of the top-5 predicted CIF files results in a successful match
        for pred_file in top_5_files:
            pred_file_path = os.path.join(formula_dir, pred_file)
            gt_file_path = os.path.join(path2, f"{formula}.cif")

            try:
                stru1 = Structure.from_file(pred_file_path)
                stru2 = Structure.from_file(gt_file_path)

                structure1 = getSymmetrized(stru1)
                structure2 = getSymmetrized(stru2)

                fit, _, _ = PMD(structure1, structure2)
                pred_sg = get_spacegroup(structure1)
                target_sg = get_spacegroup(structure2)
                sg_match = (pred_sg == target_sg)

                # Check for StructureMatcher success
                if fit == True:
                    sm_success_found = True

                # Check for Spacegroup match success
                if sg_match:
                    sg_success_found = True

                # Check for consensus (both SM and SG match)
                if fit == True and sg_match:
                    consensus_found = True
                    break  # No need to check further if consensus is found

            except Exception as e:
                continue  # If there is an error, skip this file and move to the next

        # Increment success counts for SM, SG, and consensus
        if sm_success_found:
            sm_success_count += 1
        if sg_success_found:
            sg_success_count += 1
        if consensus_found:
            consensus_success_count += 1

        total_count += 1

        # Store the results for each formula
        results.append({
            "Formula": formula,
            "SM_Success_Rate": sm_success_found,
            "SG_Success_Rate": sg_success_found,
            "Consensus_Success_Rate": consensus_found
        })

    # Calculate success rates
    sm_success_rate = sm_success_count / total_count if total_count > 0 else 0
    sg_success_rate = sg_success_count / total_count if total_count > 0 else 0
    consensus_success_rate = consensus_success_count / total_count if total_count > 0 else 0

    print(f"Success rate for StructureMatcher (SM): {sm_success_rate * 100:.2f}%")
    print(f"Success rate for Spacegroup (SG): {sg_success_rate * 100:.2f}%")
    print(f"Consensus success rate (both SM and SG): {consensus_success_rate * 100:.2f}%")

    # Save results to CSV
    results_df = pd.DataFrame(results)
    results_df.to_csv(output_file, index=False)
    print(f"Results saved to {output_file}")

if __name__ == "__main__":
    main()
