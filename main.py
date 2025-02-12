import os
import sys
import shutil
import warnings
import argparse
import subprocess
import pandas as pd
from collections import defaultdict
from pymatgen.core import Composition, Element, Structure
from pymatgen.symmetry.analyzer import SpacegroupAnalyzer
from pymatgen.io.cif import CifWriter
from chgnet.model import StructOptimizer
from BERTOS.bertos import guess_os
from utils import (
    generate_full_anonymized_formula,
    replacementPair,
    pair_euclidean_distance,
    switch_replacepairs,
    element_replace,
    get_relaxed_structure_and_energy
)

# Ignore specific warnings
for category in (UserWarning, DeprecationWarning):
    warnings.filterwarnings("ignore", category=category, module="tensorflow")

# Set CUDA device
os.environ["CUDA_VISIBLE_DEVICES"] = "0"

# Argument parser

def input_parser():
    parser = argparse.ArgumentParser(description="e-above-hull energy calculation using pymatgen")
    parser.add_argument("--input", type=str, default="NdOsO4", help="query formula")
    parser.add_argument("--templatelist", type=str, default="./templatecifs.csv", help="template CIF list")
    parser.add_argument("--templatedir", type=str, default="data/mixed_data4", help="CIFs folder")
    parser.add_argument("--outputdir", type=str, default="./output", help="Output directory")
    parser.add_argument("--topn", type=int, default=5, help="Number of template structure predictions")
    parser.add_argument("--output", type=str, default="./results.csv", help="Output result file path")
    parser.add_argument("--relax", action="store_true", help="Perform relaxation on structures")
    return parser.parse_args(sys.argv[1:])

# Initialize arguments
args = input_parser()
formula = args.input

# Define paths
TEMPLATE_LIST_FILE = 'data/data.csv'
TEMPLATE_CANDIDATES_FILE = 'templateCandidates.csv'

# Step 1: Find formulas with the same anonymized format
print("Searching for templates with the same anonymous formula format...")
df = pd.read_csv(TEMPLATE_LIST_FILE, dtype={'full_formula': str}).fillna("NaN")
anonymFormula = generate_full_anonymized_formula(formula)

# Identify matching templates
templateCandidates = [['id', 'full_formula']]
for i, formulaT in enumerate(df['full_formula'].values):
    if anonymFormula == generate_full_anonymized_formula(formulaT):
        templateCandidates.append([df.iloc[i, 0], str(formulaT)])

if not templateCandidates[1:]:
    print("No matching templates found.")
    exit(-1)

pd.DataFrame(templateCandidates).to_csv(TEMPLATE_CANDIDATES_FILE, index=False, header=None)
print(f"{len(templateCandidates)-1} templates found with the same format.")

# Step 2: Compute template similarity scores
print(f"Calculating similarity scores for {formula}...")
similarity_command = f'python3 ./find_compositionX_new3.py --database ../{TEMPLATE_CANDIDATES_FILE} --input {formula} --output ../similar_formulas.csv'
subprocess.call(similarity_command, shell=True, cwd='find_similarformula')

# Step 3: Filter valid templates based on oxidation states
print("Filtering valid template candidates...")
validCandidates = []
oxid1 = [guess_os(formula)]

with open("similar_formulas.csv", 'r') as file:
    mostsimilarFormulas = [line.split(",")[0] for line in file.readlines()][1:]

for f in mostsimilarFormulas:
    oxid2 = [guess_os(f)]
    if oxid2 and set(tuple(sorted(o.values())) for o in oxid1) & set(tuple(sorted(o.values())) for o in oxid2):
        validCandidates.append(str(Composition(f)).replace(" ", ""))

if not validCandidates:
    print("No valid candidates found with compatible oxidation states. Using all found templates.")
    validCandidates = [str(Composition(f)).replace(" ", "") for f in mostsimilarFormulas]

top_templates = validCandidates[:min(len(validCandidates), args.topn)]

# Step 4: Generate predictions and relax structures
print("Generating predictions...")
relaxer = StructOptimizer()

# Ensure output directory exists
if os.path.exists(args.outputdir):
    shutil.rmtree(args.outputdir)
os.makedirs(args.outputdir)

best_template_results = {}
for formulaT in top_templates:
    if Composition(formulaT).reduced_formula == Composition(formula).reduced_formula:
        continue

    for mp_id in df[df['full_formula'] == formulaT]['material_id']:
        file = f"{args.templatedir}/{mp_id}.cif"
        for replacementDict in sorted({tuple(pair): pair_euclidean_distance(pair) for pair in replacementPair(formula, formulaT)}.items(), key=lambda x: x[1]):
            score = replacementDict[1]
            temp_replaced_file = f"{args.outputdir}/temp_replaced_{mp_id}.cif"
            replaced_cif_string = element_replace(open(file, 'r').read(), switch_replacepairs(replacementDict[0]), temp_replaced_file)
            replaced_structure = Structure.from_file(temp_replaced_file)
            analyzer = SpacegroupAnalyzer(replaced_structure)
            spacegroup_number = analyzer.get_space_group_number()
            relaxed_structure, energy = get_relaxed_structure_and_energy(replaced_structure)
            output_filepath = f"{args.outputdir}/{score:.3f}_{energy:.2f}_sg{spacegroup_number}_{formulaT}_{mp_id}.cif"
            CifWriter(relaxed_structure).write_file(output_filepath)
            best_template_results[formulaT] = (score, output_filepath, formulaT, spacegroup_number)
            os.remove(temp_replaced_file)

# Step 5: Select best results and clean up
print("Selecting best results...")
all_results = sorted(best_template_results.values(), key=lambda x: x[0])[:args.topn]
for result in best_template_results.values():
    if result not in all_results and os.path.exists(result[1]):
        os.remove(result[1])

# Print final results
print("\nFinal Selected CIFs:")
for score, filepath, template, spacegroup in all_results:
    print(f"Score: {score:.4f}, Template: {template}, Space Group: {spacegroup}, File: {filepath}")

print(f"\nJob done. CIF files saved in {args.outputdir}")
