WORK IN PROGRESS. PLEASE WAIT FOR FIRST RELEASE

# hplib
Repository with code to 
- build a **database** with relevant data from public Heatpump Keymark Datasets
- identify **efficiency parameters** from the database with regression models  
- **simulate** heat pump efficiency and electrical & thermal power as time series

## Input-Data
The European Heat Pump Association (EHPA) hosts a webiste with the results of laboratory measurements from the keymark certification process. For every heat pump model a pdf file can be downloaded from https://keymark.eu/en/products/heatpumps/certified-products.

This repository is based on all pdf files that were download for every manufacturer on 2021-03-12

## Setup & Pre-Processing
First of all, you are free to download new keymark-files and process them with the following processing steps. The requirements are:
- clone this repository, e.g. `https://github.com/RE-Lab-Projects/hplib-database.git`
- change into the new directiory and setup an environment with `conda create --name hplib-database --file requirements.txt`
- put your pdf files into the folder `input/pdf`
- unix: *pdftotext* is included in many linux distributions | windows: install xpdf https://www.xpdfreader.com/
- run the unix bash script `./input/pdf2text.sh` or replace this step with an appropriate tool on windows/mac which converts pdf files to simple textfiles. For windows try 

## Processing
The main processing uses python / pandas to parse the text files and find the relevant data. It creates a dataframe and saves its content als CSV file.
- simply run `main.py`

## Result
The resulting database CSV file is under Attribution 4.0 International licence [![License: CC BY 4.0](https://img.shields.io/badge/License-CC%20BY%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by/4.0/) and contains the following columns

| Column | Description | Comment |
| --- | --- | --- |
| manufacturer | Name of the manufacturer | 50 manufacturers |
| Model | Name of the heat pump model | 824 models |
| Date | heat pump certification date | 2016-07-15 to 2021-12-18 |
| Type | Type of heat pump model | Brine/Water, Air/Water, Water/Water |
| Refrigerant | Refrigerant Type | R123a, R290, R32, R407c, R410a |
| Mass of Refrigerant | Mass of Refrigerant | 0.15 to 21 kg |
| Poff | Electrical power consumption, off mode | 0 to 116 W |
| Psb | Eletrical power consumption, standby mode| 0 to 116 W |
| Guideline | Values depend on measurements regarding guideline | EN 14825 |
| Climate | set point: climate definition for set points | average, colder, warmer |
| T_in | set point: source temperature | -15 to 12 °C |
| T_out | set point: output temperature | 24 to 55 °C |
| P_th | set point: thermal power | 0 to 84.7 kW |
| P_el | set point: electrical power | 0 to 29.5 kW |
| COP | set point: coefficient of performance | 0 to 12.8 |
