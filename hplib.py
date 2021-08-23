import pandas as pd

def getParameters(model): #to do: optional keywords
    df = pd.read_csv('hplib-database.csv', delimiter=',')
    df = df.loc[df['Model'] == model]
    parameters=[]
    parameters.append(df['Model'].values.tolist()[0])
    parameters.append(df['P_th_ref [W]'].values.tolist()[0])
    parameters.append(df['P_el_ref [W]'].values.tolist()[0])
    parameters.append(df['Group'].values.tolist()[0])
    parameters.append(df['p1_P_th [1/°C]'].values.tolist()[0])
    parameters.append(df['p2_P_th [1/°C]'].values.tolist()[0])
    parameters.append(df['p3_P_th [-]'].values.tolist()[0])
    parameters.append(df['p1_P_el [1/°C]'].values.tolist()[0])
    parameters.append(df['p2_P_el [1/°C]'].values.tolist()[0])
    parameters.append(df['p3_P_el [-]'].values.tolist()[0])
    parameters.append(df['p1_COP [-]'].values.tolist()[0])
    parameters.append(df['p2_COP [-]'].values.tolist()[0])
    parameters.append(df['p3_COP [-]'].values.tolist()[0])
    return parameters

def simulate(x,y,parameters):
    #input  x -> T_in [°C]
    #       y -> T_out [°C]
    #       parameters -> list from function getParameters()
    Group=parameters[3]
    k4=parameters[7]
    k5=parameters[8]
    k6=parameters[9]
    k7=parameters[10]
    k8=parameters[11]
    k9=parameters[12]
    Pel_ref=parameters[2]
    Pth_ref=parameters[1]
    # for subtype = Inverter
    if Group==(1 or 2 or 3):
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
    elif Group==(4 or 5 or 6):
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