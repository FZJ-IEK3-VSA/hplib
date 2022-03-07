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
| Date | heat pump certification date | 2016-07-27 to 2021-03-10 |
| Type | Type of heat pump model | Outdoor Air/Water, Brine/Water,  Water/Water |
| Subtype | Subtype of heat pump model | On-Off, Reglulated|
| Group ID | ID for combination of type and subtype | 1 - 6|
| Refrigerant | Refrigerant Type | R134a, R290, R32, R407c, R410a, other |
| Mass of Refrigerant [kg]| Mass of Refrigerant | 0.15 to 14.5 kg |
| SPL indoor [dBA]| Sound emissions indoor| 15 - 68 dBA|
| SPL outdoor [dBA]| Sound emissions outdoor| 33 - 78 dBA|
| PSB [W] | Eletrical power consumption, standby mode| 3 to 60 W |
| Climate | Climate definition for set points, which were used for parameter identification | average, colder, warmer |
| P_el_ref [W]| Electrical power at -7°C / 52°C | 881 to 23293 W |
| P_th_ref [W]| Thermal power at -7°C / 52°C | 2400 to 69880 W |
| p1-p4_P_th | Fit-Parameters for thermal power  | - |
| p1-p4_P_el | Fit-Parameters for electricl power  | P_el = P_el_ref * (p1*T_in + p2*T_out + p3 + p4*T_amb) |
| p1-p4_COP | Fit-Parameters for COP  | COP = p1*T_in + p2*T_out + p3 + p4*T_amb|
| MAPE_P_el | mean absolute percentage error for electrical input power (simulation vs. measurement) | average = 16,3 % |
| MAPE_COP | mean absolute percentage error for thermal input power (simulation vs. measurement) | average = 9,8 % |
| MAPE_P_th | mean absolute percentage error for coefficient of performance (simulation vs. measurement) | average = 19,7 % |