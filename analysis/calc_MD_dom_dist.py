from Bio.PDB import PDBParser
import numpy as np
from sys import argv
import pandas as pd

# 使用方法: python calc_MD_domain_distance.py input.pdb output_name
# 例如: python calc_MD_domain_distance.py my_trajectory.pdb result_distance

p = PDBParser(QUIET=True)
file_name = argv[1]
out_name = argv[2]
structure = p.get_structure('all_traj', file_name)

def calc_com_of_a_domain(set_of_coords):
    # 计算坐标集合的几何中心 (质心)
    return np.mean(set_of_coords, axis=0)

def output_domain_dist(a_model):
    group1_coords = [] # 用于存储 199-290 号残基的原子坐标
    group2_coords = [] # 用于存储 14-176 号残基的原子坐标
    
    for chain in a_model:
        for residue in chain:
            res_id = residue.get_id()[1] # 获取残基编号
            
            # 筛选 199-290 号残基
            if res_id >= 199 and res_id <= 290:
                for atom in residue:
                    group1_coords.append(atom.get_coord())
            
            # 筛选 14-176 号残基
            if res_id >= 14 and res_id <= 176:
                for atom in residue:
                    group2_coords.append(atom.get_coord())
                    
    # 计算两个组的质心 (Center of Mass)
    # 注意：如果PDB中缺失这些残基，这里可能会报错，建议确保PDB完整
    com_group1 = calc_com_of_a_domain(np.array(group1_coords))
    com_group2 = calc_com_of_a_domain(np.array(group2_coords))
    
    # 计算两个质心之间的欧几里得距离
    distance = np.linalg.norm(com_group1 - com_group2)
    
    return distance

dist_result = []

print("正在处理模型并计算距离...")
for model in structure:
    dist_result.append(output_domain_dist(model))

# 保存结果到Excel
df = pd.DataFrame(dist_result, columns=['distance_result'])
output_filename = '%s.xlsx' % out_name
df.to_excel(output_filename, index=False)
print(f"计算完成，结果已保存至 {output_filename}")