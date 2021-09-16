import pandas as pd
import scipy

def loadDatabase():
    df = pd.read_csv('hplib_database.csv')
    return df

def getParameters(model, Group=0, T_in=0, T_out=0, P_th=0):
    df = pd.read_csv('hplib_database.csv', delimiter=',')
    df = df.loc[df['Model'] == model]
    parameters=pd.DataFrame()
    
    parameters['Model']=(df['Model'].values.tolist())
    parameters['P_th_ref [W]']=(df['P_th_ref [W]'].values.tolist())
    parameters['P_el_ref [W]']=(df['P_el_ref [W]'].values.tolist())
    parameters['COP_ref']=(df['COP_ref'].values.tolist())
    parameters['Group']=(df['Group'].values.tolist())
    parameters['p1_P_th [1/°C]']=(df['p1_P_th [1/°C]'].values.tolist())
    parameters['p2_P_th [1/°C]']=(df['p2_P_th [1/°C]'].values.tolist())
    parameters['p3_P_th [-]']=(df['p3_P_th [-]'].values.tolist())
    parameters['p4_P_th [1/°C]']=(df['p4_P_th [1/°C]'].values.tolist())
    parameters['p1_P_el [1/°C]']=(df['p1_P_el [1/°C]'].values.tolist())
    parameters['p2_P_el [1/°C]']=(df['p2_P_el [1/°C]'].values.tolist())
    parameters['p3_P_el [-]']=(df['p3_P_el [-]'].values.tolist())
    parameters['p4_P_el [1/°C]']=(df['p4_P_el [1/°C]'].values.tolist())
    parameters['p1_COP [-]']=(df['p1_COP [-]'].values.tolist())
    parameters['p2_COP [-]']=(df['p2_COP [-]'].values.tolist())
    parameters['p3_COP [-]']=(df['p3_COP [-]'].values.tolist())
    parameters['p4_COP [-]']=(df['p4_COP [-]'].values.tolist())

    if model=='Generic':
        parameters=parameters.iloc[Group-1:Group]
        parameters.loc[:, 'P_th_ref [W]'] = fit_P_th_ref(T_in, T_out, Group, P_th)
        x=-7
        y=52
        p1_P_el=parameters['p1_P_el [1/°C]'].array[0]
        p2_P_el=parameters['p2_P_el [1/°C]'].array[0]
        p3_P_el=parameters['p3_P_el [-]'].array[0]
        p1_COP=parameters['p1_COP [-]'].array[0]
        p2_COP=parameters['p2_COP [-]'].array[0]
        p3_COP=parameters['p3_COP [-]'].array[0]
        p4_COP=parameters['p4_COP [-]'].array[0]
        COP_ref=p1_COP*x+p2_COP*y+p3_COP+p4_COP*x
        P_el_ref=fit_P_th_ref(T_in, T_out, Group, P_th) / COP_ref
        parameters.loc[:, 'P_el_ref [W]'] = P_el_ref
        parameters.loc[:, 'COP_ref'] = COP_ref
    return parameters

def getParameters_fit(model, Group=0, P_th=0):
    df = pd.read_csv('hplib_database.csv', delimiter=',')
    df = df.loc[df['Model'] == model]
    parameters=pd.DataFrame()
    
    parameters['Model']=(df['Model'].values.tolist())
    parameters['P_th_ref [W]']=(df['P_th_ref [W]'].values.tolist())
    parameters['P_el_ref [W]']=(df['P_el_ref [W]'].values.tolist())
    parameters['COP_ref']=(df['COP_ref'].values.tolist())
    parameters['Group']=(df['Group'].values.tolist())
    parameters['p1_P_th [1/°C]']=(df['p1_P_th [1/°C]'].values.tolist())
    parameters['p2_P_th [1/°C]']=(df['p2_P_th [1/°C]'].values.tolist())
    parameters['p3_P_th [-]']=(df['p3_P_th [-]'].values.tolist())
    parameters['p4_P_th [1/°C]']=(df['p4_P_th [1/°C]'].values.tolist())
    parameters['p1_P_el [1/°C]']=(df['p1_P_el [1/°C]'].values.tolist())
    parameters['p2_P_el [1/°C]']=(df['p2_P_el [1/°C]'].values.tolist())
    parameters['p3_P_el [-]']=(df['p3_P_el [-]'].values.tolist())
    parameters['p4_P_el [1/°C]']=(df['p4_P_el [1/°C]'].values.tolist())
    parameters['p1_COP [-]']=(df['p1_COP [-]'].values.tolist())
    parameters['p2_COP [-]']=(df['p2_COP [-]'].values.tolist())
    parameters['p3_COP [-]']=(df['p3_COP [-]'].values.tolist())
    parameters['p4_COP [-]']=(df['p4_COP [-]'].values.tolist())
    if model=='Generic':
        parameters=parameters.iloc[Group-1:Group]
        parameters.loc[:, 'P_th_ref [W]'] = P_th
        x=-7
        y=52
        p1_P_el=parameters['p1_P_el [1/°C]'].array[0]
        p2_P_el=parameters['p2_P_el [1/°C]'].array[0]
        p3_P_el=parameters['p3_P_el [-]'].array[0]
        p1_COP=parameters['p1_COP [-]'].array[0]
        p2_COP=parameters['p2_COP [-]'].array[0]
        p3_COP=parameters['p3_COP [-]'].array[0]
        p4_COP=parameters['p4_COP [-]'].array[0]
        COP_ref=p1_COP*x+p2_COP*y+p3_COP+p4_COP*x
        P_el_ref=P_th/COP_ref
        parameters.loc[:, 'P_el_ref [W]'] = P_el_ref
        parameters.loc[:, 'COP_ref'] = COP_ref
    return parameters

