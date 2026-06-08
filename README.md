# Source data for *Discovery of D-Peptides that Allosterically Enhance SARS-CoV-2 3CLpro Activity by Stabilizing its Monomeric State*
This repository contains the source data supporting the manuscript titled 'Discovery of D-Peptides that Allosterically Enhance SARS-CoV-2 3CLpro Activity by Stabilizing its Monomeric State.' The dataset includes independent MD simulation replicas (triplicates), the coordinates of the stabilized complex structure, and the full suite of MD protocols and associated analysis scripts required to reproduce the study. If you have any questions, feel free to discuss in [Issues](https://github.com/laiyii/LY11-3CLpro-trajectory/issues).<br>

<p align="center">
  <img src="https://github.com/laiyii/LY11-3CLpro-trajectory/blob/main/workflow.png" />
</p>

## Requirement
> **Note:** Ubuntu 20.04 is recommended.
- GROMACS version: 2021.3-bioconda
- gmx_MMPBSA version: v1.5.5
- forcefield: charmm36-feb2021

## MD simulation
General procedure of MD simulation is described in supplementary information. To ensure full reproducibility, **forcefield files**, **comprehensive configuration (.mdp) files** and **related complex structures** have been deposited in the repository, while the specific execution commands for each simulation stage are detailed below.
### Preprocess and energy minimization
```shell
gcc gmx pdb2gmx -f start.pdb -o test.gro -water spce
gmx editconf -f test.gro -o test_box.gro -bt dodecahedron -d 1.0
gmx solvate -cp test_box.gro -cs spc216.gro -o test_solv.gro -p topol.top
gmx grompp -f ../ions.mdp -c test_solv.gro -p topol.top -o ions.tpr -maxwarn 2
gmx genion -s ions.tpr -o test_solv_neutral.gro -p topol.top -pname NA -nname CL -neutral -conc 0.1540
gmx grompp -f ../em.mdp -c test_solv_neutral.gro -p topol.top -o em.tpr
gmx mdrun -v -deffnm em
```
### NVT, NPT equilibration and MD simulation
```shell
gcc gmx grompp -f nvt.mdp -c em.gro -p topol.top -o nvt.tpr -r em.gro
gmx mdrun -deffnm nvt
gmx grompp -f npt.mdp -c nvt.gro -t nvt.cpt -p topol.top -o npt.tpr -r nvt.gro
gmx mdrun -deffnm npt
gmx grompp -f md.mdp -c npt.gro -t npt.cpt -p topol.top -o md.tpr -r npt.gro
gmx mdrun -deffnm md
```
### Postprocess and binding property analysis
```shell
gmx trjconv -f md.xtc -s md.tpr -o md_1.xtc -dt 0.5 -tu ns
gmx trjconv -f md_1.xtc -o md_nojump.xtc -s md.tpr -pbc nojump
gmx trjconv -f md_nojump.xtc -o mono28_%s_E2P.xtc -s md.tpr -center
gmx rms -n index.ndx -s md.tpr -f LY11_3CL.xtc -o LY11_3CL.xvg -tu ns
gmx_MMPBSA -O -i mmpbsa.in -cs md.tpr -ci index.ndx -cg 20 19 -ct LY11_3CL.xtc -cp topol.top -o LY11_3CL.dat -eo LY11_3CL.csv -nogui
```
## MD simulation results
We provide triplicate MD trajectories for the LY11-3CLpro system, generated from three distinct initial velocities as per Protein Science guidelines. Click [here](https://doi.org/10.5281/zenodo.20587106) to access the data.The /analysis folder contains the necessary scripts to replicate the quantitative findings and visualizations shown in Figure 5.
```shell
python result_cal_script.py input.pdb output_name
```
For example, to calculate domain dihedral distribution, the command is
```shell
python calc_MD_domain_dihedral.py input.pdb output_name
```


