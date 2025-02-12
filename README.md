# TCSP2.0
This repository contains the code and datasets for the paper:

xxxx

by <a href="http://mleg.cse.sc.edu" target="_blank">Machine Learning and Evolution Laboratory</a>, University of South Carolina.

Our TCSP 1.0: https://pubs.acs.org/doi/full/10.1021/acs.inorgchem.1c03879

### Python Dependencies
You can install all the dependencies listed inside using the following command:
```
cd TCSP
conda env create -f tcsp_environment.yml
```

Activate the tcsp env and install chgnet.
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

Download BERTOS from the above link, then extract it.
After the above, the directory should be:
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
If you cannot use the above script, you can download datasets from the above link manually, then extract it.
The directory should be:
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
An example to predict a single crystal structure SrTiO3. You can set different argsparse.
```
python main.py --input SrTiO3
```

An example to predict multiple crystal structures in a csv file (e.g. 180_testdata.csv). 

```
python process_formulas.py 
```

If you want to collect the results for multiple CSP.
```
python collect_results.py 
```

#### How to evaluate your predicted structures

If you want to evaluate the performance or compare the results to the ground truth structures. (Here we use pymatgen StructureMatcher, Space Group Match, and Consensus Rates)
```
python comp_success.py
```

### Citation

If you use our work, please cite:

```bibtex

```


### Reference

