import hplib as hpl
import pandas as pd
import time

# load parameters
parameters = hpl.get_parameters(model='Generic', group_id=1, t_in=-7, t_out=52, p_th=10000)

# load one year input data, 1min time resolution
df = pd.read_csv('../input/TestYear.csv')
df['T_amb'] = df['T_in_primary'] # air/water heat pump -> T_amb = T_in_primary

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
    #results = hpl.simulate(t_in_primary=a, t_in_secondary=b, parameters=parameters, t_amb=c)
end = time.time()
print('Dauer mit Loop = '+str(end-start)+' Sekunden')
print(str(i)+' Aufrufe')

