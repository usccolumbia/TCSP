import json
import math
from pymatgen.core.periodic_table import Element
from pymatgen.core.composition import Composition
import pandas as pd
import multiprocessing as mp

def load_embeddings():
    with open('../matscholar-embedding.json', 'r') as file:
        return json.load(file)

embeddings = load_embeddings()

def formula_euclidean_distance(formula1, formula2):
    comp1 = Composition(formula1)
    comp2 = Composition(formula2)

    elements1 = sorted(comp1.elements, key=lambda e: (e.X, e.number))
    elements2 = sorted(comp2.elements, key=lambda e: (e.X, e.number))

    # Create pairs of elements
    pair_list = list(zip(elements1, elements2))

    total_score = 0
    unmatched_pairs = 0
    space_group_diff = 0

    for pair in pair_list:
        element1, element2 = pair
        if element1.symbol == element2.symbol:
            continue  # Skip this pair, as it contributes 0 to the total score
        
        unmatched_pairs += 1  # Count this as an unmatched pair

        if element1.symbol not in embeddings or element2.symbol not in embeddings:
            return 99999  # Return a large number if embedding is not found for any element

        vector1 = embeddings[element1.symbol]
        vector2 = embeddings[element2.symbol]
        score = math.sqrt(sum((a - b) ** 2 for a, b in zip(vector1, vector2)))
        total_score += score

        # check group consistency 
        group1 = element1.group
        group2 = element2.group
        if group1 != group2:
            space_group_diff += 1

    total_score = total_score + space_group_diff

    average_score = total_score / unmatched_pairs if unmatched_pairs > 0 else 0

    return average_score

def calc(tup):
    input_formula, formula = tup
    try:
        score = formula_euclidean_distance(input_formula, formula)
    except:
        score = 99999
    return (formula, score)

def find_similar_formulas(input_formula, database_file, output_file, num_processes=8):
    df = pd.read_csv(database_file)
    # print(f"Reading database from: {database_file}")

    with mp.Pool(processes=num_processes) as pool:
        results = pool.map(calc, [(input_formula, formula) for formula in df['full_formula']])

    formula2scores = {res[0]: res[1] for res in results}

    sorted_results = sorted(formula2scores.items(), key=lambda x: x[1])

    with open(output_file, 'w') as f:
        # f.write("formula,score\n")/
        for formula, score in sorted_results:
            f.write(f"{formula},{score}\n")

    # print(f"Results written to: {output_file}")

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Find similar formulas using Euclidean distance.")
    parser.add_argument("--input", required=True, help="Input formula")
    parser.add_argument("--database", required=True, help="Path to the database CSV file")
    parser.add_argument("--output", required=True, help="Path to the output CSV file")

    args = parser.parse_args()

    find_similar_formulas(args.input, args.database, args.output)