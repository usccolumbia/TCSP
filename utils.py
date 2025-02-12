import os
import sys
import json
import math
import pickle
import itertools
import shutil
import warnings
import numpy as np
import pandas as pd
from collections import defaultdict
from pymatgen.core import Composition, Element, Structure
from pymatgen.analysis.structure_prediction.substitution_probability import *
from pymatgen.symmetry.analyzer import SpacegroupAnalyzer
from pymatgen.io.cif import CifWriter
from chgnet.model import StructOptimizer
from BERTOS.bertos import guess_os

# Suppress warnings
for category in (UserWarning, DeprecationWarning):
    warnings.filterwarnings("ignore", category=category, module="tensorflow")

os.environ["CUDA_VISIBLE_DEVICES"] = "0"

# Load element dissimilarity data
with open("data/element_dissimilarity.pkl", 'rb') as f:
    element_dissimilarity = pickle.load(f)

# List of elements
ELEMENTS = [
    "H", "He", "Li", "Be", "B", "C", "N", "O", "F", "Ne", "Na", "Mg", "Al", "Si", "P", "S", "Cl", "Ar", "K", "Ca", "Sc", "Ti", "V",
    "Cr", "Mn", "Fe", "Co", "Ni", "Cu", "Zn", "Ga", "Ge", "As", "Se", "Br", "Kr", "Rb", "Sr", "Y", "Zr", "Nb", "Mo", "Tc", "Ru",
    "Rh", "Pd", "Ag", "Cd", "In", "Sn", "Sb", "Te", "I", "Xe", "Cs", "Ba", "La", "Ce", "Pr", "Nd", "Pm", "Sm", "Eu", "Gd", "Tb",
    "Dy", "Ho", "Er", "Tm", "Yb", "Lu", "Hf", "Ta", "W", "Re", "Os", "Ir", "Pt", "Au", "Hg", "Tl", "Pb", "Bi", "Po", "At", "Rn", "Fr",
    "Ra", "Ac", "Th", "Pa", "U", "Np", "Pu", "Am", "Cm", "Bk", "Cf", "Es", "Fm", "Md", "No", "Lr"
]

# Utilities

def convert_to_pretty_formula(formula):
    """Convert formula to its pretty string representation."""
    try:
        return Composition(formula).to_pretty_string()
    except Exception as e:
        print(f"Error processing formula {formula}: {str(e)}")
        return None

def pair_distance(pair_list):
    """Calculate total pairwise element distance using ElMD."""
    return sum(ElMD(formula=pair[0], metric='mendeleev').elmd(pair[1]) for pair in pair_list)

def pair_euclidean_distance(pair_list):
    """Calculate Euclidean distance between element pairs based on embeddings."""
    with open('data/matscholar-embedding.json', 'r') as file:
        data = json.load(file)
    
    total_score, space_group_diff = 0, 0
    for element1, element2 in pair_list:
        vector1, vector2 = data[element1], data[element2]
        total_score += math.sqrt(sum((a - b) ** 2 for a, b in zip(vector1, vector2)))
        if Element(element1).group != Element(element2).group:
            space_group_diff += 1
    
    return (total_score + space_group_diff) / max(1, len(pair_list))

def formula_to_composition(formula, elements=ELEMENTS):
    """Transform a formula into a composition vector."""
    comp = Composition(formula)
    vec = np.zeros(len(elements))
    for i, elem in enumerate(elements):
        vec[i] = comp.get_atomic_fraction(elem)
    return vec

