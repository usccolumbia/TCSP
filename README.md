# TCSP2.0
This repository contains the code and datasets for the paper:

Wei, Lai, Rongzhi Dong, Nihang Fu, Sadman Sadeed Omee, and Jianjun Hu. "TCSP 2.0: Template based crystal structure prediction with improved oxidation state prediction and chemistry heuristics." Computational Materials Science 261 (2026): 114317.


by <a href="http://mleg.cse.sc.edu" target="_blank">Machine Learning and Evolution Laboratory</a>, University of South Carolina.

Our TCSP 1.0: https://pubs.acs.org/doi/full/10.1021/acs.inorgchem.1c03879

### Python Dependencies
You can install all dependencies using the following command:
```
cd TCSP
conda env create -f tcsp_environment.yml
```

Activate the tcsp environment and install chgnet, transformers.
```
conda activate tcsp
pip install chgnet
pip install transformers
```
### BERTOS utility
BERTOS: transformer language model for oxidation state prediction
```
python download_bertos.py
```

If the script doesnt work. You can download if manually from [Figshare](https://figshare.com/articles/journal_contribution/BERTOS/28379117)

After downloading and extracting BERTOS, the directory structure should be:
```
TCSP/
   ├── BERTOS/  
      ├── model/
      ├── tokenizer/
      ├── dataset/
      ├── ...
      ├── bertos.py
   ├── data/
   ├── main.py
   ├── utils.py
   ├── ...
   └── README.md
```

### Datasets 
TCSP 2.0 templte database, it includes the Materials Project (MP) database, Materials Cloud database (both 2D and 3D), The Computational 2D Materials Database (C2DB), and Graph Networks for Materials Science database(GNoME).

All above datasets can be downloaded from [Figshare](https://figshare.com/articles/dataset/TCSP2_0_database/28379060)


#### Download Data
```
python download_database.py
```
If you cannot use the script above, you can manually download the datasets from the link and extract them.
The directory structure should be:
```
TCSP/
   ├── BERTOS/  
      ├── model/
      ├── tokenizer/
      ├── dataset/
      ├── ...
      ├── bertos.py
   ├── data/
       ├── matscholar-embedding.json
       ├── element_dissimilarity.pkl
       ├── structures.tar.gz
       ├── data.csv                    #all information for 731,293 cif files
       ├── mixed_data4/
           └── 731,293 cif files
   ├── main.py
   ├── utils.py
   ├── ...
   └── README.md
```
#### How to use TCSP 2.0
Here is an example of predicting a single crystal structure for SrTiO₃. You can modify the arguments using argparse:
```
python main.py --input SrTiO3
```

Check the predicted results in the output directory.
The output files are named using the format:
score_energy_spacegroup_templateFormula_templateSource.cif
Example:
e.g. 1.396_-8.15_sg123_La1U1O4_mp-753581.cif

To predict multiple crystal structures from a CSV file (e.g., data/180_testdata.csv):

```
python process_formulas.py 
```

If you want to collect the top-1 output of all results for multiple CSP runs:
```
python collect_results.py 
```

#### How to evaluate your predicted structures

To evaluate performance or compare results with ground truth structures, we use pymatgen StructureMatcher, Space Group Matching, and Consensus Rates.

Ensure you have the ground truth structure files with corresponding names before running the evaluation:
```
python comp_success.py
```

### Citation

If you use our work, please cite:

```bibtex

```


### Reference
Fu, Nihang, Jeffrey Hu, Ying Feng, Gregory Morrison, Hans‐Conrad zur Loye, and Jianjun Hu. "Composition Based Oxidation State Prediction of Materials Using Deep Learning Language Models." Advanced Science 10, no. 28 (2023): 2301011.

Jain, Anubhav, Shyue Ping Ong, Geoffroy Hautier, Wei Chen, William Davidson Richards, Stephen Dacek, Shreyas Cholia et al. "Commentary: The Materials Project: A materials genome approach to accelerating materials innovation." APL materials 1, no. 1 (2013).

Talirz, Leopold, Snehal Kumbhar, Elsa Passaro, Aliaksandr V. Yakutovich, Valeria Granata, Fernando Gargiulo, Marco Borelli et al. "Materials Cloud, a platform for open computational science." Scientific data 7, no. 1 (2020): 299.

Gjerding, Morten Niklas, Alireza Taghizadeh, Asbjørn Rasmussen, Sajid Ali, Fabian Bertoldo, Thorsten Deilmann, Nikolaj Rørbæk Knøsgaard et al. "Recent progress of the computational 2D materials database (C2DB)." 2D Materials 8, no. 4 (2021): 044002.

Merchant, Amil, Simon Batzner, Samuel S. Schoenholz, Muratahan Aykol, Gowoon Cheon, and Ekin Dogus Cubuk. "Scaling deep learning for materials discovery." Nature 624, no. 7990 (2023): 80-85.
