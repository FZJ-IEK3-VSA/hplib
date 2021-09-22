"""
The ``hplib`` module provides a set of functions for simulating the performance of heat pumps.
"""
import pandas as pd
import scipy
from typing import Any, Tuple


def load_database() -> pd.DataFrame:
    """
    Loads data from hplib_database.

    Returns
    -------
    df : pd.DataFrame
        Content of the database
    """
    df = pd.read_csv('hplib_database.csv')
    return df


def get_parameters(model: str, group_id: int = 0,
                   t_in: int = 0, t_out: int = 0, p_th: int = 0) -> pd.DataFrame:
    """
    Loads the content of the database for a specific heat pump model
    and returns a pandas ``DataFrame`` containing the heat pump parameters.

    Parameters
    ----------
    model : str
        Name of the heat pump model or "Generic".
    group_id : numeric, default 0
        only for model "Generic": Group ID for subtype of heat pump. [1-6].
    t_in : numeric, default 0
        only for model "Generic": Input temperature :math:`T` at primary side of the heat pump. [°C]
    t_out : numeric, default 0
        only for model "Generic": Output temperature :math:`T` at secondary side of the heat pump. [°C]
    p_th : numeric, default 0
        only for model "Generic": Thermal output power at setpoint t_in, t_out. [W]

    Returns
    -------
    parameters : pd.DataFrame
        Data frame containing the model parameters.
    """
    df = pd.read_csv('hplib_database.csv', delimiter=',')
    df = df.loc[df['Model'] == model]
    parameters = pd.DataFrame()
    parameters['Manufacturer']=(df['Manufacturer'].values.tolist())
    parameters['Model'] = (df['Model'].values.tolist())
    try:
        parameters['MAPE_COP']=df['MAPE_COP'].values.tolist()
        parameters['MAPE_P_el']=df['MAPE_P_el'].values.tolist()
        parameters['MAPE_P_th']=df['MAPE_P_th'].values.tolist()
    except:
        pass
    parameters['P_th_ref [W]'] = (df['P_th_ref [W]'].values.tolist())
    parameters['P_el_ref [W]'] = (df['P_el_ref [W]'].values.tolist())
    parameters['COP_ref'] = (df['COP_ref'].values.tolist())
    parameters['Group'] = (df['Group'].values.tolist())
    parameters['p1_P_th [1/°C]'] = (df['p1_P_th [1/°C]'].values.tolist())
    parameters['p2_P_th [1/°C]'] = (df['p2_P_th [1/°C]'].values.tolist())
    parameters['p3_P_th [-]'] = (df['p3_P_th [-]'].values.tolist())
    parameters['p4_P_th [1/°C]'] = (df['p4_P_th [1/°C]'].values.tolist())
    parameters['p1_P_el [1/°C]'] = (df['p1_P_el [1/°C]'].values.tolist())
    parameters['p2_P_el [1/°C]'] = (df['p2_P_el [1/°C]'].values.tolist())
    parameters['p3_P_el [-]'] = (df['p3_P_el [-]'].values.tolist())
    parameters['p4_P_el [1/°C]'] = (df['p4_P_el [1/°C]'].values.tolist())
    parameters['p1_COP [-]'] = (df['p1_COP [-]'].values.tolist())
    parameters['p2_COP [-]'] = (df['p2_COP [-]'].values.tolist())
    parameters['p3_COP [-]'] = (df['p3_COP [-]'].values.tolist())
    parameters['p4_COP [-]'] = (df['p4_COP [-]'].values.tolist())

    if model == 'Generic':
        parameters = parameters.iloc[group_id - 1:group_id]
        
        p_th_ref = fit_p_th_ref(t_in, t_out, group_id, p_th)
        parameters.loc[:, 'P_th_ref [W]'] = p_th_ref
        t_in_hp = [-7,0,10] # air/water, brine/water, water/water
        t_out_fix = 52
        t_amb_fix = -7
        p1_cop = parameters['p1_COP [-]'].array[0]
        p2_cop = parameters['p2_COP [-]'].array[0]
        p3_cop = parameters['p3_COP [-]'].array[0]
        p4_cop = parameters['p4_COP [-]'].array[0]
        if (p1_cop * t_in + p2_cop * t_out + p3_cop + p4_cop * t_amb_fix)<=1.0:
            raise ValueError('COP too low! Increase t_in or decrease t_out.')
        if group_id == 1 or group_id == 4:
            t_in_fix = t_in_hp[0]
        if group_id == 2 or group_id == 5:
            t_in_fix = t_in_hp[1]
        if group_id == 3 or group_id == 6:
            t_in_fix = t_in_hp[2]    
        cop_ref = p1_cop * t_in_fix + p2_cop * t_out_fix + p3_cop + p4_cop * t_amb_fix
        p_el_ref = p_th_ref / cop_ref
        parameters.loc[:, 'P_el_ref [W]'] = p_el_ref
        parameters.loc[:, 'COP_ref'] = cop_ref
    return parameters


