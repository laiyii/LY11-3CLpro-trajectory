from Bio.PDB import PDBParser
import numpy as np
from sys import argv

p = PDBParser(QUIET=True)
file_name = argv[1]
out_name = argv[2]
structure = p.get_structure('all_traj', file_name)

def calculate_distances(p1, p2):
    d12 = np.linalg.norm(p1 - p2)
    return d12

def asert_hb_distance(at1, set_of_at2):
    all_length= []
    for at2 in set_of_at2:
        length = calculate_distances(at1, at2)
        all_length.append(length)
    return min(all_length)

def calc_distance_from_model(a_model):
    N_atoms = []
    for chain in a_model:
        for residue in chain:
            if residue.get_id()[1] == 166:
                atom_166_OE1 = residue['OE1']
                atom_166_OE2 = residue['OE2']
            if residue.get_id()[1] == 142:
                atom_142_N = residue['ND2']
                N_atoms.append(atom_142_N.get_coord())
            if residue.get_id()[1] == 163:
                atom_N163_ND1 = residue['ND1']
                atom_N163_NE2 = residue['NE2']
                N_atoms.append(atom_N163_ND1.get_coord())
                N_atoms.append(atom_N163_NE2.get_coord())
    OE1_distance = asert_hb_distance(atom_166_OE1.get_coord(), N_atoms)
    OE2_distance = asert_hb_distance(atom_166_OE2.get_coord(), N_atoms) 
    min_dist = min(OE1_distance, OE2_distance)   
    return min_dist


min_dist = []

for model in structure:
    min_dist.append(calc_distance_from_model(model))

import pandas as pd
df = pd.DataFrame(min_dist, columns=['min_dist_result'])
df.to_excel('%s.xlsx'%out_name, index=False)