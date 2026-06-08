from Bio.PDB import PDBParser
import numpy as np
from sys import argv
from dihedral_calc_0801 import cal_dih

p = PDBParser(QUIET=True)
file_name = argv[1]
out_name = argv[2]
structure = p.get_structure('all_traj', file_name)

def calc_com_of_a_domain(set_of_coords):
    return np.mean(set_of_coords, axis=0)

def output_domain_coord(a_model):
    domain12_coords = []
    domain3_coords = []
    for chain in a_model:
        for residue in chain:
            if residue.get_id()[1] >= 14 and residue.get_id()[1] <= 176:
                for atom in residue:
                    if atom.element != 'H':  # 排除氢原子
                        domain12_coords.append(atom.get_coord())
            if residue.get_id()[1] >= 199 and residue.get_id()[1] <= 290:
                for atom in residue:
                    if atom.element != 'H':  # 排除氢原子
                        domain3_coords.append(atom.get_coord())
    com_domain12 = calc_com_of_a_domain(np.array(domain12_coords))
    com_domain3 = calc_com_of_a_domain(np.array(domain3_coords))
    return com_domain12, com_domain3

def calc_dihedral_angle(a_model):
    com_domain12, com_domain3 = output_domain_coord(a_model)
    for chain in a_model:
        for residue in chain:
            if residue.get_id()[1] == 127:
                atom_127CA = residue['CA']
            if residue.get_id()[1] == 133:
                atom_N133 = residue['CA']            
    com_domain12 = np.array(com_domain12)
    com_domain3 = np.array(com_domain3)
    coord_127CA = np.array(atom_127CA.get_coord())
    coord_N133 = np.array(atom_N133.get_coord())
    phi = cal_dih(com_domain3, coord_127CA, coord_N133, com_domain12)
    # print(com_domain3, coord_127CA, coord_N133, com_domain12)
    angle = np.degrees(phi)
    if angle <=0:
        angle = angle + 360

    return angle

dihedral_result = []

for model in structure:
    dihedral_result.append(calc_dihedral_angle(model))

import pandas as pd
df = pd.DataFrame(dihedral_result, columns=['dihedral_result'])
df.to_excel('%s.xlsx'%out_name, index=False)