def get_parameters_fit(model: str, group_id: int = 0, p_th: int = 0) -> pd.DataFrame:
    """
    Helper function for leastsquare fit of thermal output power at reference set point.

    Parameters
    ----------
    model : str
        Name of the heat pump model.
    group_id : numeric, default 0
        Group ID for a parameter set which represents an average heat pump of its group.
    p_th : numeric, default 0
        Thermal output power. [W]

    Returns
    -------
    parameters : pd.DataFrame
        Data frame containing the model parameters.
    """
    df = pd.read_csv('hplib_database.csv', delimiter=',')
    df = df.loc[df['Model'] == model]
    parameters = pd.DataFrame()

    parameters['Model'] = (df['Model'].values.tolist())
    parameters['P_th_ref [W]'] = (df['P_th_ref [W]'].values.tolist())
    parameters['P_el_ref [W]'] = (df['P_el_ref [W]'].values.tolist())
    parameters['COP_ref'] = (df['COP_ref'].values.tolist())
    parameters['Group'] = (df['Group'].values.tolist())
    parameters['p1_P_th [1/°C]'] = (df['p1_P_th [1/°C]'].values.tolist())
    parameters['p2_P_th [1/°C]'] = (df['p2_P_th [1/°C]'].values.tolist())
    parameters['p3_P_th [-]'] = (df['p3_P_th [-]'].values.tolist())
    parameters['p4_P_th [1/°C]'] = (df['p4_P_th [1/°C]'].values.tolist())
    parameters['p1_P_el [1/°C]'] = (df['p1_P_el [1/°C]'].values.tolist())
    parameters['p2_P_el [1/°C]'] = (df['p2_P_el [1/°C]'].values.tolist())
    parameters['p3_P_el [-]'] = (df['p3_P_el [-]'].values.tolist())
    parameters['p4_P_el [1/°C]'] = (df['p4_P_el [1/°C]'].values.tolist())
    parameters['p1_COP [-]'] = (df['p1_COP [-]'].values.tolist())
    parameters['p2_COP [-]'] = (df['p2_COP [-]'].values.tolist())
    parameters['p3_COP [-]'] = (df['p3_COP [-]'].values.tolist())
    parameters['p4_COP [-]'] = (df['p4_COP [-]'].values.tolist())
    
    if model == 'Generic':
        parameters = parameters.iloc[group_id - 1:group_id]
        parameters.loc[:, 'P_th_ref [W]'] = p_th
        t_in_hp = [-7,0,10] # air/water, brine/water, water/water
        t_out_fix = 52
        t_amb_fix = -7
        p1_cop = parameters['p1_COP [-]'].array[0]
        p2_cop = parameters['p2_COP [-]'].array[0]
        p3_cop = parameters['p3_COP [-]'].array[0]
        p4_cop = parameters['p4_COP [-]'].array[0]
        if group_id == 1 or group_id == 4:
            t_in_fix = t_in_hp[0]
        if group_id == 2 or group_id == 5:
            t_in_fix = t_in_hp[1]
        if group_id == 3 or group_id == 6:
            t_in_fix = t_in_hp[2]  
        cop_ref = p1_cop * t_in_fix + p2_cop * t_out_fix + p3_cop + p4_cop * t_amb_fix
        p_el_ref = p_th / cop_ref
        parameters.loc[:, 'P_el_ref [W]'] = p_el_ref
        parameters.loc[:, 'COP_ref'] = cop_ref
    return parameters


def fit_p_th_ref(t_in: int, t_out: int, group_id: int, p_th_set_point: int) -> Any:
    """
    Determine the thermal output power in [W] at reference conditions (T_in = [-7, 0, 10] , 
    T_out=52, T_amb=-7) for a given set point for a generic heat pump, using a least-square method.

    Parameters
    ----------
    t_in : numeric
        Input temperature :math:`T` at primary side of the heat pump. [°C]
    t_out : numeric
        Output temperature :math:`T` at secondary side of the heat pump. [°C]
    group_id : numeric
        Group ID for a parameter set which represents an average heat pump of its group.
    p_th_set_point : numeric
        Thermal output power. [W]

    Returns
    -------
    p_th : Any
        Thermal output power. [W]
    """
    P_0 = [1000]  # starting values
    a = (t_in, t_out, group_id, p_th_set_point)
    p_th, _ = scipy.optimize.leastsq(fit_func_p_th_ref, P_0, args=a)
    return p_th


