from Bio.PDB import PDBParser
import numpy as np
import pandas as pd
from sys import argv

# 使用方法: python calc_MD_sc_bb_hbond.py input.pdb output_name
# 依赖: numpy, pandas, biopython

p = PDBParser(QUIET=True)
file_name = argv[1]
out_name = argv[2]
structure = p.get_structure('all_traj', file_name)

def get_min_distance(atoms_a, atoms_b):
    """计算两组原子之间的最小欧几里得距离"""
    if not atoms_a or not atoms_b:
        return float('inf')
    
    min_dist = float('inf')
    for a in atoms_a:
        coord_a = a.get_coord()
        for b in atoms_b:
            coord_b = b.get_coord()
            dist = np.linalg.norm(coord_a - coord_b)
            if dist < min_dist:
                min_dist = dist
    return min_dist

def analyze_interactions(model):
    # 初始化结果
    has_salt_bridge = 0
    has_sc_bb_hbond = 0
    
    chain = next(iter(model)) # 获取第一条链
    
    # 安全获取残基
    def get_res(res_id):
        if res_id in chain:
            return chain[res_id]
        return None

    r131 = get_res(131)
    r289 = get_res(289)
    t198 = get_res(198)

    # --- 分析 1: 131 与 289 的盐桥 (侧链 - 侧链) ---
    # 保持不变：R131(Arg) 正电基团 vs 289(Asp/Glu) 负电基团
    if r131 and r289:
        # R131 侧链氮
        cation_atoms = [atom for atom in r131 if atom.name in ['NH1', 'NH2', 'NZ', 'NE']]
        # 289 侧链氧
        anion_atoms = [atom for atom in r289 if atom.name in ['OD1', 'OD2', 'OE1', 'OE2']]
        
        dist = get_min_distance(cation_atoms, anion_atoms)
        if dist < 4.0: 
            has_salt_bridge = 1

    # --- 分析 2: R131(侧链) 与 T198(主链) 的氢键 ---
    # R131 侧链作为供体 (Nitrogens) -> T198 主链作为受体 (Oxygen)
    if r131 and t198:
        # 1. 筛选 R131 侧链参与氢键的原子 (精氨酸的胍基和Epsilon氮)
        r131_sc_donors = [atom for atom in r131 if atom.name in ['NH1', 'NH2', 'NE']]
        
        # 2. 筛选 T198 主链受体原子 (羰基氧)
        # 注意：主链 N 通常是供体，不太可能与 Arg 侧链(也是供体)形成氢键
        t198_bb_acceptor = [atom for atom in t198 if atom.name == 'O']
        
        # 3. 计算最小距离
        dist_hbond = get_min_distance(r131_sc_donors, t198_bb_acceptor)
        
        # 4. 判断 (重原子距离 < 3.5 Å 通常被认为是氢键形成的几何标准)
        if dist_hbond < 3.5:
            has_sc_bb_hbond = 1

    return [has_salt_bridge, has_sc_bb_hbond]

results = []

print(f"正在分析文件: {file_name}")
print("包含计算: 1. R131-289 盐桥, 2. R131(侧链)-T198(主链) 氢键")

for i, model in enumerate(structure):
    res = analyze_interactions(model)
    results.append(res)
    if i % 100 == 0:
        print(f"已处理 {i} 帧...", end='\r')

# 保存结果
# 修改列名以反映新的计算逻辑
columns = ['SaltBridge_131_289', 'HBond_R131_SC_T198_BB']
df = pd.DataFrame(results, columns=columns)

output_filename = '%s.xlsx' % out_name
df.to_excel(output_filename, index=False)
print(f"\n计算完成，结果已保存至 {output_filename}")