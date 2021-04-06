# hplib-database
Repository with code for building a database with efficiency parameters from public Heatpump Keymark datasets

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
The resulting database CSV file is under Attribution 4.0 International licence [![License: CC BY 4.0](https://img.shields.io/badge/License-CC%20BY%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by/4.0/)
