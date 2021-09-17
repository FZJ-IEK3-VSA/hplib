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
        Name of the heat pump model.
    group_id : numeric, default 0
        Group ID for a parameter set which represents an average heat pump of its group.
    t_in : numeric, default 0
        Input temperature :math:`T` at primary side of the heat pump. [°C]
    t_out : numeric, default 0
        Output temperature :math:`T` at secondary side of the heat pump. [°C]
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
        parameters.loc[:, 'P_th_ref [W]'] = fit_p_th_ref(t_in, t_out, group_id, p_th)
        x = -7
        y = 52
        p1_p_el = parameters['p1_P_el [1/°C]'].array[0]
        p2_p_el = parameters['p2_P_el [1/°C]'].array[0]
        p3_p_el = parameters['p3_P_el [-]'].array[0]
        p1_cop = parameters['p1_COP [-]'].array[0]
        p2_cop = parameters['p2_COP [-]'].array[0]
        p3_cop = parameters['p3_COP [-]'].array[0]
        p4_cop = parameters['p4_COP [-]'].array[0]
        cop_ref = p1_cop * x + p2_cop * y + p3_cop + p4_cop * x
        p_el_ref = fit_p_th_ref(t_in, t_out, group_id, p_th) / cop_ref
        parameters.loc[:, 'P_el_ref [W]'] = p_el_ref
        parameters.loc[:, 'COP_ref'] = cop_ref
    return parameters


def get_parameters_fit(model: str, group_id: int = 0, p_th: int = 0) -> pd.DataFrame:
    """
    Loads the content of the database for a specific heat pump model
    and returns a pandas ``DataFrame`` containing the heat pump parameters.

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
        x = -7
        y = 52
        p1_p_el = parameters['p1_P_el [1/°C]'].array[0]
        p2_p_el = parameters['p2_P_el [1/°C]'].array[0]
        p3_p_el = parameters['p3_P_el [-]'].array[0]
        p1_cop = parameters['p1_COP [-]'].array[0]
        p2_cop = parameters['p2_COP [-]'].array[0]
        p3_cop = parameters['p3_COP [-]'].array[0]
        p4_cop = parameters['p4_COP [-]'].array[0]
        cop_ref = p1_cop * x + p2_cop * y + p3_cop + p4_cop * x
        p_el_ref = p_th / cop_ref
        parameters.loc[:, 'P_el_ref [W]'] = p_el_ref
        parameters.loc[:, 'COP_ref'] = cop_ref
    return parameters


def fit_p_th_ref(t_in: int, t_out: int, group_id: int, p_th_ref: int) -> Any:
    """
    Determine the thermal output power in [W] using the optimization library ``scipy`` module to implement
    the least-square method to fit the curve data with a given function.
    The ``leastsq()`` function applies the least-square minimization to fit the data.

    Parameters
    ----------
    t_in : numeric
        Input temperature :math:`T` at primary side of the heat pump. [°C]
    t_out : numeric
        Output temperature :math:`T` at secondary side of the heat pump. [°C]
    group_id : numeric
        Group ID for a parameter set which represents an average heat pump of its group.
    p_th_ref : numeric
        Thermal output power. [W]

    Returns
    -------
    p_th : Any
        Thermal output power. [W]
    """
    p0 = [1000]  # starting values
    a = (t_in, t_out, group_id, p_th_ref)
    p_th, _ = scipy.optimize.leastsq(fit_func_p_th_ref, p0, args=a)
    return p_th


def fit_func_p_th_ref(p_th:  int, t_in: int, t_out: int, group_id: int, p_th_ref: int) -> int:
    """
    Determine the thermal output power in [W] using the optimization library ``scipy`` module to implement
    the least-square method to fit the curve data with a given function.
    The ``leastsq()`` function applies the least-square minimization to fit the data.

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
    p_th_ref : numeric
        Thermal output power. [W]

    Returns
    -------
    p_th_diff : numeric
        Thermal output power. [W]
    """
    parameters = get_parameters_fit(model='Generic', group_id=group_id, p_th=p_th)
    p_th_calc, _, _, _, _ = simulate(t_in, t_out - 5, parameters, t_in)
    p_th_diff = p_th_calc - p_th_ref
    return p_th_diff


def simulate(t_in_primary: int, t_in_secondary: int, parameters: pd.DataFrame,
             t_amb: int = 0) -> Tuple[int, int, int, int, int]:
    """
    Determine the thermal output power in [W] using the optimization library ``scipy`` module to implement
    the least-square method to fit the curve data with a given function.
    The ``leastsq()`` function applies the least-square minimization to fit the data.

    Parameters
    ----------
    t_in_primary : numeric
        Source temperature :math:`T` (air or ground). [°C]
    t_in_secondary : numeric
        Source temperature :math:`T` from heating storage or system. [°C]
    parameters : pd.DataFrame
        Data frame containng the heat pump parameters.
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
        Mass flow. [kg/s]
    """

    DELTA_T = 5  # Inlet temperature is supposed to be heated up by 5 K
    CP = 4200  # J/(kg*K), specific heat capacity of water

    t_in = t_in_primary
    t_out = t_in_secondary + DELTA_T
    model = parameters['Model'].array[0]
    group_id = parameters['Group'].array[0]
    p1_p_th = parameters['p1_P_th [1/°C]'].array[0]
    p2_p_th = parameters['p2_P_th [1/°C]'].array[0]
    p3_p_th = parameters['p3_P_th [-]'].array[0]
    p4_p_th = parameters['p4_P_th [1/°C]'].array[0]
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
    # for subtype = Inverter
    if group_id == 1 or group_id == 4:
        t_amb = t_in
    else:
        pass

    if group_id == 1 or group_id == 2 or group_id == 3:
        cop = p1_cop * t_in + p2_cop * t_out + p3_cop + p4_cop * t_amb
        p_el = (p1_p_el * t_in + p2_p_el * t_out + p3_p_el + p4_p_el * t_amb) * p_el_ref
        if group_id == 1:
            t_in = -7
            t_amb = t_in
        if group_id == 2:
            t_amb = -7
        if p_el < 0.25 * p_el_ref * (
                p1_p_el * t_in + p2_p_el * t_out + p3_p_el + p4_p_el * t_amb):  # 25% of Pel @ -7°C T_amb = T_in
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
    # for subtype = Two-stages
    else:
        p_el = 0
        cop = 0
        p_th = 0
        if cop <= 1:
            cop = 1
            p_el = p_th_ref
            p_th = p_th_ref
    # massflow
    m_dot = p_th / (DELTA_T * CP)

    return p_th, p_el, cop, t_out, m_dot
