"""
The ``hplib`` module provides a set of functions for simulating the performance of heat pumps.
"""
import pandas as pd
import scipy
from scipy.optimize import curve_fit
from typing import Any, Tuple
import os
import numpy


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
    parameters : pd.DataFrame
        Data frame containing the model parameters.
    """
    df = pd.read_csv(cwd()+r'/hplib_database.csv', delimiter=',')
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
    parameters['P_th_h_ref [W]'] = (df['P_th_h_ref [W]'].values.tolist())
    parameters['P_el_h_ref [W]'] = (df['P_el_h_ref [W]'].values.tolist())
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
    try:
        parameters['P_th_c_ref [W]'] = (df['P_th_c_ref [W]'].values.tolist())
        parameters['P_el_c_ref [W]'] = (df['P_el_c_ref [W]'].values.tolist())
        parameters['p1_Pdc [1/°C]'] = (df['p1_Pdc [1/°C]'].values.tolist())
        parameters['p2_Pdc [1/°C]'] = (df['p2_Pdc [1/°C]'].values.tolist())
        parameters['p3_Pdc [-]'] = (df['p3_Pdc [-]'].values.tolist())
        parameters['p4_Pdc [1/°C]'] = (df['p4_Pdc [1/°C]'].values.tolist())
        parameters['p5_P_el [1/°C]'] = (df['p5_P_el [1/°C]'].values.tolist())
        parameters['p6_P_el [1/°C]'] = (df['p6_P_el [1/°C]'].values.tolist())
        parameters['p7_P_el [-]'] = (df['p7_P_el [-]'].values.tolist())
        parameters['p8_P_el [1/°C]'] = (df['p8_P_el [1/°C]'].values.tolist())
        parameters['p1_EER [-]'] = (df['p1_EER [-]'].values.tolist())
        parameters['p2_EER [-]'] = (df['p2_EER [-]'].values.tolist())
        parameters['p3_EER [-]'] = (df['p3_EER [-]'].values.tolist())
        parameters['p4_EER [-]'] = (df['p4_EER [-]'].values.tolist())
    except:
        pass

    if model == 'Generic':
        parameters = parameters.iloc[group_id - 1:group_id]
        
        p_th_ref = fit_p_th_ref(t_in, t_out, group_id, p_th)
        parameters.loc[:, 'P_th_h_ref [W]'] = p_th_ref
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
        parameters.loc[:, 'P_el_h_ref [W]'] = p_el_ref
        parameters.loc[:, 'COP_ref'] = cop_ref
        if group_id==1:
            try:
                p1_eer = parameters['p1_EER [-]'].array[0]
                p2_eer = parameters['p2_EER [-]'].array[0]
                p3_eer = parameters['p3_EER [-]'].array[0]
                p4_eer = parameters['p4_EER [-]'].array[0]
                eer_ref = p1_eer * 35 + p2_eer * 7 + p3_eer + p4_eer * 35
                parameters.loc[:,'P_th_c_ref [W]'] = p_el_ref * 0.6852 * eer_ref
                parameters['P_el_c_ref [W]'] = p_el_ref * 0.6852 #average value from real Heatpumps (P_el35/7 to P_el-7/52) 
                parameters.loc[:, 'EER_ref'] = eer_ref        
            except:
                pass
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
    df = pd.read_csv(cwd()+r'/hplib_database.csv', delimiter=',')
    df = df.loc[df['Model'] == model]
    parameters = pd.DataFrame()

    parameters['Model'] = (df['Model'].values.tolist())
    parameters['P_th_h_ref [W]'] = (df['P_th_h_ref [W]'].values.tolist())
    parameters['P_el_h_ref [W]'] = (df['P_el_h_ref [W]'].values.tolist())
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
        parameters.loc[:, 'P_th_h_ref [W]'] = p_th
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
        parameters.loc[:, 'P_el_h_ref [W]'] = p_el_ref
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
    df = simulate(t_in, t_out - 5, parameters, t_amb)
    p_th_calc=df.P_th.values[0]
    p_th_diff = p_th_calc - p_th_set_point
    return p_th_diff


def simulate(t_in_primary: any, t_in_secondary: any, parameters: pd.DataFrame,
             t_amb: any, modus: int = 1) -> pd.DataFrame:
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
    modus : int
        for heating: 1, for cooling: 2

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

    DELTA_T = 5 # Inlet temperature is supposed to be heated up by 5 K
    CP = 4200  # J/(kg*K), specific heat capacity of water
    t_in = t_in_primary#info value for dataframe
    T_amb = t_amb #info value for dataframe
    group_id = parameters['Group'].array[0]
    p1_p_el = parameters['p1_P_el [1/°C]'].array[0]
    p2_p_el = parameters['p2_P_el [1/°C]'].array[0]
    p3_p_el = parameters['p3_P_el [-]'].array[0]
    p4_p_el = parameters['p4_P_el [1/°C]'].array[0]
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
        p5_p_el = parameters['p5_P_el [1/°C]'].array[0]
        p6_p_el = parameters['p6_P_el [1/°C]'].array[0]
        p7_p_el = parameters['p7_P_el [-]'].array[0]
        p8_p_el = parameters['p8_P_el [1/°C]'].array[0]
        p_el_col_ref=parameters['P_el_c_ref [W]'].array[0]
    except:
        p1_eer = numpy.nan
        p2_eer = numpy.nan
        p3_eer = numpy.nan
        p4_eer = numpy.nan
        p5_p_el = numpy.nan
        p6_p_el = numpy.nan
        p7_p_el = numpy.nan
        p8_p_el = numpy.nan
        p_el_col_ref=numpy.nan
    # for subtype = air/water heat pump
    if group_id == 1 or group_id == 4:
        t_amb = t_in
    else:
        pass
    if(type(t_in)==pd.core.series.Series or type(t_in_secondary)==pd.core.series.Series or type(t_amb)==pd.core.series.Series):# for handling pandas.Series
        try:
            df=t_in.to_frame()
            df.rename(columns = {t_in.name:'T_in'}, inplace = True)
            df['Modus']=modus
            df.loc[df['Modus']==1,'T_out']=t_in_secondary + DELTA_T
            df.loc[df['Modus']==2,'T_out']=t_in_secondary - DELTA_T
            df['T_amb']=t_amb
            
        except:
            try:
                df=t_in_secondary.to_frame()
                df.rename(columns = {t_in_secondary.name:'T_out'}, inplace = True)
                df['Modus']=modus
                df.loc[df['Modus']==1,'T_out']=df['T_out']+ DELTA_T
                df.loc[df['Modus']==2,'T_out']=df['T_out'] - DELTA_T
                df['T_in']=t_in
                df['T_amb']=t_amb
            except:
                df=t_amb.to_frame()
                df.rename(columns = {t_amb.name:'T_amb'}, inplace = True)
                df['T_in']=t_in
                df['Modus']=modus
                df.loc[df['Modus']==1,'T_out']=t_in_secondary + DELTA_T
                df.loc[df['Modus']==2,'T_out']=t_in_secondary - DELTA_T
        if group_id == 1 or group_id == 2 or group_id == 3:
            df.loc[df['Modus']==1,'COP'] = p1_cop * t_in + p2_cop * df['T_out'] + p3_cop + p4_cop * t_amb
            df.loc[df['Modus']==1,'P_el'] = (p1_p_el * t_in + p2_p_el * df['T_out'] + p3_p_el + p4_p_el * t_amb) * p_el_ref #this is the first calculated value for P_el
            if group_id == 1:#with regulated heatpumps the electrical power can get too low. We defined a minimum value at 25% from the point at -7/output temperature.
                df.loc[df['Modus']==2,'EER'] = (p1_eer * t_in + p2_eer * df['T_out'] + p3_eer + p4_eer * t_amb)
                df.loc[df['Modus']==2,'P_el'] = (p5_p_el * t_in + p6_p_el * df['T_out'] + p7_p_el + p8_p_el * t_amb) * p_el_col_ref
                df.loc[(df['Modus']==2) & (df['T_in'] < 25),'P_el'] = p_el_col_ref * (p5_p_el * 25 + p6_p_el * df['T_out'] + p7_p_el + p8_p_el * 25)
                df.loc[(df['Modus']==2) & (df['EER']<1),'P_th'] = numpy.nan
                df.loc[(df['Modus']==2) & (df['EER']<1),'EER'] = numpy.nan
                df.loc[df['Modus']==2,'P_th'] = -(df['P_el'] * df['EER'])
                df.loc[(df['Modus']==2) & (df['P_el']<0),'EER'] = numpy.nan
                df.loc[(df['Modus']==2) & (df['P_el']<0),'P_th'] = numpy.nan
                df.loc[(df['Modus']==2) & (df['P_el']<0),'P_el'] = numpy.nan
                #df.loc[df['Modus']==2,'P_el'] = df['P_th'] / df['COP']
                df.loc[df['Modus']==1,'t_in'] = -7
                df.loc[df['Modus']==1,'t_amb'] = -7
            if group_id == 2:
                df['t_in']=df['T_in']
                df.loc[:,'t_amb'] = -7
            df.loc[(df['Modus']==1) & (df['P_el'] < 0.25 * p_el_ref * (p1_p_el * df['t_in'] + p2_p_el * df['T_out'] + p3_p_el + p4_p_el * df['t_amb'])),'P_el'] = 0.25 * p_el_ref * (p1_p_el * df['t_in'] + p2_p_el * df['T_out'] + p3_p_el + p4_p_el * df['t_amb'])
            df.loc[(df['Modus']==1) ,'P_th'] = (df['P_el'] * df['COP'])
            df.loc[(df['Modus']==1) & (df['COP'] < 1),'P_el']=p_th_ref#if COP is too low the electeric heating element is used in simulation
            df.loc[(df['Modus']==1) & (df['COP'] < 1),'P_th']=p_th_ref
            df.loc[(df['Modus']==1) & (df['COP'] < 1),'COP']=1
            df['m_dot']=df['P_th']/(DELTA_T * CP)
            del df['t_in']
            del df['t_amb']
        elif group_id == 4 or group_id == 5 or group_id == 6:
            df['COP'] = p1_cop * t_in + p2_cop * df['T_out'] + p3_cop + p4_cop * t_amb
            df['P_el'] = (p1_p_el * t_in + p2_p_el * df['T_out'] + p3_p_el + p4_p_el * t_amb) * p_el_ref
            df['P_th'] = df['P_el'] * df['COP']
            df.loc[df['COP'] < 1,'P_el']=p_th_ref
            df.loc[df['COP'] < 1,'P_th']=p_th_ref#if COP is too low the electeric heating element is used in simulation
            df.loc[df['COP'] < 1,'COP']=1
            df['m_dot']=df['P_th']/(DELTA_T * CP)
        df['P_el']=df['P_el'].round(0)
        df['COP']=df['COP'].round(2)
        df['m_dot']=df['m_dot'].round(3)
        df['m_dot']=df['m_dot'].abs()
    else:
        if modus==1:
            t_out = t_in_secondary + DELTA_T #Inlet temperature is supposed to be heated up by 5 K
            EER=0
        if modus==2: # Inlet temperature is supposed to be cooled down by 5 K
            t_out = t_in_secondary - DELTA_T
            COP=0
        # for regulated heat pumps
        if group_id == 1 or group_id == 2 or group_id == 3:
            if modus==1:
                COP = p1_cop * t_in + p2_cop * t_out + p3_cop + p4_cop * t_amb
                P_el = (p1_p_el * t_in + p2_p_el * t_out + p3_p_el + p4_p_el * t_amb) * p_el_ref
                if group_id == 1:
                    t_in = -7
                    t_amb = t_in
                if group_id == 2:
                    t_amb = -7
                
                if P_el < 0.25 * p_el_ref * (
                    p1_p_el * t_in + p2_p_el * t_out + p3_p_el + p4_p_el * t_amb):  # 25% of Pel @ -7°C T_amb = T_in
                    P_el = 0.25 * p_el_ref * (p1_p_el * t_in + p2_p_el * t_out + p3_p_el + p4_p_el * t_amb)
                P_th = P_el * COP
                if COP <= 1:
                    COP = 1
                    P_el = p_th_ref
                    P_th = p_th_ref
            elif modus==2:
                EER = (p1_eer * t_in + p2_eer * t_out + p3_eer + p4_eer * t_amb)
                
                if t_in<25:
                    t_in=25
                    t_amb=t_in
                P_el = (p5_p_el * t_in + p6_p_el * t_out + p7_p_el + p8_p_el * t_amb) * p_el_col_ref
                if P_el<0:
                    EER = 0
                    P_el = 0
                P_th = -(EER*P_el)
                if EER < 1:
                    EER = 0
                    P_el = 0
                    P_th = 0

        # for subtype = On-Off
        elif group_id == 4 or group_id == 5 or group_id == 6:
            P_el = (p1_p_el * t_in + p2_p_el * t_out + p3_p_el + p4_p_el * t_amb) * p_el_ref
            COP = p1_cop * t_in + p2_cop * t_out + p3_cop + p4_cop * t_amb
            P_th = P_el * COP
            if COP <= 1:
                COP = 1
                P_el = p_th_ref
                P_th = p_th_ref
        # massflow
        m_dot = P_th / (DELTA_T * CP)
        #round
        df=pd.DataFrame()
        
        df['T_in']=[t_in_primary]
        df['T_out']=[t_out]
        df['T_amb']=[T_amb]
        df['COP']=[COP]
        df['EER']=[EER]
        df['P_el']=[P_el]
        df['P_th']=[P_th]
        df['m_dot']=[abs(m_dot)]
    return df

def cwd():
    real_path = os.path.realpath(__file__)
    dir_path = os.path.dirname(real_path)
    return dir_path

class HeatPump:
    def __init__(self, parameters: pd.DataFrame):
        self.group_id = float(parameters['Group'].array[0])
        self.p1_p_el = float(parameters['p1_P_el [1/°C]'].array[0])
        self.p2_p_el = float(parameters['p2_P_el [1/°C]'].array[0])
        self.p3_p_el = float(parameters['p3_P_el [-]'].array[0])
        self.p4_p_el = float(parameters['p4_P_el [1/°C]'].array[0])
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
            self.p5_p_el = parameters['p5_P_el [1/°C]'].array[0]
            self.p6_p_el = parameters['p6_P_el [1/°C]'].array[0]
            self.p7_p_el = parameters['p7_P_el [-]'].array[0]
            self.p8_p_el = parameters['p8_P_el [1/°C]'].array[0]
            self.p_el_col_ref=parameters['P_el_c_ref [W]'].array[0]
        except:
            self.p1_eer = numpy.nan
            self.p2_eer = numpy.nan
            self.p3_eer = numpy.nan
            self.p4_eer = numpy.nan
            self.p5_p_el = numpy.nan
            self.p6_p_el = numpy.nan
            self.p7_p_el = numpy.nan
            self.p8_p_el = numpy.nan
            self.p_el_col_ref=numpy.nan

        self.delta_t = 5  # Inlet temperature is supposed to be heated up by 5 K
        self.cp = 4200  # J/(kg*K), specific heat capacity of water

    def simulate(self, t_in_primary: float, t_in_secondary: float, t_amb: float, modus: int = 1) -> dict:
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
        modus : int
            for heating: 1, for cooling: 2

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

        t_in = t_in_primary  # info value for dataframe
        if modus==1:
            t_out = t_in_secondary + self.delta_t #Inlet temperature is supposed to be heated up by 5 K
            eer=0
        if modus==2: # Inlet temperature is supposed to be cooled down by 5 K
            t_out = t_in_secondary - self.delta_t
            cop=0
        # for subtype = air/water heat pump
        if self.group_id in (1, 4):
            t_amb = t_in
        t_ambient=t_amb
        # for regulated heat pumps
        if self.group_id in (1, 2, 3):
            if modus==1:
                cop = self.p1_cop * t_in + self.p2_cop * t_out + self.p3_cop + self.p4_cop * t_amb

                p_el = (self.p1_p_el * t_in
                        + self.p2_p_el * t_out
                        + self.p3_p_el
                        + self.p4_p_el * t_amb) * self.p_el_ref

                if self.group_id == 1:
                    t_in = -7
                    t_amb = t_in
                elif self.group_id == 2:
                    t_amb = -7

                # 25% of Pel @ -7°C T_amb = T_in
                if p_el < 0.25 * self.p_el_ref * (self.p1_p_el * t_in
                                                + self.p2_p_el * t_out
                                                + self.p3_p_el
                                                + self.p4_p_el * t_amb):

                    p_el = 0.25 * self.p_el_ref * (self.p1_p_el * t_in
                                                + self.p2_p_el * t_out
                                                + self.p3_p_el
                                                + self.p4_p_el * t_amb)

                p_th = p_el * cop

                if cop <= 1:
                    cop = 1
                    p_el = self.p_th_ref
                    p_th = self.p_th_ref
            if modus==2:
                eer = (self.p1_eer * t_in + self.p2_eer * t_out + self.p3_eer + self.p4_eer * t_amb)
                if t_in<25:
                    t_in=25
                    t_amb=t_in
                p_el = (self.p5_p_el * t_in + self.p6_p_el * t_out + self.p7_p_el + self.p8_p_el * t_amb) * self.p_el_col_ref
                if p_el<0:
                    eer = 0
                    p_el = 0
                p_th = -(eer*p_el)
                if eer < 1:
                    eer = 0
                    p_el = 0
                    p_th = 0

        # for subtype = On-Off
        elif self.group_id in (4, 5, 6):
            p_el = (self.p1_p_el * t_in
                    + self.p2_p_el * t_out
                    + self.p3_p_el
                    + self.p4_p_el * t_amb) * self.p_el_ref

            cop = self.p1_cop * t_in + self.p2_cop * t_out + self.p3_cop + self.p4_cop * t_amb

            p_th = p_el * cop

            if cop <= 1:
                cop = 1
                p_el = self.p_th_ref
                p_th = self.p_th_ref

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
