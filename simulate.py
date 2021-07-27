import pandas as pd

def getParafast(model,para): #para is the dataframe 'data_key_para.csv' this is a fast method
    para = para.loc[para['Model'] == model]
    parameters=[]
    parameters.append(para['Group'].values.tolist()[0])
    parameters.append(para['k1'].values.tolist()[0])
    parameters.append(para['k2'].values.tolist()[0])
    parameters.append(para['k3'].values.tolist()[0])
    parameters.append(para['k4'].values.tolist()[0])
    parameters.append(para['k5'].values.tolist()[0])
    parameters.append(para['k6'].values.tolist()[0])
    parameters.append(para['k7'].values.tolist()[0])
    parameters.append(para['k8'].values.tolist()[0])
    parameters.append(para['k9'].values.tolist()[0])
    parameters.append(para['P_el_n [W]'].values.tolist()[0])
    parameters.append(para['P_th_max [W]'].values.tolist()[0])
    return parameters
def getParaeasy(model): #only with model name you get the data needed for fit. Takes a bit longer
    para = pd.read_csv('hplib.csv', delimiter=',')
    para = para.loc[para['Model'] == model]
    parameters=[]
    parameters.append(para['Group'].values.tolist()[0])
    parameters.append(para['k1'].values.tolist()[0])
    parameters.append(para['k2'].values.tolist()[0])
    parameters.append(para['k3'].values.tolist()[0])
    parameters.append(para['k4'].values.tolist()[0])
    parameters.append(para['k5'].values.tolist()[0])
    parameters.append(para['k6'].values.tolist()[0])
    parameters.append(para['k7'].values.tolist()[0])
    parameters.append(para['k8'].values.tolist()[0])
    parameters.append(para['k9'].values.tolist()[0])
    parameters.append(para['P_el_n [W]'].values.tolist()[0])
    parameters.append(para['P_th_max [W]'].values.tolist()[0])
    return parameters
def getPowerHP(x,y,parameter): #input is: x -> input temperature
                                        # y -> outflow temperature
                                        #parameter -> list from getpara(easy/fast)
    Group=parameter[0]
    k4=parameter[4]
    k5=parameter[5]
    k6=parameter[6]
    k7=parameter[7]
    k8=parameter[8]
    k9=parameter[9]
    Pel_n=parameter[10]
    Pth_max=parameter[11]
    PSUP=0
    if Group==(1 or 2 or 3):
        if x>=5: #minimum electrical Power at 5°C
            x=5
        Pel=(k4*x+k5*y+k6)*Pel_n
        if((Pel/Pel_n)<(0.15)):
            Pel=Pel_n*0.15
        COP=k7*x+k8*y+k9
        Pth=Pel*COP
        if COP<=1:
            COP=1
            Pel=0
            PSUP=Pth_max
            Pth=Pth_max
    elif Group==(4 or 5 or 6):
        Pel=(k4*x+k5*y+k6)*Pel_n
        if((Pel/Pel_n)<(0.15)):
            Pel=Pel_n*0.15
        COP=k7*x+k8*y+k9
        Pth=Pel*COP
        if COP<=1:
            COP=1
            Pel=0
            PSUP=Pth_max
            Pth=Pth_max
    else:
        Pel=(k4*x+k5*y+k6)*Pel_n
        if((Pel/Pel_n)<(0.15)):
            Pel=Pel_n*0.15
        COP=k7*x+k8*y+k9
        Pth=Pel*COP
        if COP<=1:
            COP=1
            Pel=0
            PSUP=Pth_max
            Pth=Pth_max
    return Pth,Pel,PSUP,COP