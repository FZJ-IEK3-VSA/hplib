import hplib as hpl
import pandas as pd
import numpy as np
import time

# load parameters
parameters = hpl.get_parameters(model='i-SHWAK V4 06', group_id=1, t_in=-7, t_out=52, p_th=10000)

# load one year input data, 1min time resolution
temperature = pd.read_csv('../input/TestYear.csv')
temperature['T_amb'] = temperature['T_in_primary'] # air/water heat pump -> T_amb = T_in_primary

# Old way
"""
# simulate one time step
start = time.time()
results = hpl.simulate(t_in_primary=5, t_in_secondary=30, parameters=parameters, t_amb=5)
end = time.time()
print('Dauer mit Einzelaufruf = '+str(end-start)+' Sekunden')

# simulate array
start = time.time()
results = hpl.simulate(t_in_primary=df['T_in_primary'], t_in_secondary=df['T_in_secondary'], parameters=parameters, t_amb=df['T_amb'])
end = time.time()
print('Dauer mit Array = '+str(end-start)+' Sekunden')


# simulate loop
t_in_primary=df['T_in_primary'].values
t_in_secondary=df['T_in_secondary'].values
t_amb=df['T_amb'].values

start = time.time()
i=0
for a, b, c in zip(t_in_primary, t_in_secondary, t_amb):
    i=i+1
    results = hpl.simulate(t_in_primary=a, t_in_secondary=b, parameters=parameters, t_amb=c)
end = time.time()
print('Dauer mit Loop = '+str(end-start)+' Sekunden')
print(str(i)+' Aufrufe')
"""
# New Way
# Was macht was

heat_pump = hpl.HeatPump(parameters)

start = time.time()

results = heat_pump.simulate(t_in_primary=5, t_in_secondary=30, t_amb=5)
end = time.time()
print('Dauer Einzelaufruf mit neuem Konzept = '+str(end-start)+' Sekunden')

temp = temperature['T_in_primary'].to_numpy()
start = time.time()
results = heat_pump.simulate(temperature['T_in_primary'].to_numpy(),
                             temperature['T_in_secondary'].to_numpy(),
                             temperature['T_amb'].to_numpy())
end = time.time()
print('Dauer Array mit neuem Konzept = '+str(end-start)+' Sekunden')


i = 0
start = time.time()
for a, b, c in zip(temperature['T_in_primary'].values, temperature['T_in_secondary'].values, temperature['T_amb'].values):
    i = i + 1
    results = heat_pump.simulate(t_in_primary=a, t_in_secondary=b, t_amb=c)
end = time.time()
print('Dauer Loop mit neuem Konzept = '+str(end-start)+' Sekunden')
print(str(i)+' Aufrufe')