def fit_func_p_th_ref(p_th:  int, t_in: int, t_out: int, group_id: int, p_th_set_point: int) -> int:
    """
    Helper function to determine difference between given and calculated 
    thermal output power in [W].

    Parameters
    ----------
    p_th : numeric
        Thermal output power. [W]
    t_in : numeric
        Input temperature :math:`T` at primary side of the heat pump. [°C]
    t_out : numeric
        Output temperature :math:`T` at secondary side of the heat pump. [°C]
    group_id : numeric
        Group ID for a parameter set which represents an average heat pump of its group.
    p_th_set_point : numeric
        Thermal output power. [W]

    Returns
    -------
    p_th_diff : numeric
        Thermal output power. [W]
    """
    if group_id == 1 or group_id == 4:
        t_amb = t_in
    else:
        t_amb = -7
    parameters = get_parameters_fit(model='Generic', group_id=group_id, p_th=p_th)
    p_th_calc, _, _, _, _ = simulate(t_in, t_out - 5, parameters, t_amb)
    p_th_diff = p_th_calc - p_th_set_point
    return p_th_diff


def simulate(t_in_primary: int, t_in_secondary: int, parameters: pd.DataFrame,
             t_amb: int) -> Tuple[int, int, int, int, int]:
    """
    Performs the simulation of the heat pump model.

    Parameters
    ----------
    t_in_primary : numeric
        Input temperature on primry side :math:`T` (air, brine, water). [°C]
    t_in_secondary : numeric
        Input temperature on secondary side :math:`T` from heating storage or system. [°C]
    parameters : pd.DataFrame
        Data frame containing the heat pump parameters.
    t_amb : numeric, default 0
        Ambient temperature :math:'T' of the air. [°C]

    Returns
    -------
    p_th :  numeric
        Thermal output power. [W]
    p_el : numeric
        Electrical input Power. [W]
    cop : numeric
        Coefficient of performance.
    t_out : numeric
        Output temperature :math:`T` at secondary side of the heat pump. [°C]
    m_dot : numeric
        Mass flow at secondary side of the heat pump. [kg/s]
    """

    DELTA_T = 5  # Inlet temperature is supposed to be heated up by 5 K
    CP = 4200  # J/(kg*K), specific heat capacity of water

    t_in = t_in_primary
    t_out = t_in_secondary + DELTA_T
    group_id = parameters['Group'].array[0]
    p1_p_el = parameters['p1_P_el [1/°C]'].array[0]
    p2_p_el = parameters['p2_P_el [1/°C]'].array[0]
    p3_p_el = parameters['p3_P_el [-]'].array[0]
    p4_p_el = parameters['p4_P_el [1/°C]'].array[0]
    p1_cop = parameters['p1_COP [-]'].array[0]
    p2_cop = parameters['p2_COP [-]'].array[0]
    p3_cop = parameters['p3_COP [-]'].array[0]
    p4_cop = parameters['p4_COP [-]'].array[0]
    p_el_ref = parameters['P_el_ref [W]'].array[0]
    p_th_ref = parameters['P_th_ref [W]'].array[0]

    # for subtype = air/water heat pump
    if group_id == 1 or group_id == 4:
        t_amb = t_in
    else:
        pass
    
    # for regulated heat pumps
    if group_id == 1 or group_id == 2 or group_id == 3:
        cop = p1_cop * t_in + p2_cop * t_out + p3_cop + p4_cop * t_amb
        p_el = (p1_p_el * t_in + p2_p_el * t_out + p3_p_el + p4_p_el * t_amb) * p_el_ref
        if group_id == 1:
            t_in = -7
            t_amb = t_in
        if group_id == 2:
            t_amb = -7
        
        if p_el < 0.25 * p_el_ref * (p1_p_el * t_in + p2_p_el * t_out + p3_p_el + p4_p_el * t_amb):  # 25% of Pel @ -7°C T_amb = T_in
            p_el = 0.25 * p_el_ref * (p1_p_el * t_in + p2_p_el * t_out + p3_p_el + p4_p_el * t_amb)
        p_th = p_el * cop
        if cop <= 1:
            cop = 1
            p_el = p_th_ref
            p_th = p_th_ref
    # for subtype = On-Off
    elif group_id == 4 or group_id == 5 or group_id == 6:
        p_el = (p1_p_el * t_in + p2_p_el * t_out + p3_p_el + p4_p_el * t_amb) * p_el_ref
        cop = p1_cop * t_in + p2_cop * t_out + p3_cop + p4_cop * t_amb
        p_th = p_el * cop
        if cop <= 1:
            cop = 1
            p_el = p_th_ref
            p_th = p_th_ref
    # massflow
    m_dot = p_th / (DELTA_T * CP)

    return p_th, p_el, cop, t_out, m_dot
