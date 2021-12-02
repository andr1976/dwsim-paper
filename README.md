# dwsim-paper
This repository contains supplementary material and information for the paper "Evaluation of an open-source chemical process simulator using a plant wide oil and gas separation plant flowsheet model as basis" by Anders Andreasen. 

![image](https://user-images.githubusercontent.com/58475535/144512151-81bf3f1f-4b1c-4ed5-972c-b9468d1ec3a7.png)

## Description
The results in the paper are generated with process simulations for both DWSIM and Aspen HYSYS. The following simulation files are available in the `simulations/` folder:

* `Base_case_benchmark.dwxmz`, the main DWSIM simulation file for comparison with HYSYS
* `Black oil EOS density.hsc`, the HYSYS counterpart
* `optimisation.dwxmz`, the DWSIM simulation file used for the 100 case run parametric study, slightly modified version of the base case
* `Optim.hsc`, the HYSYS simulation file used for the 100 case run parametric study, slightly modified version of the base case

Two main scripts are used for running the parametric studies, one for DWIM and one for HYSYS, both are located in the `scripts` folder. Run as: 

```
    python -i DWSIM_automation.py
```

The scripts uses a sampling plan already defined from the `data` folder and writes results to file in the root dir. Data files used in the paper are in the `data` folder. A third script is used to load the data files and make plots and summary statistics. 

## Requirements
In order to run the DWSIM simulation file, DWSIM can be downloaded from: https://dwsim.inforside.com.br/new/index.php/download/. Version 7.0.1 or above is recommended. The results have been prepared using the windows version. The automation script has not been tested on Linux with dotnet/Mono. 

For running the HYSYS automation script an installation of Aspentech HYSYS is required. 

For python, python38 has been used and the required modules/packages are listed in `requirements.txt`.

## References 
The simulation file used as basis for the present study originates from the paper: 

Andreasen, A. Applied Process Simulation-Driven Oil and Gas Separation Plant Optimization Using Surrogate Modeling and Evolutionary Algorithms. ChemEngineering 2020, 4, 11. https://doi.org/10.3390/chemengineering4010011
