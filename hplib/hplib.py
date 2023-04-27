"""
The ``hplib`` module provides a set of functions for simulating the performance of heat pumps.
"""
import string
import pandas as pd
import scipy
from scipy.optimize import curve_fit
from typing import Any, Dict, Union
import os
import numpy as np


def load_database() -> pd.DataFrame:
    """
    Loads data from hplib_database.

    Returns
    -------
    df : pd.DataFrame
        Content of the database
    """
    df = pd.read_csv(cwd()+r'/hplib_database.csv')
    return df


def load_all_heat_pumps() -> pd.DataFrame:
    """
    Loads data from all heat pumps for heating.

    Returns
    -------
    df : pd.DataFrame
        Content of the database
    """
    df = pd.read_csv(cwd()+r'/hplib_database_all.csv')
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
        only for model "Generic": Thermal output power at setpoint t_in, t_out (and for 
        water/water, brine/water heat pumps t_amb = -7°C). [W]

    Returns
    -------
    df : pd.DataFrame
        Data frame containing the model parameters.
    """
    df = pd.read_csv(cwd()+r'/hplib_database.csv', delimiter=',')
    if model=='Generic':
        model='Generic_average'
    df = df.loc[df['Titel'] == model]
    if model.startswith('Generic'):
        df = df.loc[df['Group']==group_id]
        p_th_ref = fit_p_th_ref(t_in, t_out, group_id, p_th, model)
        df.loc[:, 'P_th_h_ref [W]'] = p_th_ref
        t_in_hp = [-7,0,10] # air/water, brine/water, water/water
        t_out_fix = 52
        t_amb_fix = -7
        p1_cop = df['p1_COP [-]'].array[0]
        p2_cop = df['p2_COP [-]'].array[0]
        p3_cop = df['p3_COP [-]'].array[0]
        p4_cop = df['p4_COP [-]'].array[0]
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
        df.loc[:, 'P_el_h_ref [W]'] = p_el_ref
        df.loc[:, 'COP_ref'] = cop_ref
        if group_id==1:
            try:
                p1_eer = df['p1_EER [-]'].array[0]
                p2_eer = df['p2_EER [-]'].array[0]
                p3_eer = df['p3_EER [-]'].array[0]
                p4_eer = df['p4_EER [-]'].array[0]
                eer_ref = p1_eer * 35 + p2_eer * 7 + p3_eer + p4_eer * 35
                df.loc[:,'P_th_c_ref [W]'] = p_el_ref * 0.6852 * eer_ref
                df['P_el_c_ref [W]'] = p_el_ref * 0.6852 #average value from real Heatpumps (P_el35/7 to P_el-7/52) 
                df.loc[:, 'EER_ref'] = eer_ref        
            except:
                pass
    return df


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
    df = pd.read_csv(cwd()+r'/hplib_database.csv', delimiter=',')
    df = df.loc[df['Titel'] == model]
    
    if model.startswith('Generic'):
        df = df.loc[df['Group']==group_id]
        df.loc[:, 'P_th_h_ref [W]'] = p_th
        t_in_hp = [-7,0,10] # air/water, brine/water, water/water
        t_out_fix = 52
        t_amb_fix = -7
        p1_cop = df['p1_COP [-]'].array[0]
        p2_cop = df['p2_COP [-]'].array[0]
        p3_cop = df['p3_COP [-]'].array[0]
        p4_cop = df['p4_COP [-]'].array[0]
        if group_id == 1 or group_id == 4:
            t_in_fix = t_in_hp[0]
        if group_id == 2 or group_id == 5:
            t_in_fix = t_in_hp[1]
        if group_id == 3 or group_id == 6:
            t_in_fix = t_in_hp[2]  
        cop_ref = p1_cop * t_in_fix + p2_cop * t_out_fix + p3_cop + p4_cop * t_amb_fix
        p_el_ref = p_th / cop_ref
        df.loc[:, 'P_el_h_ref [W]'] = p_el_ref
        df.loc[:, 'COP_ref'] = cop_ref
    return df


def fit_p_th_ref(t_in: int, t_out: int, group_id: int, p_th_set_point: int, model: str) -> Any:
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
    model : str
        define wich generic heatpump [one of 'Generic_top', 'Generic_average' or 'Generic_bottom'].

    Returns
    -------
    p_th : Any
        Thermal output power. [W]
    """
    P_0 = [1000]  # starting values
    a = (t_in, t_out, group_id, p_th_set_point, model)
    p_th, _ = scipy.optimize.leastsq(fit_func_p_th_ref, P_0, args=a)
    return p_th