def fit_P_th_ref(T_in, T_out, Group, P_th_vorgabe):
    p0=[1000] # starting values
    a=(T_in, T_out, Group, P_th_vorgabe) 
    P_th,_ = scipy.optimize.leastsq(fitfunc_P_th_ref,p0,args=a)
    return P_th

def fitfunc_P_th_ref(P_th, T_in, T_out, Group, P_th_vorgabe):
    parameters = getParameters_fit('Generic',Group=Group, P_th=P_th)
    P_th_calc,_,_,_,_ = simulate(T_in,T_out-5,parameters,T_in)
    P_th_diff = P_th_calc - P_th_vorgabe
    return P_th_diff

def simulate(T_in_primary, T_in_secondary, parameters, T_amb=0):
    #inputs  
    # T_in_primary [°C], source temperature (air or ground)
    # T_in_secondary [°C], source temperature from heating storage or system
    # parameters -> list from function getParameters()
    # T_amb [°C], ambient temperature of the air
    
    delta_T = 5 # Inlet temperature is supposed to be heated up by 5 K
    cp = 4200 # J/(kg*K), specific heat capacity of water
    T_in=T_in_primary
    T_out=T_in_secondary + delta_T
    Model=parameters['Model'].array[0]
    Group=parameters['Group'].array[0]
    p1_P_th=parameters['p1_P_th [1/°C]'].array[0]
    p2_P_th=parameters['p2_P_th [1/°C]'].array[0]
    p3_P_th=parameters['p3_P_th [-]'].array[0]
    p4_P_th=parameters['p4_P_th [1/°C]'].array[0]
    p1_P_el=parameters['p1_P_el [1/°C]'].array[0]
    p2_P_el=parameters['p2_P_el [1/°C]'].array[0]
    p3_P_el=parameters['p3_P_el [-]'].array[0]
    p4_P_el=parameters['p4_P_el [1/°C]'].array[0]
    p1_COP=parameters['p1_COP [-]'].array[0]
    p2_COP=parameters['p2_COP [-]'].array[0]
    p3_COP=parameters['p3_COP [-]'].array[0]
    p4_COP=parameters['p4_COP [-]'].array[0]
    Pel_ref=parameters['P_el_ref [W]'].array[0]
    Pth_ref=parameters['P_th_ref [W]'].array[0]
    # for subtype = Inverter
    if Group==1 or Group==4:
        T_amb=T_in
    else:
        pass

    if Group==1 or Group==2 or Group==3:
        COP=p1_COP*T_in+p2_COP*T_out+p3_COP+p4_COP*T_amb
        Pel=(p1_P_el*T_in+p2_P_el*T_out+p3_P_el+p4_P_el*T_amb)*Pel_ref
        if Pel < 0.15*Pel_ref: # alternatively 15% of Pel @ -7°C and T_in
            Pel = 0.15*Pel_ref
        Pth=Pel*COP
        if COP<=1:
            COP=1
            Pel=Pth_ref
            Pth=Pth_ref   
    # for subtype = On-Off
    elif Group==4 or Group==5 or Group==6:
        Pel=(p1_P_el*T_in+p2_P_el*T_out+p3_P_el+p4_P_el*T_amb)*Pel_ref
        COP=p1_COP*T_in+p2_COP*T_out+p3_COP+p4_COP*T_amb
        Pth=Pel*COP
        if COP<=1:
            COP=1
            Pel=Pth_ref
            Pth=Pth_ref
    # for subtype = Two-stages
    else:
        Pel=0
        COP=0
        Pth=0
        if COP<=1:
            COP=1
            Pel=Pth_ref
            Pth=Pth_ref
    # massflow
    m_dot = Pth / (delta_T * cp)

    return Pth,Pel,COP,T_out,m_dot