def replacementPair(formula1, formula2):
    """Find possible element replacement pairs between two chemical formulas."""
    replacementSolutions = []
    
    # Get oxidation states for both formulas
    state1 = [guess_os(formula1)]
    state2 = [guess_os(formula2)]
    
    for assignment in state1:
        # Sort elements by oxidation state
        x1 = sorted(assignment.items(), key=lambda item: item[1])
        statelist1 = [pair[1] for pair in x1]
        elementlist1 = [pair[0] for pair in x1]
            
        for assignment2 in state2:
            x2 = sorted(assignment2.items(), key=lambda item: item[1])
            statelist2 = [pair[1] for pair in x2]
            elementlist2 = [pair[0] for pair in x2]

            if statelist1 == statelist2:
                # Group elements with same oxidation state
                elementGroupList = []
                elementGroup = []
                
                for i, state in enumerate(statelist2):
                    if i == 0:
                        elementGroup.append(elementlist2[i])
                    elif statelist2[i] == statelist2[i-1]:
                        elementGroup.append(elementlist2[i])
                        if i == len(statelist2) - 1:
                            elementGroupList.append(elementGroup)
                    else:
                        elementGroupList.append(elementGroup)
                        elementGroup = []
                        elementGroup.append(elementlist2[i])
                        if i == len(statelist2) - 1:
                            elementGroupList.append(elementGroup)

                # Generate all possible permutations of replacements
                pre_patterns = None
                for i, group in enumerate(elementGroupList):
                    if i == 0:
                        pre_patterns = list(itertools.permutations(group))
                    else:
                        patterns = list(itertools.permutations(group))
                        new_patterns = []
                        for p1 in pre_patterns:
                            for p2 in patterns:
                                new_patterns.append(list(p1) + list(p2))
                        pre_patterns = new_patterns

                # Create replacement dictionaries
                for pattern in pre_patterns:
                    replacementDict = []
                    for elem1, elem2 in zip(elementlist1, pattern):
                        if elem1 != elem2:
                            replacementDict.append((elem1, elem2))
                    if replacementDict:
                        replacementSolutions.append(replacementDict)

            else:
                # Handle formulas with different oxidation states
                query_formula = Composition(formula1)
                vec = formula_to_composition(query_formula, elements)
                N_ele = sum(vec != 0)
                comp_index = np.argsort(vec)[::-1][:N_ele]

                sug_formula = Composition(formula2)
                vec_sug = formula_to_composition(sug_formula, elements)
                comp_sug_index = np.argsort(vec_sug)[::-1][:N_ele]

                # Group by composition ratio
                comp = np.sort(vec)[::-1][:N_ele]
                keys = np.sort(list(set(comp)))[::-1]

                group_index = []
                group_sug_index = []
                for k in range(len(keys)):
                    x = (comp == keys[k])
                    group_index.append(comp_index[x])
                    group_sug_index.append(comp_sug_index[x])

                # Find optimal replacements
                replacement = []
                for l in range(len(keys)):
                    if len(group_index[l]) == 1:
                        replacement.append(group_sug_index[l])
                    else:
                        seq = group_sug_index[l]
                        pmt = list(itertools.permutations(seq))
                        dis_sum = np.zeros(len(pmt))
                        for m in range(len(pmt)):
                            dis_sum[m] = sum(element_dissimilarity[group_index[l], pmt[m]])
                        replacement.append(np.array(pmt[np.argmin(dis_sum)]))

                rep_index = np.concatenate(replacement)
                element_symbol = np.array(elements)
                q_ele = element_symbol[comp_index]
                rep_ele = element_symbol[rep_index]
                rep_dict = dict(zip(rep_ele, q_ele))
                replacementSolutions = [[(key, value) for key, value in rep_dict.items()]]

    return replacementSolutions

# pairs = replacementPair('NdOsO4', 'CeReO4')
# print(pairs)

def element_replace(cif_string, replacement_dict, file):
    """Replace elements in CIF file according to replacement dictionary."""
    for old, new in replacement_dict:
        cif_string = cif_string.replace(old, new)
    
    with open(file, 'w') as ofile:
        ofile.write(cif_string)
    return cif_string

def generate_full_anonymized_formula(full_formula):
    """Generate an anonymized version of a given formula."""
    comp = Composition(full_formula)
    elements = list(comp.as_dict().keys())
    element_map = {element: chr(65 + i) for i, element in enumerate(elements)}
    return ''.join(f"{element_map[element]}{int(count) if count != 1 else ''}" for element, count in comp.as_dict().items())

def get_relaxed_structure_and_energy(structure):
    """
    Relax structure and get its energy using the Relaxer.
    Returns both the relaxed structure and energy per atom.
    """
    relaxer = StructOptimizer()
    try:
        relax_results = relaxer.relax(structure, verbose=True)
        final_structure = relax_results['final_structure']
        final_energy_per_atom = float(relax_results['trajectory'].energies[-1] / len(structure))
        
        print(f"Relaxed lattice parameter is {final_structure.lattice.abc[0]:.3f} ?")
        print(f"Final energy is {final_energy_per_atom:.3f} eV/atom")
        
        return final_structure, final_energy_per_atom
    except Exception as e:
        print(f"Error in relaxation: {str(e)}")
        return structure, None


def switch_replacepairs(replacesolution):
    return [(x[1], x[0]) for x in replacesolution]

def manage_output_directory(outputdir):
    if os.path.exists(outputdir):
        shutil.rmtree(outputdir)
    os.makedirs(outputdir)
    print(f"Created fresh output directory: {outputdir}")