def fit_func_p_th_ref(p_th:  int, t_in: int, t_out: int, group_id: int, p_th_set_point: int, model: str) -> int:
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
    model : str
        define wich generic heatpump [one of 'Generic_top', 'Generic_average' or 'Generic_bottom'].

    Returns
    -------
    p_th_diff : numeric
        Thermal output power. [W]
    """
    if group_id == 1 or group_id == 4:
        t_amb = t_in
    else:
        t_amb = -7
    parameters = get_parameters_fit(model = model, group_id = group_id, p_th = p_th)
    df = simulate(t_in, t_out - 5, parameters, t_amb)
    p_th_calc=df.P_th.values[0]
    p_th_diff = p_th_calc - p_th_set_point
    return p_th_diff


def simulate(t_in_primary: Union[float,np.ndarray], t_in_secondary: Union[float,np.ndarray], parameters, t_amb: Union[float,np.ndarray], mode: int = 1, p_th_min: Union[float,np.ndarray] = 0) -> dict:
    """
    Performs the simulation of the heat pump model.

    Parameters
    ----------
    t_in_primary : numeric or iterable (e.g. pd.Series)
        Input temperature on primry side :math:`T` (air, brine, water). [°C]
    t_in_secondary : numeric or iterable (e.g. pd.Series)
        Input temperature on secondary side :math:`T` from heating storage or system. [°C]
    parameters : pd.DataFrame
        Data frame containing the heat pump parameters from hplib.getParameters().
    t_amb : numeric or iterable (e.g. pd.Series)
        Ambient temperature :math:'T' of the air. [°C]
    mode : int
        for heating: 1, for cooling: 2
    P_th_min : Minimum thermal power output [W]. Inverter heat pumps increase electrical Power input. At maximum electrical input a electrical heating rod turns on.

    Returns
    -------
    df : pd.DataFrame
        with the following columns
        T_in = Input temperature :math:`T` at primary side of the heat pump. [°C]
        T_out = Output temperature :math:`T` at secondary side of the heat pump. [°C]
        T_amb = Ambient / Outdoor temperature :math:`T`. [°C]
        COP = Coefficient of Performance.
        EER = Energy Efficiency Ratio.
        P_el = Electrical input Power. [W]
        P_th = Thermal output power. [W]
        m_dot = Mass flow at secondary side of the heat pump. [kg/s]    
    """

    delta_t = 5  # Inlet temperature is supposed to be heated up by 5 K
    cp = 4200  # J/(kg*K), specific heat capacity of water
    group_id = parameters['Group'].array[0]
    p1_p_el_h = parameters['p1_P_el_h [1/°C]'].array[0]
    p2_p_el_h = parameters['p2_P_el_h [1/°C]'].array[0]
    p3_p_el_h = parameters['p3_P_el_h [-]'].array[0]
    p4_p_el_h = parameters['p4_P_el_h [1/°C]'].array[0]
    p1_cop = parameters['p1_COP [-]'].array[0]
    p2_cop = parameters['p2_COP [-]'].array[0]
    p3_cop = parameters['p3_COP [-]'].array[0]
    p4_cop = parameters['p4_COP [-]'].array[0]
    p_el_ref = parameters['P_el_h_ref [W]'].array[0]
    p_th_ref = parameters['P_th_h_ref [W]'].array[0]
    try:
        p1_eer = parameters['p1_EER [-]'].array[0]
        p2_eer = parameters['p2_EER [-]'].array[0]
        p3_eer = parameters['p3_EER [-]'].array[0]
        p4_eer = parameters['p4_EER [-]'].array[0]
        p1_p_el_c = parameters['p1_P_el_c [1/°C]'].array[0]
        p2_p_el_c = parameters['p2_P_el_c [1/°C]'].array[0]
        p3_p_el_c = parameters['p3_P_el_c [-]'].array[0]
        p4_p_el_c = parameters['p4_P_el_c [1/°C]'].array[0]
        p_el_col_ref=parameters['P_el_c_ref [W]'].array[0]
    except:
        p1_eer = np.nan
        p2_eer = np.nan
        p3_eer = np.nan
        p4_eer = np.nan
        p1_p_el_c = np.nan
        p2_p_el_c = np.nan
        p3_p_el_c = np.nan
        p4_p_el_c = np.nan
        p_el_col_ref=np.nan

    if mode==2 and group_id > 1:
        raise ValueError('Cooling is only possible with heat pumps of group id = 1.')
    
    t_in = t_in_primary  # info value for dataframe
    if mode==1:
        t_out = t_in_secondary + delta_t #Inlet temperature is supposed to be heated up by 5 K
        eer=0
    if mode==2: # Inlet temperature is supposed to be cooled down by 5 K
        t_out = t_in_secondary - delta_t
        cop=0
    # for subtype = air/water heat pump
    if group_id in (1, 4):
        t_amb = t_in
    t_ambient=t_amb
    # for regulated heat pumps
    if group_id in (1, 2, 3):
        if mode==1:
            cop = p1_cop * t_in + p2_cop * t_out + p3_cop + p4_cop * t_amb
            p_el=p_el_ref * (p1_p_el_h * t_in
                                + p2_p_el_h * t_out
                                + p3_p_el_h
                                + p4_p_el_h * t_amb)
            if group_id == 1:
                if isinstance(t_in, np.ndarray):
                    t_in = np.full_like(t_in, -7)
                else:
                    t_in = -7
                t_amb = t_in

            elif group_id == 2:
                if isinstance(t_amb, np.ndarray):
                    t_amb = np.full_like(t_amb, -7)
                else:
                    t_amb = -7
            p_el_25 = 0.25 * p_el_ref * (p1_p_el_h * t_in
                                            + p2_p_el_h * t_out
                                            + p3_p_el_h
                                            + p4_p_el_h * t_amb)
            if isinstance(p_el, np.ndarray):
                p_el = np.where(p_el < p_el_25, p_el_25, p_el)
            elif p_el < p_el_25:
                p_el = p_el_25

            p_th = p_el * cop

            if isinstance(cop, np.ndarray):
                # turn on heating rod and compressor
                p_el=np.where((cop>1) & (p_th < p_th_min) & (p_el_ref < p_th_min/cop), p_el_ref + p_th_ref, p_el)
                p_th=np.where((cop>1) & (p_th < p_th_min) & (p_el_ref < p_th_min/cop), p_el_ref * cop + p_th_ref, p_th)
                # increase electrical power for compressor
                p_el=np.where((cop>1) & (p_th < p_th_min) & (p_el_ref > p_th_min/cop), p_th_min/cop, p_el)
                p_th=np.where((cop>1) & (p_th < p_th_min) & (p_el_ref > p_th_min/cop), p_th_min, p_th)
                # only turn on heating rod
                p_el = np.where(cop <= 1, p_th_ref, p_el)
                p_th = np.where(cop <= 1, p_th_ref, p_th)
                cop = p_th/p_el
            else:
                if cop <= 1:
                    cop = 1
                    p_el = p_th_ref
                    p_th = p_th_ref
                elif p_th < p_th_min:
                    if p_el_ref > p_th_min/cop:
                        p_el = p_th_min/cop
                        p_th = p_th_min
                    else:
                        p_el = p_el_ref + p_th_ref
                        p_th = p_el_ref*cop + p_th_ref
                        cop = p_th/p_el                            
                
        if mode==2:
            eer = (p1_eer * t_in + p2_eer * t_out + p3_eer + p4_eer * t_amb)
            if isinstance(t_in, np.ndarray):
                t_in=np.where(t_in<25,25,t_in)
            elif t_in<25:
                t_in=25
            t_amb=t_in
            p_el = (p1_p_el_c * t_in + p2_p_el_c * t_out + p3_p_el_c + p4_p_el_c * t_amb) * p_el_col_ref
            if isinstance(p_el,np.ndarray):
                eer = np.where(p_el<0,0,eer)
                p_el = np.where(p_el<0,0,p_el)
            elif p_el<0:
                eer = 0
                p_el = 0
            p_th = -(eer*p_el)
            if isinstance(eer,np.ndarray):
                p_el = np.where(eer <= 1, 0 , p_el)
                p_th = np.where(eer <= 1, 0 , p_th)
                eer = np.where(eer <= 1, 0, eer)
            elif eer < 1:
                eer = 0
                p_el = 0
                p_th = 0

    # for subtype = On-Off
    elif group_id in (4, 5, 6):
        p_el = (p1_p_el_h * t_in
                + p2_p_el_h * t_out
                + p3_p_el_h
                + p4_p_el_h * t_amb) * p_el_ref

        cop = p1_cop * t_in + p2_cop * t_out + p3_cop + p4_cop * t_amb

        p_th = p_el * cop

        if isinstance(cop, np.ndarray):
            p_el=np.where((cop>1) & (p_th < p_th_min) , p_el + p_th_ref, p_el)
            p_th=np.where((cop>1) & (p_th < p_th_min) , p_th + p_th_ref, p_th)
            p_el = np.where(cop <= 1, p_th_ref, p_el)
            p_th = np.where(cop <= 1, p_th_ref, p_th)
            cop = p_th / p_el

        else:
            if cop <= 1:
                cop = 1
                p_el = p_th_ref
                p_th = p_th_ref
            elif p_th < p_th_min:
                p_th=p_th+p_th_ref
                p_el=p_el+p_th_ref
                cop=p_th/p_el

    # massflow
    m_dot = abs(p_th / (delta_t * cp))
    
    # round
    result = pd.DataFrame()

    result['T_in'] = [t_in_primary]
    result['T_out'] = [t_out]
    result['T_amb'] = [t_ambient]
    result['COP'] = [cop]
    result['EER'] = [eer]
    result['P_el'] = [p_el]
    result['P_th'] = [p_th]
    result['m_dot']= [m_dot]
    return result


def cwd():
    """
    Returns parent directory.
    """
    real_path = os.path.realpath(__file__)
    dir_path = os.path.dirname(real_path)
    return dir_path


class HeatPump:
    def __init__(self, parameters: pd.DataFrame):
        self.group_id = float(parameters['Group'].array[0])
        self.p1_p_el_h = float(parameters['p1_P_el_h [1/°C]'].array[0])
        self.p2_p_el_h = float(parameters['p2_P_el_h [1/°C]'].array[0])
        self.p3_p_el_h = float(parameters['p3_P_el_h [-]'].array[0])
        self.p4_p_el_h = float(parameters['p4_P_el_h [1/°C]'].array[0])
        self.p1_cop = float(parameters['p1_COP [-]'].array[0])
        self.p2_cop = float(parameters['p2_COP [-]'].array[0])
        self.p3_cop = float(parameters['p3_COP [-]'].array[0])
        self.p4_cop = float(parameters['p4_COP [-]'].array[0])
        self.p_el_ref = float(parameters['P_el_h_ref [W]'].array[0])
        self.p_th_ref = float(parameters['P_th_h_ref [W]'].array[0])
        try:
            self.p1_eer = parameters['p1_EER [-]'].array[0]
            self.p2_eer = parameters['p2_EER [-]'].array[0]
            self.p3_eer = parameters['p3_EER [-]'].array[0]
            self.p4_eer = parameters['p4_EER [-]'].array[0]
            self.p1_p_el_c = parameters['p1_P_el_c [1/°C]'].array[0]
            self.p2_p_el_c = parameters['p2_P_el_c [1/°C]'].array[0]
            self.p3_p_el_c = parameters['p3_P_el_c [-]'].array[0]
            self.p4_p_el_c = parameters['p4_P_el_c [1/°C]'].array[0]
            self.p_el_col_ref=parameters['P_el_c_ref [W]'].array[0]
        except:
            self.p1_eer = np.nan
            self.p2_eer = np.nan
            self.p3_eer = np.nan
            self.p4_eer = np.nan
            self.p1_p_el_c = np.nan
            self.p2_p_el_c = np.nan
            self.p3_p_el_c = np.nan
            self.p4_p_el_c = np.nan
            self.p_el_col_ref=np.nan

        self.delta_t = 5  # Inlet temperature is supposed to be heated up by 5 K
        self.cp = 4200  # J/(kg*K), specific heat capacity of water

    def simulate(self, t_in_primary: Union[float,np.ndarray], t_in_secondary: Union[float,np.ndarray], t_amb: Union[float,np.ndarray], mode: int = 1, p_th_min: Union[float,np.ndarray] = 0) -> dict:
        """
        Performs the simulation of the heat pump model.

        Parameters
        ----------
        t_in_primary : numeric or iterable (e.g. pd.Series)
            Input temperature on primry side :math:`T` (air, brine, water). [°C]
        t_in_secondary : numeric or iterable (e.g. pd.Series)
            Input temperature on secondary side :math:`T` from heating storage or system. [°C]
        parameters : pd.DataFrame
            Data frame containing the heat pump parameters from hplib.getParameters().
        t_amb : numeric or iterable (e.g. pd.Series)
            Ambient temperature :math:'T' of the air. [°C]
        mode : int
            for heating: 1, for cooling: 2
        P_th_min : Minimum thermal power output [W]. Inverter heat pumps increase electrical Power input. At maximum electrical input a electrical heating rod turns on.

        Returns
        -------
        result : dict
            with the following columns
            T_in = Input temperature :math:`T` at primary side of the heat pump. [°C]
            T_out = Output temperature :math:`T` at secondary side of the heat pump. [°C]
            T_amb = Ambient / Outdoor temperature :math:`T`. [°C]
            COP = Coefficient of Performance.
            EER = Energy Efficiency Ratio.
            P_el = Electrical input Power. [W]
            P_th = Thermal output power. [W]
            m_dot = Mass flow at secondary side of the heat pump. [kg/s]
        """

        if mode==2 and self.group_id > 1:
            raise ValueError('Cooling is only possible with heat pumps of group id = 1.')
        
        t_in = t_in_primary  # info value for dataframe
        if mode==1:
            t_out = t_in_secondary + self.delta_t #Inlet temperature is supposed to be heated up by 5 K
            eer=0
        if mode==2: # Inlet temperature is supposed to be cooled down by 5 K
            t_out = t_in_secondary - self.delta_t
            cop=0
        # for subtype = air/water heat pump
        if self.group_id in (1, 4):
            t_amb = t_in
        t_ambient=t_amb
        # for regulated heat pumps
        if self.group_id in (1, 2, 3):
            if mode==1:
                cop = self.p1_cop * t_in + self.p2_cop * t_out + self.p3_cop + self.p4_cop * t_amb
                p_el=self.p_el_ref * (self.p1_p_el_h * t_in
                                    + self.p2_p_el_h * t_out
                                    + self.p3_p_el_h
                                    + self.p4_p_el_h * t_amb)
                if self.group_id == 1:
                    if isinstance(t_in, np.ndarray):
                        t_in = np.full_like(t_in, -7)
                    else:
                        t_in = -7
                    t_amb = t_in

                elif self.group_id == 2:
                    if isinstance(t_amb, np.ndarray):
                        t_amb = np.full_like(t_amb, -7)
                    else:
                        t_amb = -7
                p_el_25 = 0.25 * self.p_el_ref * (self.p1_p_el_h * t_in
                                                + self.p2_p_el_h * t_out
                                                + self.p3_p_el_h
                                                + self.p4_p_el_h * t_amb)
                if isinstance(p_el, np.ndarray):
                    p_el = np.where(p_el < p_el_25, p_el_25, p_el)
                elif p_el < p_el_25:
                    p_el = p_el_25

                p_th = p_el * cop

                if isinstance(cop, np.ndarray):
                    # turn on heating rod and compressor
                    p_el=np.where((cop>1) & (p_th < p_th_min) & (self.p_el_ref < p_th_min/cop), self.p_el_ref + self.p_th_ref, p_el)
                    p_th=np.where((cop>1) & (p_th < p_th_min) & (self.p_el_ref < p_th_min/cop), self.p_el_ref * cop + self.p_th_ref, p_th)
                    # increase electrical power for compressor
                    p_el=np.where((cop>1) & (p_th < p_th_min) & (self.p_el_ref > p_th_min/cop), p_th_min/cop, p_el)
                    p_th=np.where((cop>1) & (p_th < p_th_min) & (self.p_el_ref > p_th_min/cop), p_th_min, p_th)
                    # only turn on heating rod
                    p_el = np.where(cop <= 1, self.p_th_ref, p_el)
                    p_th = np.where(cop <= 1, self.p_th_ref, p_th)
                    cop = p_th/p_el
                else:
                    if cop <= 1:
                        cop = 1
                        p_el = self.p_th_ref
                        p_th = self.p_th_ref
                    elif p_th < p_th_min:
                        if self.p_el_ref > p_th_min/cop:
                            p_el = p_th_min/cop
                            p_th = p_th_min
                        else:
                            p_el = self.p_el_ref + self.p_th_ref
                            p_th = self.p_el_ref*cop + self.p_th_ref
                            cop = p_th/p_el                            
                    
            if mode==2:
                eer = (self.p1_eer * t_in + self.p2_eer * t_out + self.p3_eer + self.p4_eer * t_amb)
                if isinstance(t_in, np.ndarray):
                    t_in=np.where(t_in<25,25,t_in)
                elif t_in<25:
                    t_in=25
                t_amb=t_in
                p_el = (self.p1_p_el_c * t_in + self.p2_p_el_c * t_out + self.p3_p_el_c + self.p4_p_el_c * t_amb) * self.p_el_col_ref
                if isinstance(p_el,np.ndarray):
                    eer = np.where(p_el<0,0,eer)
                    p_el = np.where(p_el<0,0,p_el)
                elif p_el<0:
                    eer = 0
                    p_el = 0
                p_th = -(eer*p_el)
                if isinstance(eer,np.ndarray):
                    p_el = np.where(eer <= 1, 0 , p_el)
                    p_th = np.where(eer <= 1, 0 , p_th)
                    eer = np.where(eer <= 1, 0, eer)
                elif eer < 1:
                    eer = 0
                    p_el = 0
                    p_th = 0

        # for subtype = On-Off
        elif self.group_id in (4, 5, 6):
            p_el = (self.p1_p_el_h * t_in
                    + self.p2_p_el_h * t_out
                    + self.p3_p_el_h
                    + self.p4_p_el_h * t_amb) * self.p_el_ref

            cop = self.p1_cop * t_in + self.p2_cop * t_out + self.p3_cop + self.p4_cop * t_amb

            p_th = p_el * cop

            if isinstance(cop, np.ndarray):
                p_el=np.where((cop>1) & (p_th < p_th_min) , p_el + self.p_th_ref, p_el)
                p_th=np.where((cop>1) & (p_th < p_th_min) , p_th + self.p_th_ref, p_th)
                p_el = np.where(cop <= 1, self.p_th_ref, p_el)
                p_th = np.where(cop <= 1, self.p_th_ref, p_th)
                cop = p_th / p_el

            else:
                if cop <= 1:
                    cop = 1
                    p_el = self.p_th_ref
                    p_th = self.p_th_ref
                elif p_th < p_th_min:
                    p_th=p_th+self.p_th_ref
                    p_el=p_el+self.p_th_ref
                    cop=p_th/p_el

        # massflow
        m_dot = abs(p_th / (self.delta_t * self.cp))
        
        # round
        result = dict()

        result['T_in'] = t_in_primary
        result['T_out'] = t_out
        result['T_amb'] = t_ambient
        result['COP'] = cop
        result['EER'] = eer
        result['P_el'] = p_el
        result['P_th'] = p_th
        result['m_dot']= m_dot

        return result


class HeatingSystem:
    def __init__(self, t_outside_min: float = -15.0,
                t_inside_set: float = 20.0,
                t_hs_set: list = [35,28],
                f_hs_size: float = 1.0,
                f_hs_exp: float = 1.1):
        """
        Init function to set several input parameters for functions regarding the heating system.

        Parameters:
        ----------
        t_outside_min : minimal reference outside temperatur for building.
        t_inside_set : set room temperatur for building.
        t_hf_set : list with maximum heating flow and return temperature in °C
                [35,28] for floor heating
                [55,45] for low temperatur radiator
                [70,55] for radtiator
        f_hs_size : factor of oversizing of heat distribution system
        f_hs_exp : exponent factor of heating distribution system, e.g. 1.1 floor heating and 1.3 radiator
        """

        self.t_outside_min = t_outside_min
        self.t_inside_set = t_inside_set
        self.t_hf_max = t_hs_set[0]
        self.t_hf_min = t_inside_set
        self.t_hr_max = t_hs_set[1]
        self.t_hr_min = t_inside_set
        self.f_hs_size = f_hs_size
        self.f_hs_exp = f_hs_exp


    def calc_brine_temp(self, t_avg_d: float):
        """
        Calculate the soil temperature by the average Temperature of the day. 
        Source: „WP Monitor“ Feldmessung von Wärmepumpenanlagen S. 115, Frauenhofer ISE, 2014
        added 9 points at -15°C average day at 3°C soil temperature in order to prevent higher temperature of soil below -10°C.

        Parameters
        ----------
        t_avg_d : the average temperature of the day.

        Returns:
        ----------
        t_brine : the temperature of the soil/ Brine inflow temperature
        """
        
        t_brine = -0.0003*t_avg_d**3 + 0.0086*t_avg_d**2 + 0.3047*t_avg_d + 5.0647
        
        return t_brine

    def calc_heating_dist_temp(self, t_avg_d: float):
        """
        Calculate the heat distribution flow and return temperature 
        as a function of the moving average daily mean outside temperature.
        Calculations are bsed on DIN V 4701-10, Section 5

        Parameters
        ----------
        self : parameters from __init__

        Returns:
        ----------
        t_dist : list with heating flow and heating return temperature
        """
        
        if t_avg_d > self.t_inside_set:
            t_hf = self.t_hf_min
            t_hr = self.t_hr_min
        else:
            t_hf = self.t_hf_min + ((1/self.f_hs_size) * ((self.t_inside_set-t_avg_d)/(self.t_inside_set-self.t_outside_min)))**(1/self.f_hs_exp) * (self.t_hf_max - self.t_hf_min)
            t_hr = self.t_hr_min + ((1/self.f_hs_size) * ((self.t_inside_set-t_avg_d)/(self.t_inside_set-self.t_outside_min)))**(1/self.f_hs_exp) * (self.t_hr_max - self.t_hr_min)
        
        t_dist = [t_hf, t_hr]
        
        return t_dist

class Same_Built:
    def __init__(self):
        """
        Init function to load Database.

        Parameters:
        ----------
        """
        self.all_hp=load_all_heat_pumps()
        self.df = pd.read_csv(cwd()+r'/hplib_database.csv', delimiter=',')
        self.same=pd.read_pickle(cwd()+r'/same_built_type.pkl')

    def all_to_database(self, modelname: string) -> str:
        """
        If the heatpump is in hplib/hplib_database_all.csv but not in hplib/hplib_database.csv use this function to find the heatpump with equivalent fitting parameters.

        Parameters
        ----------
        modelname : the modelname which is in the hplib_database_all.csv

        Returns
        ----------
        same_built : modelname of the model in hplib_database.csv
        """
        model=self.df.loc[self.df['p3_P_el_h [-]']==(self.all_hp.loc[self.all_hp['Model']==modelname,'p3_P_el_h [-]'][self.all_hp.loc[self.all_hp['Model']==modelname].index[0]]),'Model'].values[0]
        return model

    def database_to_all(self, modelname: string) -> list:
        """
        If the heatpump is in hplib/hplib_database.csv use this function to find the heatpumps with equivalent fitting parameters.
        Returns all models which have the same parameters. But different names.

        Parameters
        ----------
        modelname : the modelname which is in the hplib_database.csv

        Returns
        ----------
        same_built : list of all models with same fitting parameters
        """
        same_built=self.same[modelname]
        return (same_built)
