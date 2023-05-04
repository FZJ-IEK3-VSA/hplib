def cop_carnot(T_source, T_sink, efficiency_grade = 0.45, b_hp =0):
    """
    Calculates the coefficient of performance of a heat pump based on the
    carnot efficiency.

    E.g., used by Stadler 2018, Girardin 2012, Huchtemann 2015, Kotzur 2018, Lauinger 2016
    
    Patteeuw 2015, Bettgenhäuser ??, use b_hp not equal zero. 
    
    Parameters
    ----------
    T_source : float
        Temperature of the heat source in °C.
    T_sink : float
        Temperature of the heat sink in °C.
    efficiency_grade : float, optional
        Efficiency grade of the heat pump. The default is 0.45.
    b_hp : float, optional
        Additional losses of the heat pump. The default is 0.

    Returns
    -------
    float
        Coefficient of performance of the heat pump.
    """

    return efficiency_grade * (T_sink + 273.15) / (T_sink - T_source + b_hp)

def cop_schlosser(T_source, T_sink, a = 1.448e10, b = 88.730, c = 4.9460, d = 0.0):
    """
    Calculates the coefficient of efficiency of a heat pump based on the
    function of Schlosser et al. 2018

    Parameters
    ----------
    T_source : float
        Temperature of the heat source in °C.
    T_sink : float
        Temperature of the heat sink in °C.
    a : float, optional
        Parameter a of the function. The default is 1.448e10.
    b : float, optional
        Parameter b of the function. The default is 88.730.
    c : float, optional
        Parameter c of the function. The default is 4.9460.
    d : float, optional
        Parameter d of the function. The default is 0.0.
    
    Returns
    -------
    float
        Coefficient of efficiency of the heat pump.
    """
    delta_T = T_sink - T_source
    return a * (delta_T + 2 * b) ** c + (T_sink + b ) ** d


def cop_poolynomial(T_source, T_sink, k_0 = 6.81, k_1 = - 0.121, k_2 = 0.00063):
    """
    Derives the coefficient of performance based on a 2n degree polynomial function.
    The proposed parameters are from Staffel 2012 for an air source heatpump.
    Ground source:
    k_0 = 8.77, k_1 = - 0.150, k_2 = 0.000734

    Used by Staffel 2012, Runau 2019, Fischer 2017, Lindberg 2015,2016. 

    
    Parameters
    ----------
    T_source : float
        Temperature of the heat source in °C.
    T_sink : float
        Temperature of the heat sink in °C.
    k_0 : float, optional
        Parameter k_0 of the function. The default is 6.81.
    k_1 : float, optional
        Parameter k_1 of the function. The default is - 0.121.
    k_2 : float, optional
        Parameter k_2 of the function. The default is 0.00063.

    Returns
    -------
    float
        Coefficient of performance of the heat pump.
    """
    delta_T = T_sink - T_source
    return k_0 + k_1 * delta_T + k_2 * delta_T ** 2


def cop_schwamberger(T_source, T_sink, p1_cop = 57.53, 
                     p2_cop = -0.06, p3_cop = 5.67, p4_cop = -57.43):
    """
    COP calculation based on Schwamberg 1991.
    K. Schwamberger: „Modellbildung und Regelung von Gebäudeheizungsanlagen mit Wärmepumpen“, VDI Verlag, Düsseldorf, Fortschrittsberichte VDI Reihe 6 Nr. 263, 1991.
    Used in the current version of this package. 

    The default values are taken from the generic regulated 
    air source heat pump.
    
    Parameters
    ----------
    T_source : float
        Temperature of the heat source in °C.
    T_sink : float
        Temperature of the heat sink in °C.
    p1_cop : float, optional
        Parameter p1_cop of the function. The default is 57.53.
    p2_cop : float, optional
        Parameter p2_cop of the function. The default is -0.06.
    p3_cop : float, optional
        Parameter p3_cop of the function. The default is 5.67.
    p4_cop : float, optional
        Parameter p4_cop of the function. The default is -57.43.
    
    Returns
    -------
    float
    """
    # the original model goes with supply and return temperature
    # t_in = T_source - delta_t / 2

    # the package defined a fixed delta t of 5 K
    delta_t = 5 # K

    t_in = T_source - delta_t
    t_out = T_sink
    t_amb = T_source
    return p1_cop * t_in + p2_cop * t_out + p3_cop + p4_cop * t_amb