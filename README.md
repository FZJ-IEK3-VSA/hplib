# hplib-database
Repository with code for building a database with efficiency parameters from public Heatpump Keymark datasets

WORK IN PROGRESS. PLEASE WAIT FOR FIRST RELEASE

## Input-Data
The European Heat Pump Association (EHPA) hosts a webiste with the results of laboratory measurements from the keymark certification process. For every heat pump model a pdf file can be downloaded from https://keymark.eu/en/products/heatpumps/certified-products.

This repository is based on all pdf files that were download for every manufacturer on 2021-03-12

## Pre-Processing
First of all, all pdf files were extracted an converted to txt files with the unix shell script "pdf2txt.sh"

## Processing
The main processing took place with the programming language python. To process the data by yourself, do the following steps
- setup environment with requirements
- download and pro-process new data
- run main.py

## Result
The resulting database CSV file is under Attribution 4.0 International licence [![License: CC BY 4.0](https://img.shields.io/badge/License-CC%20BY%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by/4.0/) and contains the following columns

| Column | Description | Comment |
| --- | --- | --- |
| manufacturer | Name of the manufacturer | *count?* |
| Model | Name of the heat pump model | *count?* |
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
