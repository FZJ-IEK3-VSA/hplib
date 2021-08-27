# hplib - heat pump library

Repository with code to
 
- build a **database** with relevant data from public Heatpump Keymark Datasets
- identify **efficiency parameters** from the database with a least-square regression model  
- **simulate** heat pump efficiency as well as  electrical & thermal power as time series.

For the simulation, it is possible to calculate outputs of a specific **manufacturer + model or** alternatively for an **9 different types of a generic heat pump** 

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

| [Group ID]: Count | Inverter | On-Off | Two-Stage|
| :---: | :---: | :---: | :---: |
| Outdoor Air / Water | [1]: 371 | [4]: 23 |[7]: 3 |
| Brine / Water | [2]: 49 | [5]: 53 | [8]: 4 |
| Water / Water | [3]: 0 | [6]: 10 | [9]: 0 |

## Database

All resulting database CSV file are under [![License: CC BY 4.0](https://img.shields.io/badge/License-CC%20BY%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by/4.0/).

The following columns are available for every heat pump of this library

| Column | Description | Comment |
| --- | --- | --- |
| manufacturer | Name of the manufacturer | 50 manufacturers |
| Model | Name of the heat pump model | 3235 models |
| Date | heat pump certification date | 2016-07-15 to 2021-12-18 |
| Type | Type of heat pump model | Brine/Water, Air/Water, Water/Water |
| Modus | conrol of heatpump model | On-Off, Inverter, two-stages|
| Refrigerant | Refrigerant Type | R123a, R290, R32, R407c, R410a |
| Mass of Refrigerant | Mass of Refrigerant | 0.15 to 21 kg |
| SPL indoor/outdoor | Sound emissions | 0 - 84 dBA|
| Prated | thermal Power output by the manufacturer | 2,86 to 84,67 kW |
| Psb | Eletrical power consumption, standby mode| 0 to 60 W |
| Guideline | Values depend on measurements regarding guideline | EN 14825 |
| Climate | set point: climate definition for set points | average, colder, warmer |
| P_el_n | set point: electrical power at -7/34 | 0.75 to 17.58 kW |
| P_th_max | set point thermal power at -7/52 | 2.4 to 70 kW |
| k1-k3 | parameters to fit thermal power  | with formula: (k1\*T(in)+k2\*T(out)+k3)\*P_th_n |
| k4-k6 | parameters to fit electrical power  | with formula: (k4\*T(in)+k5\*T(out)+k6) \*P_el_n|
| k7-k9 | parameters to fit COP | with formula: k7\*T(in)+k8\*T(out)+k9 |
| Group | Groups represent the Modus and Type of heatpump | 1: Air Water-Inverter, 2: Brine/Water-Inverter, 4:Air/Water-On-Off, 5:Brine/Water-On-Off

## Input-Data and further development
The European Heat Pump Association (EHPA) hosts a webiste with the results of laboratory measurements from the keymark certification process. For every heat pump model a pdf file can be downloaded from https://keymark.eu/en/products/heatpumps/certified-products.

This repository is based on all pdf files that were download for every manufacturer on 2021-03-12.

**Further development**

- [ ] Extend hplib.py and hplib_database.csv for cooling functionality 
- [ ] add some validation notebooks
- [ ] make hplib installable via `pip`

If you find errors or are interested in develop the hplib, please create an ISSUE and/or FORK this repository and create a PULL REQUEST.
