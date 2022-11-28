<a href="https://www.fz-juelich.de/en/iek/iek-3"><img src="https://raw.githubusercontent.com/OfficialCodexplosive/README_Assets/862a93188b61ab4dd0eebde3ab5daad636e129d5/FJZ_IEK-3_logo.svg" alt="FZJ Logo" width="300px"></a>

# hplib - heat pump library

Repository with code to
 
- build a **database** with relevant data from public Heatpump Keymark Datasets.
- identify **efficiency parameters** from the database with a least-square regression model, comparable to Schwamberger [1].  
- **simulate** heat pump efficiency (COP) as well as electrical (P_el) & thermal power (P_th) and massflow (m_dot) as time series.

For the simulation, it is possible to calculate outputs of a **specific manufacturer + model** or alternatively for one of **6 different generic heat pump types**.

[1] *K. Schwamberger: „Modellbildung und Regelung von Gebäudeheizungsanlagen mit Wärmepumpen“, VDI Verlag, Düsseldorf, Fortschrittsberichte VDI Reihe 6 Nr. 263, 1991.*

**For reference purposes:**
- DOI: [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.5521597.svg)](https://doi.org/10.5281/zenodo.5521597)
- Citation: Tjarko Tjaden, Hauke Hoops, Kai Rösken. (2021). RE-Lab-Projects/hplib: heat pump library (v1.8). Zenodo. https://doi.org/10.5281/zenodo.5521597

## Documentation

If you're interested in how the database and parameters were calclulated, have a look into the Documentation [HTML](http://htmlpreview.github.io/?https://github.com/RE-Lab-Projects/hplib/blob/main/notebooks/documentation.html) or [Jupyter-Notebook](https://github.com/RE-Lab-Projects/hplib/blob/main/notebooks/documentation.ipynb). There you also find a **simulation examples** and a **validation**.



---

## Heat pump models and Group IDs
The hplib_database.csv contains the following number of heat pump models, sorted by Group ID

| [Group ID]: Count | Reglulated | On-Off |
| :--- | :--- | :--- |
| Outdoor Air / Water | [1]: 366 | [4]: 23 |
| Brine / Water | [2]: 54 | [5]: 53 |
| Water / Water | [3]: 0 | [6]: 10 |

## Database

All resulting database CSV file are under [![License: CC BY 4.0](https://img.shields.io/badge/License-CC%20BY%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by/4.0/).

The following columns are available for every heat pump of this library

| Column | Description | Comment |
| :--- | :--- | :--- |
| Manufacturer | Name of the manufacturer | 30 manufacturers |
| Model | Name of the heat pump model | 506 models |
| Date | heat pump certification date | 2016-07-27 to 2021-03-10 |
| Type | Type of heat pump model | Outdoor Air/Water, Brine/Water,  Water/Water |
| Subtype | Subtype of heat pump model | On-Off, Regulated|
| Group ID | ID for combination of type and subtype | 1 - 6|
| Refrigerant | Refrigerant Type | R134a, R290, R32, R407c, R410a, other |
| Mass of Refrigerant [kg]| Mass of Refrigerant | 0.15 to 14.5 kg |
| SPL indoor [dBA]| Sound emissions indoor| 15 - 68 dBA|
| SPL outdoor [dBA]| Sound emissions outdoor| 33 - 78 dBA|
| PSB [W] | Eletrical power consumption, standby mode| 3 to 60 W |
| Climate | Climate definition for set points, which were used for parameter identification | average, colder, warmer |
| P_el_h_ref [W]| Electrical power at -7°C / 52°C | 881 to 23293 W |
| P_th_h_ref [W]| Thermal heating power at -7°C / 52°C | 2400 to 69880 W |
| p1-p4_P_th | Fit-Parameters for thermal power  | - |
| p1-p4_P_el | Fit-Parameters for electricl power  | P_el = P_el_ref * (p1 * T_in + p2 * T_out + p3 + p4 * T_amb) |
| p1-p4_COP | Fit-Parameters for COP  | COP = p1 * T_in + p2 * T_out + p3 + p4 * T_amb|
| p1-p4_EER | Fit-Parameters for EER  | EER = p1 * T_in + p2 * T_out + p3 + p4 * T_amb|
| MAPE_P_el | mean absolute percentage error for electrical input power (simulation vs. measurement) | average over all heat pump models = 16,3 % |
| MAPE_COP | mean absolute percentage error for thermal input power (simulation vs. measurement) | average over all heat pump models = 9,8 % |
| MAPE_P_th | mean absolute percentage error for coefficient of performance (simulation vs. measurement) | average over all heat pump models = 19,7 % |

## Usage

- Get repository with pip:
  - `pip install hplib`

or: 

- Download or clone repository:
  - `git clone https://github.com/RE-Lab-Projects/hplib.git`
  - Create the environment:
    - `conda env create --name hplib --file requirements.txt`

Create some code with `from hplib import hplib` and use the included functions `hplib.load_database()`, `hplib.get_parameters`, `hplib.same_built_type()`,  `hplib.HeatPump`, `hplib.HeatPump.simulate`, `hplib.HeatingSystem.calc_brine_temp()` and `hplib.HeatingSystem.calc_heating_dist_temp()`


**Hint:** The csv files in the `output` folder are for documentation and validation purpose. The code and database files, which are meant to be used for simulations, are located in the `hplib` folder. 

---

## Input-Data
The European Heat Pump Association (EHPA) hosts a website with the results of laboratory measurements from the keymark certification process. For every heat pump model a pdf file can be downloaded from https://keymark.eu/en/products/heatpumps/certified-products.

This repository is based on all pdf files that were download for every manufacturer on 2021-03-12.

## Further development & possibilities to collaborate

If you find errors or are interested in developing together on the heat pump library, please create an ISSUE and/or FORK this repository and create a PULL REQUEST.

## License
MIT License

Copyright (c) 2022

You should have received a copy of the MIT License along with this program.
If not, see https://opensource.org/licenses/MIT

## About Us
<p align="center"><a href="https://www.fz-juelich.de/en/iek/iek-3"><img src="https://github.com/OfficialCodexplosive/README_Assets/blob/master/iek3-wide.png?raw=true" alt="Institut TSA"></a></p>
We are the <a href="https://www.fz-juelich.de/en/iek/iek-3">Institute of Energy and Climate Research - Techno-economic Systems Analysis (IEK-3)</a> belonging to the <a href="https://www.fz-juelich.de/en">Forschungszentrum Jülich</a>. Our interdisciplinary department's research is focusing on energy-related process and systems analyses. Data searches and system simulations are used to determine energy and mass balances, as well as to evaluate performance, emissions and costs of energy systems. The results are used for performing comparative assessment studies between the various systems. Our current priorities include the development of energy strategies, in accordance with the German Federal Government’s greenhouse gas reduction targets, by designing new infrastructures for sustainable and secure energy supply chains and by conducting cost analysis studies for integrating new technologies into future energy market frameworks.
