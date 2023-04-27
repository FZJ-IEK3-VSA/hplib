## src

This folder contains the main files for usage:

|File|Content|
|:---|:---|
|documentation.ipynb|Explanations how the database was created. Examples how to use hplib.py for simulation. Validation calculations and plots.|
|hplib_database.csv|Database with one row per heatpump, containing relevant data and simulation parameters|
|hplib.py|Functions for simulations purposes|

Columns and Description from **hplib_database.csv**

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
