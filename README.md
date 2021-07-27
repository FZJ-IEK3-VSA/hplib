WORK IN PROGRESS. PLEASE WAIT FOR FIRST RELEASE

# hplib - heat pump library
Repository with code to 
- build a **database** with relevant data from public Heatpump Keymark Datasets
- identify **efficiency parameters** from the database with regression models  
- **simulate** heat pump efficiency and electrical & thermal power as time series.

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

Further more, based on this library four generic heat pumps with an average efficieny where created
- air/water | onoff
- air/water | inverter
- brine/water | onoff
- brine/water | inverter
----------------

## Input-Data
The European Heat Pump Association (EHPA) hosts a webiste with the results of laboratory measurements from the keymark certification process. For every heat pump model a pdf file can be downloaded from https://keymark.eu/en/products/heatpumps/certified-products.

This repository is based on all pdf files that were download for every manufacturer on 2021-03-12.

## Setup & Pre-Processing
First of all, you are free to download new keymark-files and process them with the following processing steps. The requirements are:
- clone this repository, e.g. `https://github.com/RE-Lab-Projects/hplib-database.git`
- change into the new directiory and setup an environment with `conda create --name hplib-database --file requirements.txt`
- put your pdf files into the folder `input/pdf`
- unix: *pdftotext* is included in many linux distributions | windows: install xpdf https://www.xpdfreader.com/
- run the unix bash script `./input/pdf2text.sh` or replace this step with an appropriate tool on windows/mac which converts pdf files to simple textfiles. For windows try 

## Usage of hplib

### create database
The main processing uses python / pandas to parse the text files and find the relevant data. It creates a dataframe and saves its content to `output/data_key.csv´
- first run `1_create_database.ipynb`



### fit efficiency parameters

In this database every measurement point has a input temperature, a output temperature and the thermal and electric power. From this data for every heatpump three graphs are fittet with the formula: 
Pth(Tin,Tout)=k1\*Tin+k2\*Tout+k3 and Pel(Tin,Tout)=k4\*Tin+k5\*Tout+k6 and COP(Tin,Tout)=k7\*Tin+k8\*Tout+k9. The parameters are saved in the `data_key_para.csv`.
  
-for this run `2_fit_parameters.ipynb`


### simulate a heat pump

To use these parameters you need to get the functions from `simulate.ipynb` and give a input temperature, output temperature and the model name. 
In those functions effects like a negative electrical value are neglected and a suplementary heater is defined. In return you get the Thermal Power, the electrical power, the electrical power of the suplementary heater and the COP as a list.
- there are some examples in `simulate.ipynb`
 
## Result

All resulting database CSV file are under Attribution 4.0 International licence [![License: CC BY 4.0](https://img.shields.io/badge/License-CC%20BY%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by/4.0/).
