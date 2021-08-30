import pandas as pd

def loadDatabase():
    df = pd.read_csv('hplib_database.csv')
    return df

def getParameters(model, Group=0, P_th_ref=10000): #to do: optional keywords
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
    parameters['p1_P_el [1/°C]']=(df['p1_P_el [1/°C]'].values.tolist())
    parameters['p2_P_el [1/°C]']=(df['p2_P_el [1/°C]'].values.tolist())
    parameters['p3_P_el [-]']=(df['p3_P_el [-]'].values.tolist())
    parameters['p1_COP [-]']=(df['p1_COP [-]'].values.tolist())
    parameters['p2_COP [-]']=(df['p2_COP [-]'].values.tolist())
    parameters['p3_COP [-]']=(df['p3_COP [-]'].values.tolist())
    if model=='Generic':
        parameters=parameters.iloc[Group-1:Group]
        parameters.loc[:, 'P_th_ref [W]'] = P_th_ref
        x=-7
        y=52
        k4=parameters['p1_P_el [1/°C]'].array[0]
        k5=parameters['p2_P_el [1/°C]'].array[0]
        k6=parameters['p3_P_el [-]'].array[0]
        k7=parameters['p1_COP [-]'].array[0]
        k8=parameters['p2_COP [-]'].array[0]
        k9=parameters['p3_COP [-]'].array[0]
        COP_ref=k7*x+k8*y+k9
        P_el_ref=P_th_ref/COP_ref
        parameters.loc[:, 'P_el_ref [W]'] = P_el_ref
        parameters.loc[:, 'COP_ref'] = COP_ref
    return parameters

def simulate(T_in_primary,T_in_secondary,parameters):
    #input  T_in_primary [°C]
    #       T_in_secondary [°C]
    #       parameters -> list from function getParameters()
    
    x=T_in_primary
    y=T_in_secondary+5 # Inlet temperature is supposed to be heated up by 5 K
    Group=parameters['Group'].array[0]
    k4=parameters['p1_P_el [1/°C]'].array[0]
    k5=parameters['p2_P_el [1/°C]'].array[0]
    k6=parameters['p3_P_el [-]'].array[0]
    k7=parameters['p1_COP [-]'].array[0]
    k8=parameters['p2_COP [-]'].array[0]
    k9=parameters['p3_COP [-]'].array[0]
    Pel_ref=parameters['P_el_ref [W]'].array[0]
    Pth_ref=parameters['P_th_ref [W]'].array[0]
    # for subtype = Inverter
    if Group==1 or Group==2 or Group==3:
        COP=k7*x+k8*y+k9
        if x>=5: #minimum electrical Power at 5°C
            x=5
        Pel=(k4*x+k5*y+k6)*Pel_ref
        Pth=Pel*COP
        if COP<=1:
            COP=1
            Pel=Pth_ref
            Pth=Pth_ref
        
    # for subtype = On-Off
    elif Group==4 or Group==5 or Group==6:
        Pel=(k4*x+k5*y+k6)*Pel_ref
        COP=k7*x+k8*y+k9
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
    
    return Pth,Pel,COP