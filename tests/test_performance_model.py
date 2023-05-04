import pytest
import os
import numpy as np
import pandas as pd
import hplib.hplib as hpl




def test_validate_performance_model():
    """
    Tests the performance prediction of  a single heat pump
    """

    # define model
    model = 'AEROTOP S07.2'


    # Load parameters of generic air/water | regulated
    parameters = hpl.get_parameters(model)
    heatpump=hpl.HeatPump(parameters)

    # Create input series
    T_in=2 # * C
    T_out=np.array([35, 55]) # * C

    results = heatpump.simulate(t_in_primary=T_in, t_in_secondary=T_out, t_amb=T_in, mode=1)

    # values read from heatpumpkeymark.com for the model
    np.isclose(results['P_th'][0]/1000, 5.01, atol=0.5) # low temnperature
    np.isclose(results['P_th'][1]/1000, 3.89, atol=0.7) # medium temperature

    # Comment lk: Tolerances need to be quite high...

def test_cop_performance_schwarmberger():
    """
    Checks if proper COP values can be calculated by the schwarmberger model
    """
    parameters = hpl.get_parameters(model='Generic_average', group_id=1, t_in=-7, 
                                    t_out=55, 
                                    p_th=10000)
    heatpump = hpl.HeatPump(parameters)
    
    results = heatpump.simulate(t_in_primary=-7, t_in_secondary=55, t_amb=-7, mode=1)
    
    assert results['COP'] > 1
    assert results['COP'] < 3