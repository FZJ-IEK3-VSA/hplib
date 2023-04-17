# hplib - heat pump library

Repository with code to
 
- build a **database** with relevant data from public Heatpump Keymark Datasets.
- identify **efficiency parameters** from the database with a least-square regression model, comparable to Schwamberger [1].  
- **simulate** heat pump efficiency (COP) as well as electrical (P_el) & thermal power (P_th) and massflow (m_dot) as time series.

For the simulation, it is possible to calculate outputs of a **specific manufacturer + model** or alternatively for one of **6 different generic heat pump types**.

[1] *K. Schwamberger: „Modellbildung und Regelung von Gebäudeheizungsanlagen mit Wärmepumpen“, VDI Verlag, Düsseldorf, Fortschrittsberichte VDI Reihe 6 Nr. 263, 1991.*

**For reference purposes:**
- DOI: [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.5521597.svg)](https://doi.org/10.5281/zenodo.5521597)
- Citation: Tjarko Tjaden, Hauke Hoops, Kai Rösken. (2021). RE-Lab-Projects/hplib: heat pump library (v2.0). Zenodo. https://doi.org/10.5281/zenodo.5521597

## Documentation

If you're interested in how the database and parameters were calclulated, have a look into the Documentation [HTML](http://htmlpreview.github.io/?https://github.com/RE-Lab-Projects/hplib/blob/main/notebooks/documentation.html) or [Jupyter-Notebook](https://github.com/RE-Lab-Projects/hplib/blob/main/notebooks/documentation.ipynb). There you also find a **simulation examples** and a **validation**.



---

## Heat pump models and Group IDs
The hplib_database.csv contains the following number of heat pump models, sorted by Group ID

| [Group ID]: Count | Regulated | On-Off |
| :--- | :--- | :--- |
| Outdoor Air / Water | [1]: 5812 | [4]: 40 |
| Brine / Water | [2]: 283 | [5]: 194 |
| Water / Water | [3]: 6| [6]: 6 |

## Database

All resulting database CSV file are under [![License: CC BY 4.0](https://img.shields.io/badge/License-CC%20BY%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by/4.0/).

The following columns are available for every heat pump of this library

| Column | Description | Comment |
| :--- | :--- | :--- |
| Manufacturer | Name of the manufacturer | 30 manufacturers |
| Model | Name of the heat pump model | 506 models |
| Titel | Name of the heat pump submodel | use titel name for simulating |
| Date | heat pump certification date | 2016-07-27 to 2021-03-10 |
| Type | Type of heat pump model | Outdoor Air/Water, Brine/Water,  Water/Water |
| Subtype | Subtype of heat pump model | On-Off, Regulated|
| Group ID | ID for combination of type and subtype | 1 - 6|
| Rated Power low T [kW] | Rated Power for low temperature level | -7/34 °C |
| Rated Power medium T [kW] | Rated Power for medium temperature level | -7/52 °C|
| Refrigerant | Refrigerant Type | R134a, R290, R32, R407c, R410a, other |
| Mass of Refrigerant [kg]| Mass of Refrigerant | 0.15 to 17.5 kg |
| SPL indoor [dBA]| Sound emissions indoor| 15 - 68 dBA|
| SPL outdoor [dBA]| Sound emissions outdoor| 33 - 78 dBA|
| Bivalence temperature [°C] | Minimum temperature heat pump is running without supplementary heater| *T_biv not used in simulation|
| Tolerance temperature [°C] | Minimum temperature heat pump is running with supplementary heater| *TOL not used in simulation|
| Max. water heating temperature [°C] | Maximum heating temperature | *T_max not used in simulation|
| Poff [W] | Eletrical power consumption, ? | *P_off not used in simulation (0-110 W)|
| PTOS [W] | Eletrical power consumption, ? | *P_tos not used in simulation (0-404 W)|
| PSB [W] | Eletrical power consumption, standby mode | *P_sb not used in simulation (0-110 W)|
| PCKS [W] | Eletrical power consumption, ? | *P_cks not used in simulation (0-99 W)|
| eta low T [%] | Efficiency for low temperature level| 105-300% |
| eta medium T [%] | Efficiency for medium temperature level| 107-202% |
| SCOP | seasonal COP | 2,7-7,7 |
| SEER low T | seasonal EER for low Temperature Level | 3,39-12,93 |
| SEER medium T | seasonal EER for medium Temperature Level | 5,04-13,87 |
| P_th_h_ref [W]| Thermal heating power at -7°C / 52°C | 2400 to 69880 W |
| P_th_c_ref [W]| Thermal cooling power at ? | 3000 to 53200 W |
| P_el_h_ref [W]| Electrical power at -7°C / 52°C | 881 to 29355 W |
| P_el_c_ref [W]| Electrical power at ? | 881 to 17647 W |
| COP_ref | COP at -7°C / 52°C | 1,53 to 7,95 |
| EER_ref | Electrical power at ? | 1,99 to 10,8 |
| p1-p4_P_th | Fit-Parameters for thermal power  | - |
| p1-p4_P_el | Fit-Parameters for electricl power  | P_el = P_el_ref * (p1*T_in + p2*T_out + p3 + p4*T_amb) |
| p1-p4_COP | Fit-Parameters for COP  | COP = p1*T_in + p2*T_out + p3 + p4*T_amb|
| MAPE_P_th | mean absolute percentage error for coefficient of performance (simulation vs. measurement) | average = 19,7 % |
| MAPE_P_el | mean absolute percentage error for electrical input power (simulation vs. measurement) | average = 16,3 % |
| MAPE_COP | mean absolute percentage error for thermal input power (simulation vs. measurement) | average = 9,8 % |
| MAPE_P_dc | mean absolute percentage error for coefficient of performance (simulation vs. measurement) | average = 19,7 % |
| MAPE_P_el | mean absolute percentage error for electrical input power (simulation vs. measurement) | average = 16,3 % |
| MAPE_EER | mean absolute percentage error for electrical input power (simulation vs. measurement) | average = 16,3 % |

## Usage

- Get repository with pip:
  - `pip install hplib`

or: 

- Download or clone repository:
  - `git clone https://github.com/RE-Lab-Projects/hplib.git`
  - Create the environment:
    - `conda env create --name hplib --file requirements.txt`

Create some code with `from hplib import hplib` and use the included functions `hplib.load_database()`, `hplib.get_parameters`, `hplib.HeatPump()`, `hplib.HeatPump.simulate()`, `hplib.HeatingSystem.calc_brine_temp()` and `hplib.HeatingSystem.calc_heating_dist_temp()`


**Hint:** The csv files in the `output` folder are for documentation and validation purpose. The code and database files, which are meant to be used for simulations, are located in the `hplib` folder. 

---

## Input-Data
The European Heat Pump Association (EHPA) hosts a website with the results of laboratory measurements from the keymark certification process. For every heat pump model a pdf file can be downloaded from https://keymark.eu/en/products/heatpumps/certified-products.

This repository is based on all pdf files that were download for every manufacturer on 2023-04-17.

## Further development & possibilities to collaborate

If you find errors or are interested in developing together on the heat pump library, please create an ISSUE and/or FORK this repository and create a PULL REQUEST.
