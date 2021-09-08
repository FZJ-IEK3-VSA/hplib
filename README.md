# hplib - heat pump library

Repository with code to
 
- build a **database** with relevant data from public Heatpump Keymark Datasets
- identify **efficiency parameters** from the database with a least-square regression model  
- **simulate** heat pump efficiency as well as  electrical & thermal power as time series.

For the simulation, it is possible to calculate outputs of a specific **manufacturer + model or** alternatively for an **9 different generic types of a heat pump**. 

## Documentation

If you're interested in how the database and parameters were calclulated, have a look into the Documentation.ipynb

There you also find a litte example on how to use the hplib.py for simulation.

## Usage

Download or clone repository:

`git clone https://github.com/RE-Lab-Projects/hplib.git`

Create the environment:

`conda env create --name hplib --file requirements.txt`

Create some code with `import hplib` and use the included functions `loadDatabase`, `getParameters` and `simulate`.

## Heat pump models and Group IDs
The hplib_database.csv contains the following number of heat pump models, sorted by Group ID

| [Group ID]: Count | Inverter | On-Off |
| :--- | :--- | :--- |
| Outdoor Air / Water | [1]: 371 | [4]: 23 |
| Brine / Water | [2]: 49 | [5]: 53 |
| Water / Water | [3]: 0 | [6]: 10 |

## Database

All resulting database CSV file are under [![License: CC BY 4.0](https://img.shields.io/badge/License-CC%20BY%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by/4.0/).

The following columns are available for every heat pump of this library

| Column | Description | Comment |
| :--- | :--- | :--- |
| Manufacturer | Name of the manufacturer | 30 manufacturers |
| Model | Name of the heat pump model | 513 models |
| Date | heat pump certification date | 2016-07-27 to 2021-03-10 |
| Type | Type of heat pump model | Outdoor Air/Water, Brine/Water,  Water/Water |
| Subtype | Subtype of heat pump model | On-Off, Inverter, 2-Stages|
| Group ID | ID for combination of type and subtype | 1 - 9|
| Refrigerant | Refrigerant Type | R134a, R290, R32, R407c, R410a, other |
| Mass of Refrigerant [kg]| Mass of Refrigerant | 0.15 to 14.5 kg |
| SPL indoor [dBA]| Sound emissions indoor| 15 - 68 dBA|
| SPL outdoor [dBA]| Sound emissions outdoor| 33 - 78 dBA|
| PSB [W] | Eletrical power consumption, standby mode| 3 to 60 W |
| Climate | Climate definition for set points, which were used for parameter identification | average, colder, warmer |
| P_el_ref [W]| Electrical power at -7°C / 52°C | 625 to 23293 W |
| P_th_ref [W]| Thermal power at -7°C / 52°C | 1700 to 69880 W |
| p1-p3_P_th | Fit-Parameters for thermal power  | P_th = P_th_ref * (p1 * T_in + p2 * T_out + p3) |
| p1-p3_P_th | Fit-Parameters for electricl power  | P_el = P_el_ref * (p1 * T_in + p2 * T_out + p3) |
| p1-p3_COP | Fit-Parameters for COP  | COP = p1 * T_in + p2 * T_out + p3 |

## Input-Data and further development
The European Heat Pump Association (EHPA) hosts a webiste with the results of laboratory measurements from the keymark certification process. For every heat pump model a pdf file can be downloaded from https://keymark.eu/en/products/heatpumps/certified-products.

This repository is based on all pdf files that were download for every manufacturer on 2021-03-12.

**Further development**

- [ ] Extend hplib.py and hplib_database.csv for cooling functionality 
- [ ] add some validation notebooks
- [ ] make hplib installable via `pip`

If you find errors or are interested in develop the hplib, please create an ISSUE and/or FORK this repository and create a PULL REQUEST.
