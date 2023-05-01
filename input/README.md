## Input-Data
The European Heat Pump Association (EHPA) hosts a website with the results of laboratory measurements from the keymark certification process. For every heat pump model a pdf file can be downloaded from https://keymark.eu/en/products/heatpumps/certified-products.

This repository is based on all csv files that were downloaded for every manufacturer on 2023-04-17.




## Mapping dictionary

The downloaded .csv files contain the following columns:

* **modelID** - In case multiple heatpump models are downloaded, this column contains the model ID
* **varName** - Name/ID of the variable in the keymark database
* **value** - Value of the variable
* **temperature** - Integer indicating the temperature of the supplied medium (4,5 heating mode - 6,7 cooling mode)

| Temperature | Sink temperature |
| --- | ---------------- |
| int | °C               |
| 4   | 35               |
| 5   | 55               |
| 6   | 7 or 12          |
| 7   | 18 or 23         |
* **climate** - Integer indicating the climate zone (1-4)

| climate | Climate zone |
| --- | ------------ |
| int |              |
| 1   | warmer       |
| 2   | ?            |
| 3   | average      |
| 4   | ?            |
* **indoorUnittype** - TODO	
* **info** - TODO
* **hpType** - TODO



Following mapping dictionary is considered for the **varName**:

| Keymark varName  | hplib varName or ID             | Unit  | Description                                                                                 | Comment                                                                                             |
| ------------ | -------------------- | ----- | ------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------- |
| Manufacturer | manufacturers        | \-    |                                                                                             |                                                                                                     |
| Modelname    | models               | \-    |                                                                                             |                                                                                                     |
| title        | titels               | \-    | Unique identifier                                                                           |                                                                                                     |
| Date         | dates                |       | Certifcation date                                                                           |                                                                                                     |
| application  | types                |       | Type of heat pump model                                                                     | Medium of source / Medium of sink, e.g., Outdoor Air/ Water. Types are Outdoor Air, Water and Brine |
| Refrigerant  | refrigerants         |       | Refrigerant                                                                                 | R134a, R290, R32, R407c, R410a, other                                                               |
| Mass of Refr | mass_of_refrigerants | kg    | Mass of Refrigerant                                                                         |                                                                                                     |
| Energy       | supply_energy        |       |                                                                                             |                                                                                                     |
| EN12102_1_001 | spl_indoor           | dBA   | Sound emissions indoor at low power                                                         |                                                                                                     |
| EN12102_1_002 | spl_outdoor          | dbA   | Sound emissions outdoor at low power                                                        |                                                                                                     |
| EN14825_001  | eta                  | \-    | Efficiency?                                                                                 |                                                                                                     |
| EN14825_002  | p_rated              | kW    |                                                                                             |                                                                                                     |
| EN14825_003  | scop                 | \-    | Seasonal Coefficient of Performance                                                         |                                                                                                     |
| EN14825_004  | t_biv                | ° C   | Bicalence temperature                                                                       | Temperature at which other heat suppliers need to support                                           |
| EN14825_005  | tol                  | ° C   | TOL - Minimum temperature of source medium                                                  |                                                                                                     |
| EN14825_008  | p_th_minus7          | kW    | Thermal heat supply at -7°C supply temperature                                              |                                                                                                     |
| EN14825_009  | cop_minus7           | \-    | Coefficient of performance at at -7°C supply temperature                                    |                                                                                                     |
| EN14825_010  | p_th_2               | kW    | Thermal heat supply at 2 °C supply temperature                                              |                                                                                                     |
| EN14825_011  | cop_2                | \-    | Coefficient of performance at at 2 °C supply temperature                                    |                                                                                                     |
| EN14825_012  | p_th_7               | kW    | Thermal heat supply at 7 °C supply temperature                                              |                                                                                                     |
| EN14825_013  | cop_7                | \-    | Coefficient of performance at at 7 °C supply temperature                                    |                                                                                                     |
| EN14825_014  | p_th_12              | kW    | Thermal heat supply at 12 °C supply temperature                                             |                                                                                                     |
| EN14825_015  | cop_12               | \-    | Coefficient of performance at at 12 °C supply temperature                                   |                                                                                                     |
| EN14825_016  | p_th_tbiv            | kW    | Thermal heat supply at bilance temperature                                                  |                                                                                                     |
| EN14825_017  | cop_tbiv             | \-    | Coefficient of performance at bivalence temperature                                         |                                                                                                     |
| EN14825_018  | p_th_tol             | kW    | Thermal heat supply at minimal operating temperature                                        |                                                                                                     |
| EN14825_019  | cop_tol              | \-    | Thermal heat supply at minimal operating temperature                                        |                                                                                                     |
| EN14825_020  | rated_airflows       | m³/h  | Nominal air flow                                                                            |                                                                                                     |
| EN14825_022  | wtols                | ° C   | WTOL - Maximal temperature of supply medium                                                 |                                                                                                     |
| EN14825_023  | poffs                | kW    | Power supply off                                                                            |                                                                                                     |
| EN14825_024  | ptos                 | kW    | Power supply standby                                                                        |                                                                                                     |
| EN14825_025  | psbs                 | kW    | Power supply off with thermostat ready                                                      |                                                                                                     |
| EN14825_026  | pcks                 | kW    | Power supply with heating of ventilation                                                    |                                                                                                     |
| EN14825_027  | supp_energy_types    | \-    | Supplementary Heater: Type of energy input                                                  |                                                                                                     |
| EN14825_028  | p_sups               | kW    | Rated power of additional heater                                                            |                                                                                                     |
| EN14825_029  | E_heating            | kWh/a | Annual energy (power ?) consumption for heating                                             |                                                                                                     |
| EN14825_030  | p_design_cools       | kW    | Rated cooling load                                                                          |                                                                                                     |
| EN14825_031  | seers                | \-    | Seasonal Coefficient of Performance for cooling                                             |                                                                                                     |
| EN14825_032  | pdcs_35              | kW    | Cooling supply at 35°C                                                                      |                                                                                                     |
| EN14825_033  | eer_35               | \-    | Energy efficiency rating (EER) at 35 °C - cooling output in comparison to electricity input |                                                                                                     |
| EN14825_034  | pdcs_30              | kW    | Cooling supply at 30 °C                                                                     | Pdc Tj = 30°C                                                                                       |
| EN14825_035  | eer_30               | \-    | Energy efficiency rating (EER) at 30 °C - cooling output in comparison to electricity input |                                                                                                     |
| EN14825_036  | pdcs_25              | kW    | Cooling supply at 25 °C                                                                     |                                                                                                     |
| EN14825_037  | eer_25               | \-    | Energy efficiency rating (EER) at 25 °C - cooling output in comparison to electricity input |                                                                                                     |
| EN14825_038  | pdcs_20              | kW    | Cooling supply at 20 °C                                                                     |                                                                                                     |
| EN14825_039  | eer_20               | \-    | Energy efficiency rating (EER) at 20 °C - cooling output in comparison to electricity input |                                                                                                     |
| EN14825_041  | E_cooling            | kWh/a | Annual energy (power ?) consumption for cooling                                             |                                                                                                     |
| EN14825_047  |                      |       |                                                                                             |                                                                                                     |
| EN14825_048  |                      |       |                                                                                             |                                                                                                     |
| EN14825_049  |                      |       | Cdh Tj = +12 °C                                                                             |                                                                                                     |
| EN14825_050  |                      |       | Cdh Tj = +7 °C                                                                              |                                                                                                     |
| EN14825_053  |                      |       |                                                                                             |                                                                                                     |
| EN14825_054  | cdh_7                | \-    | Cdh Tj = +7 °C                                                                              |                                                                                                     |
| EN14825_055  |                      |       | Cdc Tj = 20 °C                                                                              |                                                                                                     |
