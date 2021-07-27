import os
import glob
import pandas as pd
import scipy
from scipy.optimize import curve_fit

def get_modus(P_th_minus7_34, P_th_2_30, P_th_7_27, P_th_12_24):
    if (P_th_minus7_34 <= P_th_2_30):
        if (P_th_2_30 <= P_th_7_27):
            if (P_th_7_27 <= P_th_12_24):
                modus='On-Off'#\\\
            else:
                modus='On-Off'#/\\ idk why but its true examples: AQUATOP S08; TTF 35
        else:
            if(P_th_7_27 <= P_th_12_24):
                modus='2-Stages'#\/\
            else:
                modus='Inverter'#\//
    else:
        modus='Inverter'#/\/
    if (P_th_minus7_34 == P_th_12_24):
        modus='delete'
    return modus    
def fit_simple(x,y,z):
    p0=[0.1,0.001,1.] # starting values
    a=(x,y,z) 
    para,_ = scipy.optimize.leastsq(func_simple_zero,p0,args=a)
    return para
def func_simple_zero(para, x, y, z):
    k1,k2,k3 = para
    z_calc = k1*x + k2*y + k3
    z_diff = z_calc - z
    return z_diff
def func_simple(para, x, y):
    # Function to calculate z using parameters and any x and y:
    k1,k2,k3 = para
    z = k1*x + k2*y + k3
    return z

def AssignGroup(filename):
    #Every Heatpump gets a modus depending on its modus and Type
    data_key = pd.read_csv(r'output/'+ filename) #read Dataframe of all models
    filt1 = (data_key['Type'] == 'Outdoor Air/Water') & (data_key['Modus']=='Inverter')
    data_key.loc[filt1, 'Group'] = 1
    filt1 = (data_key['Type'] == 'Exhaust Air/Water') & (data_key['Modus']=='Inverter')
    data_key.loc[filt1, 'Group'] = 1
    filt1 = (data_key['Type'] == 'Brine/Water') & (data_key['Modus']=='Inverter')
    data_key.loc[filt1, 'Group'] = 2
    filt1 = (data_key['Type'] == 'Water/Water') & (data_key['Modus']=='Inverter')
    data_key.loc[filt1, 'Group'] = 3


    filt1 = (data_key['Type'] == 'Outdoor Air/Water') & (data_key['Modus']=='On-Off')
    data_key.loc[filt1, 'Group'] = 4
    filt1 = (data_key['Type'] == 'Exhaust Air/Water') & (data_key['Modus']=='On-Off')
    data_key.loc[filt1, 'Group'] = 4
    filt1 = (data_key['Type'] == 'Brine/Water') & (data_key['Modus']=='On-Off')
    data_key.loc[filt1, 'Group'] = 5
    filt1 = (data_key['Type'] == 'Water/Water') & (data_key['Modus']=='On-Off')
    data_key.loc[filt1, 'Group'] = 6

    filt1 = (data_key['Type'] == 'Outdoor Air/Water') & (data_key['Modus']=='2-Stages')
    data_key.loc[filt1, 'Group'] = 7
    filt1 = (data_key['Type'] == 'Exhaust Air/Water') & (data_key['Modus']=='2-Stages')
    data_key.loc[filt1, 'Group'] = 7
    filt1 = (data_key['Type'] == 'Brine/Water') & (data_key['Modus']=='2-Stages')
    data_key.loc[filt1, 'Group'] = 8
    filt1 = (data_key['Type'] == 'Water/Water') & (data_key['Modus']=='2-Stages')
    data_key.loc[filt1, 'Group'] = 9
    data_key.to_csv(r'output/'+filename[:-4]+'_group.csv', encoding='utf-8', index=False)

def GetModusforeveryModel(filename):
    #Get Modus like Inverter or On-Off or Two-Stages by comparing the thermal Power output at different temperature levels:
    #-7/34 |  2/30  |  7/27  |  12/24
    #assumptions for On-Off Heatpump: if temperature difference is bigger thermal Power output is smaller
    #assumptions for 2 stages Heatpump: if temperature difference is bigger thermal Power output is smaller but it has one Jump in between 2/30 and 7/27
    #assumptions for Inverter: the rest

    data_key = pd.read_csv(r'output/'+filename) #read Dataframe of all models
    Models=data_key['Model'].values.tolist()
    Models = list(dict.fromkeys(Models))
    data_keymark = data_key.rename(columns={'P_el [W]': 'P_el', 'P_th [W]': 'P_th', 'T_in [°C]': 'T_in', 'T_out [°C]': 'T_out'})
    data_keymark['deltaT']=data_keymark['T_out']-data_keymark['T_in']

    Moduslist=[]
    for model in Models:
        try:
            P_thermal=[]
            filt1=data_keymark['T_out']==34
            Tin_minus_seven = data_keymark.loc[filt1]
            filt2=Tin_minus_seven['Model']==model
            Model_minus_seven = Tin_minus_seven[filt2]
            P_th_minus_seven = Model_minus_seven['P_th'].array[0]
            P_thermal.append(P_th_minus_seven)


            filt1=data_keymark['T_out']==30
            T_in_plus_two = data_keymark.loc[filt1]
            filt2=T_in_plus_two['Model']==model
            Model_plus_two = T_in_plus_two[filt2]
            P_th_plus_two = Model_plus_two['P_th'].array[0]
            P_thermal.append(P_th_plus_two)

            filt1=data_keymark['T_out']==27
            Tin_plus_seven = data_keymark.loc[filt1]
            filt2=Tin_plus_seven['Model']==model
            Model_plus_seven = Tin_plus_seven[filt2]
            P_th_plus_seven = Model_plus_seven['P_th'].array[0]
            P_thermal.append(P_th_plus_seven)

            filt1=data_keymark['T_out']==24
            Tin_plus_twelfe = data_keymark.loc[filt1]
            filt2=Tin_plus_twelfe['Model']==model
            Model_plus_twelfe = Tin_plus_twelfe[filt2]
            P_th_plus_twelfe = Model_plus_twelfe['P_th'].array[0]
            P_thermal.append(P_th_plus_twelfe)
            P_thermal
            Modus = get_modus(P_thermal[0],P_thermal[1],P_thermal[2],P_thermal[3])
        except:
            print(model)
        Moduslist.append(Modus)
    Modusdf = pd.DataFrame()
    Modusdf['Model']=Models
    Modusdf['Modus']=Moduslist
    Modusdf
    data_key = pd.read_csv(r'output/'+filename) #read Dataframe of all models
    data_key=data_key.merge(Modusdf, how='inner', on='Model')
    data_key.to_csv(r'output/'+filename[:-4]+'_modus.csv', encoding='utf-8', index=False)

def NormalizeKeymarkData(filename):
    data_key = pd.read_csv(r'output/'+filename) #read Dataframe of all models
    Models=data_key['Model'].values.tolist()
    Models = list(dict.fromkeys(Models))
    new_df=pd.DataFrame()
    for model in Models:
        data_key = pd.read_csv(r'output/'+filename) #read Dataframe of all models
        Pth_ref=data_key.loc[((data_key['Model']==model) & (data_key['T_out [°C]']==52))]#only use data of model and ref point -7/52
        Pel_ref=Pth_ref['P_el [W]'].array[0]#ref Point Pel
        Pth_ref=Pth_ref['P_th [W]'].array[0]#ref Point Pth
        data_key=data_key.loc[data_key['Model']==model]#only use data of model
        data_key.loc[:,['P_th_n']]= data_key['P_th [W]']/Pth_ref #get normalized Value P_th_n
        data_key.loc[:,['P_el_n']]= data_key['P_el [W]']/Pel_ref #get normalized Value P_el_n
        new_df=pd.concat([new_df,data_key]) #merge new Dataframe with old one
    new_df.to_csv(r'output/'+filename[:-4]+'_normalized.csv', encoding='utf-8', index=False)

def ReduceKeymarkData(filename, climate):
    # reduce the hplib_database_keymark to a specific climate measurement series (average, warm, cold)
    # delete redundant entries
    # climate = average, warm or cold
    df = pd.read_csv('output/'+filename)
    data_key = df.loc[df['Climate']== climate]
    delete=[]
    Models=data_key['Model'].values.tolist()
    Models = list(dict.fromkeys(Models))
    for model in Models:
        Modeldf = data_key.loc[data_key['Model']==model,:]
        if Modeldf.shape[0]!=8: #Models with more ar less than 8 datapoints are deletet
            delete.append('delete')
        else:
            delete.append('keep')
    deletemodels=pd.DataFrame()
    deletemodels['delete']=delete
    deletemodels['Model']=Models
    data_key=data_key.merge(deletemodels, how='inner', on='Model')
    data_key=data_key.loc[data_key['delete']=='keep']
    data_key.drop(columns=['delete'], inplace=True)
    data_key.to_csv(os.getcwd()+r'/output/database_keymark_'+climate+'.csv', index=False)

def GetParameters(filename):
    #get normalized Parameters 
    data_key = pd.read_csv(r'output/'+ filename)
    Models=data_key['Model'].values.tolist()
    Models = list(dict.fromkeys(Models))#get models

    Group=[]
    Pel_n=[]
    Pth_max=[]
    k1=[]
    k2=[]
    k3=[]
    k4=[]
    k5=[]
    k6=[]
    k7=[]
    k8=[]
    k9=[]

    for model in Models:
        data_key = pd.read_csv(r'output/'+filename)
        data_key = data_key.rename(columns={'P_el [W]': 'P_el', 'P_th [W]': 'P_th', 'T_in [°C]': 'T_in', 'T_out [°C]': 'T_out'})
        data_key = data_key.loc[data_key['Model'] == model]#get data of model
        group = data_key.Group.array[0]#get Group of model
        Pel_ref=data_key.loc[data_key['P_el_n']==1,['P_el']].values.tolist()[0][0]
        Pth_52=data_key.loc[data_key['T_out']==52,['P_th']].values.tolist()[0][0]
        K = 273.15
        eta_carnot_key = (data_key['T_out']+K) / ((data_key['T_out']+K)-(data_key['T_in']+K))
        data_key['eta'] = data_key['COP'] / eta_carnot_key
        data_key.fillna(0, inplace=True)
        variables=['P_el_n', 'P_th_n', 'COP', 'eta']
            
        for var in variables: #get all parameters
            vars()[var+'_para_key'] = fit_simple(data_key['T_in'],data_key['T_out'],data_key[var])
            data_key[var+'_fit'] = func_simple(globals()[var+'_para_key'], data_key['T_in'], data_key['T_out'])
            data_key[var+'_fit_err'] = (data_key[var+'_fit'] - data_key[var]) / data_key[var] * 100
            d = data_key[var+'_fit_err'].mean(), data_key[var+'_fit_err'].max(), data_key[var+'_fit_err'].min()
            vars()[var+'_err'] = pd.DataFrame(d, index=['mean', 'max', 'min'])
        #write Parameters in List
        k1.append(P_th_n_para_key[0])
        k2.append(P_th_n_para_key[1])
        k3.append(P_th_n_para_key[2])
        k4.append(P_el_n_para_key[0])
        k5.append(P_el_n_para_key[1])
        k6.append(P_el_n_para_key[2])
        k7.append(COP_para_key[0])
        k8.append(COP_para_key[1])
        k9.append(COP_para_key[2])
        Group.append(group)
        Pel_n.append(Pel_ref)
        Pth_max.append(Pth_52)
    #write List  in Dataframe

    paradf=pd.DataFrame()
    paradf['Model']=Models
    paradf['k1']=k1 
    paradf['k2']=k2
    paradf['k3']=k3
    paradf['k4']=k4
    paradf['k5']=k5
    paradf['k6']=k6
    paradf['k7']=k7
    paradf['k8']=k8
    paradf['k9']=k9
    paradf['Group']=Group
    paradf['P_el_n']=Pel_n
    paradf['P_th_max']=Pth_max

    para = paradf
    key = pd.read_csv(r'output/'+filename)
    key=key.loc[key['T_out [°C]']==52]
    parakey=para.merge(key, how='left', on='Model')
    parakey = parakey.rename(columns={'Group_x': 'Group','P_el_n_x': 'P_el_n [W]','Prated [W]': 'Prated [kW]','P_th_max':'P_th_max [W]'})
    table=parakey[['Manufacturer', 'Model', 'Type', 'Modus','Refrigerant','Mass of Refrigerant [kg]','Date','SPL indoor [dBA]','SPL outdoor [dBA]','Prated [kW]','PSB [W]','Guideline','Climate','P_el_n [W]','P_th_max [W]','k1','k2','k3','k4', 'k5','k6','k7','k8','k9', 'Group']]

    filt1 = (table['k4'] > 0) & (table['Group']==2)
    table.loc[filt1, 'Group'] = 5
    table.loc[filt1, 'Modus'] = 'On-Off'
    table.to_csv('hplib.csv', encoding='utf-8', index=False)

def ImportKeymarkData():
    # read in keymark data from *.txt files in /input/txt/
    # save a dataframe to database_keymark.csv in folder /output/
    Modul=[]
    Manufacturer=[]
    Date=[]
    Refrigerant=[]
    Mass=[]
    Poff=[]
    Psb=[]
    Prated=[]
    SPLindoor=[]
    SPLoutdoor=[]
    Type=[]
    Climate=[]
    Guideline=[]
    T_in=[]
    T_out=[]
    P_th=[]
    COP=[]
    df=pd.DataFrame()
    root=os.getcwd()
    Scanordner=(root+'/input/txt')
    os.chdir(Scanordner)
    Scan = os.scandir(os.getcwd())
    with Scan as dir1:
        for file in dir1:
            with open (file, 'r',encoding='utf-8') as f:
                contents=f.readlines()
                date='NaN'
                modul='NaN'
                prated_low='NaN'
                prated_medium='NaN'
                heatpumpType='NaN'
                refrigerant='NaN'
                splindoor_low='NaN'
                splindoor_medium='NaN'
                sploutdoor_low='NaN'
                sploutdoor_medium='NaN'
                poff='NaN'
                climate='NaN'
                NumberOfTestsPerNorm=[]
                NumberOfTestsPerModule=[]
                i=1#indicator for the line wich is read
                d=0 #indicator if only medium Temperature is given
                p=0#-15° yes or no
                date=contents[1]
                date=date[61:]
                if(date=='17 Dec 2020\n'):
                    date='17.12.2020\n'
                if(date=='18 Dec 2020\n'):
                    date='18.12.2020\n'
                if(date.startswith('5 Mar 2021')):
                    date='05.03.2021\n'
                if(date.startswith('15 Feb 2021')):
                    date='15.02.2021\n'
                if(date.startswith('22 Feb 2021')):
                    date='22.02.2021\n'
                for lines in contents:
                    i=i+1
                    if(lines.startswith('Name\n')==1):
                        manufacturer = (contents[i])
                        if (manufacturer.find('(')>0):
                            manufacturer=manufacturer.split('(', 1)[1].split('\n')[0]
                        if manufacturer.endswith('GmbH\n'):
                            manufacturer=manufacturer[:-5]
                        if manufacturer.endswith('S.p.A.\n'):
                            manufacturer=manufacturer[:-6]
                        if manufacturer.endswith('s.p.a.\n'):
                            manufacturer=manufacturer[:-6]
                        if manufacturer.endswith('S.p.A\n'):
                            manufacturer=manufacturer[:-5]
                        if manufacturer.endswith('S.L.U.\n'):
                            manufacturer=manufacturer[:-6]
                        if manufacturer.endswith('s.r.o.\n'):
                            manufacturer=manufacturer[:-6]
                        if manufacturer.endswith('S.A.\n'):
                            manufacturer=manufacturer[:-4]
                        if manufacturer.endswith('S.L.\n'):
                            manufacturer=manufacturer[:-4]
                        if manufacturer.endswith('B.V.\n'):
                            manufacturer=manufacturer[:-4]
                        if manufacturer.endswith('N.V.\n'):
                            manufacturer=manufacturer[:-4]
                        if manufacturer.endswith('GmbH & Co KG\n'):
                            manufacturer=manufacturer[:-12]
                        elif manufacturer.startswith('NIBE'):
                            manufacturer='Nibe\n'
                        elif manufacturer.startswith('Nibe'):
                            manufacturer='Nibe\n'
                        elif manufacturer.startswith('Mitsubishi'):
                            manufacturer='Mitsubishi\n'
                        elif manufacturer.startswith('Ochsner'):
                            manufacturer='Ochsner\n'
                        elif manufacturer.startswith('OCHSNER'):
                            manufacturer='Ochsner\n' 
                        elif manufacturer.startswith('Viessmann'):
                            manufacturer='Viessmann\n'
                        
                    elif(lines.endswith('Date\n')==1):
                        date = (contents[i])
                        if (date=='basis\n'):
                            date = contents[i-3]
                            date = date[14:] 
                    elif(lines.startswith('Model')==1):
                        modul = (contents[i-2])
                        splindoor_low='NaN'
                        splindoor_medium='NaN'
                        sploutdoor_low='NaN'
                        sploutdoor_medium='NaN'
                    elif lines.endswith('Type\n'):
                        heatpumpType=contents[i][:-1]
                        if heatpumpType.startswith('A'):
                            heatpumpType= 'Outdoor Air/Water'
                        if heatpumpType.startswith('Eau glycol'):
                            heatpumpType= 'Brine/Water'
                    elif(lines.startswith('Sound power level indoor')):

                        SPL=1
                        if(contents[i].startswith('Low')):
                            if contents[i+2].startswith('Medium'):
                                splindoor_low= contents[i+4][:-7]
                                splindoor_medium= contents[i+6][:-7]
                        if contents[i].startswith('Medium'):
                            splindoor_medium=contents[i+4][:-7]
                            splindoor_low= contents[i+6][:-7]
                        elif(contents[i].endswith('dB(A)\n')):
                            if(contents[i-3].startswith('Low')):
                                splindoor_low=contents[i][:-7]
                            if(contents[i-3].startswith('Medium')):
                                splindoor_medium=contents[i][:-7]
                            if(contents[i-6].startswith('Low')):
                                splindoor_low=contents[i][:-7]
                            
                            if(contents[i-6].startswith('Medium')):
                                splindoor_medium=contents[i+2][:-7]
                            if(contents[i-4].startswith('Low')):
                                splindoor_low=contents[i][:-7]
                            if(contents[i-4].startswith('Medium')):
                                splindoor_medium=contents[i+2][:-7]
                            else:
                                splindoor_low=contents[i][:-7]
                                splindoor_medium=contents[i][:-7]

                    elif(lines.startswith('Sound power level outdoor')):
                        SPL=1
                        if(contents[i].startswith('Low')):
                            if contents[i+2].startswith('Medium'):
                                sploutdoor_low= contents[i+4][:-7]
                                sploutdoor_medium= contents[i+6][:-7]
                        if contents[i].startswith('Medium'):
                            sploutdoor_medium=contents[i+4][:-7]
                            sploutdoor_low= contents[i+6][:-7]
                        elif(contents[i].endswith('dB(A)\n')):
                            if(contents[i-3].startswith('Low')):
                                sploutdoor_low=contents[i][:-7]
                            if(contents[i-3].startswith('Medium')):
                                sploutdoor_medium=contents[i][:-7]
                            if(contents[i-6].startswith('Low')):
                                sploutdoor_low=contents[i][:-7]
                            if(contents[i-6].startswith('Medium')):
                                sploutdoor_medium=contents[i+2][:-7]
                            if(contents[i-4].startswith('Low')):
                                sploutdoor_low=contents[i][:-7]
                            if(contents[i-4].startswith('Medium')):
                                sploutdoor_medium=contents[i+2][:-7]
                            else:
                                sploutdoor_low=contents[i][:-7]
                                sploutdoor_medium=contents[i][:-7]

                    elif(lines.startswith('Puissance acoustique extérieure')):
                        b=1
                        if(contents[i].startswith('Low')):
                            if contents[i+2].startswith('Medium'):
                                sploutdoor_low= contents[i+4][:-7]
                                sploutdoor_medium= contents[i+6][:-7]
                        if contents[i].startswith('Medium'):
                            sploutdoor_medium=contents[i+4][:-7]
                            sploutdoor_low= contents[i+6][:-7]
                        elif(contents[i].endswith('dB(A)\n')):
                            if(contents[i-3].startswith('Low')):
                                sploutdoor_low=contents[i][:-7]
                            if(contents[i-3].startswith('Medium')):
                                sploutdoor_medium=contents[i][:-7]
                            if(contents[i-6].startswith('Low')):
                                sploutdoor_low=contents[i][:-7]
                            if(contents[i-6].startswith('Medium')):
                                sploutdoor_medium=contents[i+2][:-7]
                            if(contents[i-4].startswith('Low')):
                                sploutdoor_low=contents[i][:-7]
                            if(contents[i-4].startswith('Medium')):
                                sploutdoor_medium=contents[i+2][:-7]
                            else:
                                sploutdoor_low=contents[i][:-7]
                                sploutdoor_medium=contents[i][:-7]
                    elif(lines.startswith('Potencia sonora de la unidad interior')):
                        SPL=1
                        if(contents[i].startswith('Low')):
                            if contents[i+2].startswith('Medium'):
                                splindoor_low= contents[i+4][:-7]
                                splindoor_medium= contents[i+6][:-7]
                        if contents[i].startswith('Medium'):
                            splindoor_medium=contents[i+4][:-7]
                            splindoor_low= contents[i+6][:-7]
                        elif(contents[i].endswith('dB(A)\n')):
                            if(contents[i-3].startswith('Low')):
                                splindoor_low=contents[i][:-7]
                            if(contents[i-3].startswith('Medium')):
                                splindoor_medium=contents[i][:-7]
                            if(contents[i-6].startswith('Low')):
                                splindoor_low=contents[i][:-7]
                            if(contents[i-6].startswith('Medium')):
                                splindoor_medium=contents[i+2][:-7]
                            if(contents[i-4].startswith('Low')):
                                splindoor_low=contents[i][:-7]
                            if(contents[i-4].startswith('Medium')):
                                splindoor_medium=contents[i+2][:-7]
                            else:
                                splindoor_low=contents[i][:-7]
                                splindoor_medium=contents[i][:-7]
                    elif(lines.startswith('Potencia sonora de la unidad exterior')):
                        SPL=1
                        if(contents[i].startswith('Low')):
                            if contents[i+2].startswith('Medium'):
                                sploutdoor_low= contents[i+4][:-7]
                                sploutdoor_medium= contents[i+6][:-7]
                        if contents[i].startswith('Medium'):
                            sploutdoor_medium=contents[i+4][:-7]
                            sploutdoor_low= contents[i+6][:-7]
                        elif(contents[i].endswith('dB(A)\n')):
                            if(contents[i-3].startswith('Low')):
                                sploutdoor_low=contents[i][:-7]
                            if(contents[i-3].startswith('Medium')):
                                sploutdoor_medium=contents[i][:-7]
                            if(contents[i-6].startswith('Low')):
                                sploutdoor_low=contents[i][:-7]
                            if(contents[i-6].startswith('Medium')):
                                sploutdoor_medium=contents[i+2][:-7]
                            if(contents[i-4].startswith('Low')):
                                sploutdoor_low=contents[i][:-7]
                            if(contents[i-4].startswith('Medium')):
                                sploutdoor_medium=contents[i+2][:-7]
                            else:
                                sploutdoor_low=contents[i][:-7]
                                sploutdoor_medium=contents[i][:-7]
                    elif(lines.startswith('Nivel de Potência sonora interior')):
                        SPL=1
                        if(contents[i].startswith('Low')):
                            if contents[i+2].startswith('Medium'):
                                splindoor_low= contents[i+4][:-7]
                                splindoor_medium= contents[i+6][:-7]
                        if contents[i].startswith('Medium'):
                            splindoor_medium=contents[i+4][:-7]
                            splindoor_low= contents[i+6][:-7]
                        elif(contents[i].endswith('dB(A)\n')):
                            if(contents[i-3].startswith('Low')):
                                splindoor_low=contents[i][:-7]
                            if(contents[i-3].startswith('Medium')):
                                splindoor_medium=contents[i][:-7]
                            if(contents[i-6].startswith('Low')):
                                splindoor_low=contents[i][:-7]
                            if(contents[i-6].startswith('Medium')):
                                splindoor_medium=contents[i+2][:-7]
                            if(contents[i-4].startswith('Low')):
                                splindoor_low=contents[i][:-7]
                            if(contents[i-4].startswith('Medium')):
                                splindoor_medium=contents[i+2][:-7]
                            else:
                                splindoor_low=contents[i][:-7]
                                splindoor_medium=contents[i][:-7]
                    elif(lines.startswith('Nivel de Potência sonora exterior')):
                        SPL=1
                        if(contents[i].startswith('Low')):
                            if contents[i+2].startswith('Medium'):
                                sploutdoor_low= contents[i+4][:-7]
                                sploutdoor_medium= contents[i+6][:-7]
                        if contents[i].startswith('Medium'):
                            sploutdoor_medium=contents[i+4][:-7]
                            sploutdoor_low= contents[i+6][:-7]
                        elif(contents[i].endswith('dB(A)\n')):
                            if(contents[i-3].startswith('Low')):
                                sploutdoor_low=contents[i][:-7]
                            if(contents[i-3].startswith('Medium')):
                                sploutdoor_medium=contents[i][:-7]
                            if(contents[i-6].startswith('Low')):
                                sploutdoor_low=contents[i][:-7]
                            if(contents[i-6].startswith('Medium')):
                                sploutdoor_medium=contents[i+2][:-7]
                            if(contents[i-4].startswith('Low')):
                                sploutdoor_low=contents[i][:-7]
                            if(contents[i-4].startswith('Medium')):
                                sploutdoor_medium=contents[i+2][:-7]
                            else:
                                sploutdoor_low=contents[i][:-7]
                                sploutdoor_medium=contents[i][:-7]
                    elif(lines.startswith('Livello di potenza acustica interna')):
                        SPL=1
                        if(contents[i].startswith('Low')):
                            if contents[i+2].startswith('Medium'):
                                splindoor_low= contents[i+4][:-7]
                                splindoor_medium= contents[i+6][:-7]
                        if contents[i].startswith('Medium'):
                            splindoor_medium=contents[i+4][:-7]
                            splindoor_low= contents[i+6][:-7]
                        elif(contents[i].endswith('dB(A)\n')):
                            if(contents[i-3].startswith('Low')):
                                splindoor_low=contents[i][:-7]
                            if(contents[i-3].startswith('Medium')):
                                splindoor_medium=contents[i][:-7]
                            if(contents[i-6].startswith('Low')):
                                splindoor_low=contents[i][:-7]
                            if(contents[i-6].startswith('Medium')):
                                splindoor_medium=contents[i+2][:-7]
                            if(contents[i-4].startswith('Low')):
                                splindoor_low=contents[i][:-7]
                            if(contents[i-4].startswith('Medium')):
                                splindoor_medium=contents[i+2][:-7]
                            else:
                                splindoor_low=contents[i][:-7]
                                splindoor_medium=contents[i][:-7]
                    elif(lines.startswith('Livello di potenza acustica externa')):
                        SPL=1
                        if(contents[i].startswith('Low')):
                            if contents[i+2].startswith('Medium'):
                                sploutdoor_low= contents[i+4][:-7]
                                sploutdoor_medium= contents[i+6][:-7]
                        if contents[i].startswith('Medium'):
                            sploutdoor_medium=contents[i+4][:-7]
                            sploutdoor_low= contents[i+6][:-7]
                        elif(contents[i].endswith('dB(A)\n')):
                            if(contents[i-3].startswith('Low')):
                                sploutdoor_low=contents[i][:-7]
                            if(contents[i-3].startswith('Medium')):
                                sploutdoor_medium=contents[i][:-7]
                            if(contents[i-6].startswith('Low')):
                                sploutdoor_low=contents[i][:-7]
                            if(contents[i-6].startswith('Medium')):
                                sploutdoor_medium=contents[i+2][:-7]
                            if(contents[i-4].startswith('Low')):
                                sploutdoor_low=contents[i][:-7]
                            if(contents[i-4].startswith('Medium')):
                                sploutdoor_medium=contents[i+2][:-7]
                            else:
                                sploutdoor_low=contents[i][:-7]
                                sploutdoor_medium=contents[i][:-7]
                    elif(lines=='Refrigerant\n'):
                        if(contents[i-3]=='Mass Of\n'):
                            continue
                        refrigerant = (contents[i])
                    elif(lines.startswith('Mass Of')==1):
                        if (lines=='Mass Of\n'):
                            mass=contents[i+1]
                        elif(lines.endswith('kg\n')==1):
                            mass=contents[i-2]
                            mass=mass[20:]
                        else:
                            mass=contents[i]
                    
                    elif lines.startswith('Average'):
                        climate='average'
                    elif lines.startswith('Cold'):
                        climate='cold'
                    elif lines.startswith('Warmer Climate'):
                        climate='warm'
                        
                    elif(lines.startswith('EN')==1):
                        if(p==1):
                            Poff.append(poff)
                            Psb.append(psb)
                        if(p==2):
                            Poff.append(poff)
                            Poff.append(poff)
                            Psb.append(psb)
                            Psb.append(psb_medium)
                        guideline=(contents[i-2])
                        d=0 #Medium or Low Content
                        p=0 #-15 yes or no
                        
                        
                        NumberOfTestsPerNorm=[]
                        if(contents[i-1].startswith('Low')==1):
                            d=0
                            continue
                        if(contents[i-1]=='\n'):

                            continue
                        if(contents[i-1].startswith('Medium')):
                            d=1
                        else: 
                            d=0
                    if lines.startswith('Prated'):
                        prated_low=contents[i][:-4]
                        if(contents[i+2].endswith('kW\n')):
                            prated_medium=contents[i+2][:-4]                        


                    elif(lines.startswith('Pdh Tj = -15°C')==1): #check
                        if(contents[i].endswith('Cdh\n')==1):#wrong content
                            continue
                        if(contents[i]=='\n'):#no content
                            continue                        
                        else:
                            minusfifteen_low=contents[i]
                            P_th.append(minusfifteen_low[:-4])
                            T_in.append('-15')
                            if d==0:#first low than medium Temperatur
                                if(climate=='average'):
                                    T_out.append('35')
                                elif(climate=='cold'):
                                    T_out.append('32')
                                elif(climate=='warm'):
                                    T_out.append('35')

                            if d==1:#first medium Temperature
                                if(climate=='average'):
                                    T_out.append('55')
                                elif(climate=='cold'):
                                    T_out.append('49')
                                elif(climate=='warm'):
                                    T_out.append('55')
                            
                                
                            Modul.append(modul[7:-1])
                            Manufacturer.append(manufacturer[:-1])
                            Date.append(date[:-1])
                            Refrigerant.append(refrigerant[:-1])
                            Mass.append(mass[:-4])
                            Prated.append(prated_low)
                            SPLindoor.append(splindoor_low)
                            #SPLindoor.append(splindoor_medium)
                            SPLoutdoor.append(sploutdoor_low)
                            #SPLoutdoor.append(sploutdoor_medium)
                            Guideline.append(guideline[:-1])
                            Climate.append(climate)
                            
                            Type.append(heatpumpType)
                            if(contents[i+2].startswith('COP')): #for PDF without medium heat
                                continue
                            if(contents[i+2].startswith('Disclaimer')): #for PDF without medium heat
                                continue
                            if(contents[i+2].startswith('EHPA')):#End of page
                                if(contents[i+8].startswith('COP')):#end of page plus no medium heat
                                    continue
                            minusfifteen_medium=contents[i+2]

                            P_th.append(minusfifteen_medium[:-4])
                            T_in.append('-15')
                            if(climate=='average'):
                                T_out.append('55')
                            elif(climate=='cold'):
                                T_out.append('49')
                            elif(climate=='warm'):
                                T_out.append('55')
                            Modul.append(modul[7:-1])
                            Manufacturer.append(manufacturer[:-1])
                            Date.append(date[:-1])
                            Refrigerant.append(refrigerant[:-1])
                            Mass.append(mass[:-4])
                            Prated.append(prated_medium)
                            #SPLindoor.append(splindoor_low)
                            SPLindoor.append(splindoor_medium)
                            #SPLoutdoor.append(sploutdoor_low)
                            SPLoutdoor.append(sploutdoor_medium)
                            Type.append(heatpumpType)
                            Guideline.append(guideline[:-1])
                            Climate.append(climate)
                            
                    elif(lines.startswith('COP Tj = -15°C')):
                        if(contents[i]=='\n'):
                            continue
                        if(contents[i].startswith('EHPA')):
                            continue
                        COP.append(contents[i][:-1])
                        NumberOfTestsPerModule.append(i)
                        p=1

                
                        if(contents[i+2].startswith('Pdh')):#no medium Climate
                            continue
                        if(contents[i+2].startswith('Cdh')):#no medium Climate
                            continue
                        if(contents[i+2].startswith('EHPA')):#no medium Climate
                            continue
                        COP.append(contents[i+2][:-1])
                        NumberOfTestsPerModule.append(i)
                        p=2


                    elif(lines.startswith('Pdh Tj = -7°C')==1):#check
                        minusseven_low=contents[i]
                        P_th.append(minusseven_low[:-4])
                        T_in.append('-7')
                        if d==0:#first low than medium Temperatur
                            if(climate=='average'):
                                T_out.append('34')
                            elif(climate=='cold'):
                                T_out.append('30')
                            elif(climate=='warm'):
                                T_out.append('35')

                        if d==1:#first medium Temperature
                            if(climate=='average'):
                                T_out.append('52')
                            elif(climate=='cold'):
                                T_out.append('44')
                            elif(climate=='warm'):
                                T_out.append('55')                    

                        Modul.append(modul[7:-1])
                        Manufacturer.append(manufacturer[:-1])
                        Date.append(date[:-1])
                        Refrigerant.append(refrigerant[:-1])
                        Mass.append(mass[:-4])
                        Prated.append(prated_low)
                        SPLindoor.append(splindoor_low)
                        #SPLindoor.append(splindoor_medium)
                        SPLoutdoor.append(sploutdoor_low)
                        #SPLoutdoor.append(sploutdoor_medium)
                        Type.append(heatpumpType)
                        Guideline.append(guideline[:-1])
                        Climate.append(climate)
                        
                        if(contents[i+2].startswith('COP')==1):
                            continue
                        else:
                            minusseven_medium=contents[i+2]
                            P_th.append(minusseven_medium[:-4])
                            T_in.append('-7')
                            if(climate=='average'):
                                T_out.append('52')
                            elif(climate=='cold'):
                                T_out.append('44')
                            elif(climate=='warm'):
                                T_out.append('55')
                            Modul.append(modul[7:-1])
                            Manufacturer.append(manufacturer[:-1])
                            Date.append(date[:-1])
                            Refrigerant.append(refrigerant[:-1])
                            #SPLindoor.append(splindoor_low)
                            SPLindoor.append(splindoor_medium)
                            #SPLoutdoor.append(sploutdoor_low)
                            SPLoutdoor.append(sploutdoor_medium)
                            Mass.append(mass[:-4])
                            Prated.append(prated_medium)
                            Type.append(heatpumpType)
                            Guideline.append(guideline[:-1])
                            Climate.append(climate)
                            
                    elif(lines.startswith('COP Tj = -7°C')):
                        COP.append(contents[i][:-1])
                        NumberOfTestsPerNorm.append(i)
                        NumberOfTestsPerModule.append(i)
                        if(contents[i+2].startswith('Pdh')):#no medium Climate
                            continue
                        if(contents[i+2].startswith('Cdh')):#no medium Climate
                            continue
                        COP.append(contents[i+2][:-1])
                        NumberOfTestsPerNorm.append(i)
                        NumberOfTestsPerModule.append(i)


                    elif(lines.startswith('Pdh Tj = +2°C')==1): 
                        if(contents[i].endswith('Cdh\n')==1):#wrong content
                            continue
                        if(contents[i]=='\n'):#no content
                            continue                        
                        else:
                            plustwo_low=contents[i]
                            P_th.append(plustwo_low[:-4])
                            T_in.append('2')
                            if d==0:#first low than medium Temperatur
                                if(climate=='average'):
                                    T_out.append('30')
                                elif(climate=='cold'):
                                    T_out.append('27')
                                elif(climate=='warm'):
                                    T_out.append('35')

                            if d==1:#first medium Temperature
                                if(climate=='average'):
                                    T_out.append('42')
                                elif(climate=='cold'):
                                    T_out.append('37')
                                elif(climate=='warm'):
                                    T_out.append('55')
                            Modul.append(modul[7:-1])
                            Manufacturer.append(manufacturer[:-1])
                            Date.append(date[:-1])
                            Refrigerant.append(refrigerant[:-1])
                            SPLindoor.append(splindoor_low)
                            #SPLindoor.append(splindoor_medium)
                            SPLoutdoor.append(sploutdoor_low)
                            #SPLoutdoor.append(sploutdoor_medium)
                            Mass.append(mass[:-4])
                            Prated.append(prated_low)
                            Type.append(heatpumpType)
                            Guideline.append(guideline[:-1])
                            Climate.append(climate)
                            
                            if(contents[i+2].startswith('COP')): #for PDF without medium heat
                                continue
                            if(contents[i+2].startswith('Disclaimer')): #for PDF without medium heat
                                continue
                            if(contents[i+2].startswith('EHPA')):#End of page
                                if(contents[i+8].startswith('COP')):#end of page plus no medium heat
                                    continue
                            plustwo_medium=contents[i+2]
                            #if(plustwo_low[:-1].endswith('kW')==0):#test
                                #print(plustwo_low[:-1])
                            #if(plustwo_medium[:-1].endswith('kW')==0):#test
                                #print(file.name)#plustwo_medium[:-1]

                            P_th.append(plustwo_medium[:-4])
                            T_in.append('2')
                            if(climate=='average'):
                                T_out.append('42')
                            elif(climate=='cold'):
                                T_out.append('37')
                            elif(climate=='warm'):
                                T_out.append('55')
                            Modul.append(modul[7:-1])
                            Manufacturer.append(manufacturer[:-1])
                            Date.append(date[:-1])
                            Refrigerant.append(refrigerant[:-1])
                            #SPLindoor.append(splindoor_low)
                            SPLindoor.append(splindoor_medium)
                            #SPLoutdoor.append(sploutdoor_low)
                            SPLoutdoor.append(sploutdoor_medium)
                            Mass.append(mass[:-4])
                            Prated.append(prated_medium)
                            Type.append(heatpumpType)
                            Guideline.append(guideline[:-1])
                            Climate.append(climate)
                            
                    elif(lines.startswith('COP Tj = +2°C')):#check
                        if(contents[i]=='\n'):#no infos
                            continue
                        if(contents[i].startswith('EHPA')):#end of page
                            print(file.name)
                            continue
                        if(contents[i+2].startswith('Warmer')):#usless infos
                            continue
                        if(contents[i]=='n/a\n'):#usless infos
                            continue
                        COP.append(contents[i][:-1])
                        NumberOfTestsPerNorm.append(i)
                        NumberOfTestsPerModule.append(i)

                        if(contents[i+2].startswith('Pdh')):#no medium Climate
                            continue
                        if(contents[i+2].startswith('Cdh')):#no medium Climate
                            continue
                        if(contents[i+2].startswith('EHPA')):#no medium Climate
                            continue
                        COP.append(contents[i+2][:-1])
                        NumberOfTestsPerNorm.append(i)
                        NumberOfTestsPerModule.append(i)


                    elif(lines.startswith('Pdh Tj = +7°C')==1):
                        if(contents[i].endswith('Cdh\n')==1):#wrong content
                            continue
                        if(contents[i]=='\n'):#no content
                            continue                        
                        else:
                            plusseven_low=contents[i]
                            P_th.append(plusseven_low[:-4])
                            T_in.append('7')
                            if d==0:#first low than medium Temperatur
                                if(climate=='average'):
                                    T_out.append('27')
                                elif(climate=='cold'):
                                    T_out.append('25')
                                elif(climate=='warm'):
                                    T_out.append('31')

                            if d==1:#first medium Temperature
                                if(climate=='average'):
                                    T_out.append('36')
                                elif(climate=='cold'):
                                    T_out.append('32')
                                elif(climate=='warm'):
                                    T_out.append('46')
                            Modul.append(modul[7:-1])
                            Manufacturer.append(manufacturer[:-1])
                            Date.append(date[:-1])
                            Refrigerant.append(refrigerant[:-1])
                            SPLindoor.append(splindoor_low)
                            #SPLindoor.append(splindoor_medium)
                            SPLoutdoor.append(sploutdoor_low)
                            #SPLoutdoor.append(sploutdoor_medium)
                            Mass.append(mass[:-4])
                            Prated.append(prated_low)
                            Type.append(heatpumpType)
                            Guideline.append(guideline[:-1])
                            Climate.append(climate)
                            
                            if(contents[i+2].startswith('COP')): #for PDF without medium heat
                                continue
                            if(contents[i+2].startswith('Disclaimer')): #for PDF without medium heat
                                continue
                            if(contents[i+2].startswith('EHPA')):#End of page
                                if(contents[i+8].startswith('COP')):#end of page plus no medium heat
                                    continue
                            plusseven_medium=contents[i+2]

                            P_th.append(plusseven_medium[:-4])
                            T_in.append('7')
                            if(climate=='average'):
                                T_out.append('36')
                            elif(climate=='cold'):
                                T_out.append('32')
                            elif(climate=='warm'):
                                T_out.append('46')
                            
                            Modul.append(modul[7:-1])
                            Manufacturer.append(manufacturer[:-1])
                            Date.append(date[:-1])
                            Refrigerant.append(refrigerant[:-1])
                            #SPLindoor.append(splindoor_low)
                            SPLindoor.append(splindoor_medium)
                            #SPLoutdoor.append(sploutdoor_low)
                            SPLoutdoor.append(sploutdoor_medium)
                            Mass.append(mass[:-4])
                            Prated.append(prated_medium)
                            Type.append(heatpumpType)
                            Guideline.append(guideline[:-1])
                            Climate.append(climate)
                            
                    elif(lines.startswith('COP Tj = +7°C')):#check
                        if(contents[i]=='\n'):#no infos
                            continue
                        if(contents[i].startswith('EHPA')):#end of page
                            continue
                        if(contents[i+2].startswith('Warmer')):#usless infos
                            continue
                        if(contents[i]=='n/a\n'):#usless infos
                            continue
                        COP.append(contents[i][:-1])
                        NumberOfTestsPerNorm.append(i)
                        NumberOfTestsPerModule.append(i)

                        if(contents[i+2].startswith('Pdh')):#no medium Climate
                            continue
                        if(contents[i+2].startswith('Cdh')):#no medium Climate
                            continue
                        if(contents[i+2].startswith('EHPA')):#no medium Climate
                            continue
                        COP.append(contents[i+2][:-1])
                        NumberOfTestsPerNorm.append(i)
                        NumberOfTestsPerModule.append(i)


                    elif(lines.startswith('Pdh Tj = 12°C')==1):
                        
                        if(contents[i].endswith('Cdh\n')==1):#wrong content
                            continue
                        if(contents[i]=='\n'):#no content
                            continue  
                        if (contents[i].startswith('EHPA Secretariat')==1):
                            plustwelfe_low=(contents[i-11])
                            
                            P_th.append(plustwelfe_low[:-4])
                            T_in.append('12')
                            if(climate=='average'):
                                T_out.append('24')
                            elif(climate=='cold'):
                                T_out.append('24')
                            elif(climate=='warm'):
                                T_out.append('26')
                            Modul.append(modul[7:-1])
                            Manufacturer.append(manufacturer[:-1])
                            Date.append(date[:-1])
                            Refrigerant.append(refrigerant[:-1])
                            SPLindoor.append(splindoor_low)
                            #SPLindoor.append(splindoor_medium)
                            SPLoutdoor.append(sploutdoor_low)
                            #SPLoutdoor.append(sploutdoor_medium)
                            Mass.append(mass[:-4])
                            Prated.append(prated_low)
                            Type.append(heatpumpType)
                            Guideline.append(guideline[:-1])
                            Climate.append(climate)
                            
                            plustwelfe_medium=(contents[i-9])
                            
                            P_th.append(plustwelfe_medium[:-4])
                            T_in.append('12')
                            if(climate=='average'):
                                T_out.append('30')
                            elif(climate=='cold'):
                                T_out.append('28')
                            elif(climate=='warm'):
                                T_out.append('34')
                            Modul.append(modul[7:-1])
                            Manufacturer.append(manufacturer[:-1])
                            Date.append(date[:-1])
                            Refrigerant.append(refrigerant[:-1])
                            #SPLindoor.append(splindoor_low)
                            SPLindoor.append(splindoor_medium)
                            #SPLoutdoor.append(sploutdoor_low)
                            SPLoutdoor.append(sploutdoor_medium)
                            Mass.append(mass[:-4])
                            Prated.append(prated_medium)
                            Type.append(heatpumpType)
                            Guideline.append(guideline[:-1])
                            Climate.append(climate)  
                                                
                        else:
                            plustwelfe_low=contents[i]
                            
                            P_th.append(plustwelfe_low[:-4])
                            T_in.append('12')
                            if d==0:#first low than medium Temperatur
                                if(climate=='average'):
                                    T_out.append('24')
                                elif(climate=='cold'):
                                    T_out.append('24')
                                elif(climate=='warm'):
                                    T_out.append('26')

                            if d==1:#first medium Temperature
                                if(climate=='average'):
                                    T_out.append('30')
                                elif(climate=='cold'):
                                    T_out.append('28')
                                elif(climate=='warm'):
                                    T_out.append('34')
                            Modul.append(modul[7:-1])
                            Manufacturer.append(manufacturer[:-1])
                            Date.append(date[:-1])
                            Refrigerant.append(refrigerant[:-1])
                            SPLindoor.append(splindoor_low)
                            
                            SPLoutdoor.append(sploutdoor_low)
                            
                            Mass.append(mass[:-4])
                            Prated.append(prated_low)
                            Type.append(heatpumpType)
                            Guideline.append(guideline[:-1])
                            Climate.append(climate)
                            
                            if(contents[i+2].startswith('COP')): #for PDF without medium heat
                                continue
                            if(contents[i+2].startswith('Disclaimer')): #for PDF without medium heat
                                continue
                            if(contents[i+2].startswith('EHPA')):#End of page
                                if(contents[i+8].startswith('COP')):#end of page plus no medium heat
                                    continue
                            

                            plustwelfe_medium=contents[i+2]
                            P_th.append(plustwelfe_medium[:-4])
                            T_in.append('12')
                            if(climate=='average'):
                                T_out.append('30')
                            elif(climate=='cold'):
                                T_out.append('28')
                            elif(climate=='warm'):
                                T_out.append('34')
                            Modul.append(modul[7:-1])
                            Manufacturer.append(manufacturer[:-1])
                            Date.append(date[:-1])
                            Refrigerant.append(refrigerant[:-1])
                            #SPLindoor.append(splindoor_low)
                            SPLindoor.append(splindoor_medium)
                            
                            SPLoutdoor.append(sploutdoor_medium)
                            Mass.append(mass[:-4])
                            Prated.append(prated_medium)
                            Type.append(heatpumpType)
                            Guideline.append(guideline[:-1])
                            Climate.append(climate)
                            
                    elif(lines.startswith('COP Tj = 12°C')):#check
                        if(contents[i]=='\n'):#no infos
                            continue
                        if(contents[i].startswith('EHPA')):#end of page
                            print('W')
                            continue
                        if(contents[i+2].startswith('Warmer')):#usless infos
                            continue
                        if(contents[i]=='n/a\n'):#usless infos
                            continue
                        COP.append(contents[i][:-1])
                        NumberOfTestsPerNorm.append(i)
                        NumberOfTestsPerModule.append(i)

                        if(contents[i+2].startswith('Pdh')):#no medium Climate
                            continue
                        if(contents[i+2].startswith('Cdh')):#no medium Climate
                            continue
                        if(contents[i+2].startswith('EHPA')):#no medium Climate
                            continue
                        COP.append(contents[i+2][:-1])
                        NumberOfTestsPerNorm.append(i)
                        NumberOfTestsPerModule.append(i)


                    elif(lines.startswith('Poff')):
                        l=0 #l shows if Poff Medium is different to Poff Low Temperature
                        c=2 # c is just an iterator to print every second Poff
                        poff=contents[i][:-2]
                        if poff.endswith(' '):
                            poff=poff[:-1]
                            if poff.endswith('.00'):
                                poff=poff[:-3]
                        second_poff=contents[i+2][:-2]
                        if second_poff.endswith(' '):
                            second_poff=second_poff[:-1]
                            if second_poff.endswith('.00'):
                                second_poff=second_poff[:-3]
                        if(poff!=second_poff): #see if Poff Medium to Poff low
                            if(contents[i+2].endswith('W\n')):
                                if (contents[i+2]!='W\n'):
                                    l=1
                        for Tests in NumberOfTestsPerNorm:
                            if l==0:
                                Poff.append(poff)
                            if l==1:
                                c+=1
                                if c%2==1:
                                    Poff.append(poff)
                                if c%2==0:
                                    Poff.append(second_poff)
                    elif(lines.startswith('PSB')):
                        l=0 #l shows if Poff Medium is different to Poff Low Temperature
                        c=2 # c is just an iterator to print every second Poff
                        psb=contents[i][:-2]
                        if psb.endswith(' '):
                            psb=psb[:-1]
                            if psb.endswith('.00'):
                                psb=psb[:-3]
                        psb_medium=contents[i+2][:-2]
                        if psb_medium.endswith(' '):
                            psb_medium=psb_medium[:-1]
                            if psb_medium.endswith('.00'):
                                psb_medium=psb_medium[:-3]
                        if(psb!=psb_medium): #see if Poff Medium to Poff low
                            if(contents[i+2].endswith('W\n')):
                                if (contents[i+2]!='W\n'):
                                    l=1
                        

                        for Tests in NumberOfTestsPerNorm:
                            if l==0:
                                Psb.append(psb)
                            if l==1:
                                c+=1
                                if c%2==1:
                                    Psb.append(psb)
                                if c%2==0:
                                    Psb.append(psb_medium)

                if p==1:
                    Poff.append(poff)
                    Psb.append(psb)
                if p==2:
                    Poff.append(poff)
                    Poff.append(second_poff)
                    Psb.append(psb)
                    Psb.append(psb_medium) 

    df['Manufacturer']=Manufacturer
    df['Model']=Modul                 
    df['Date']=Date
    df['Date'] = pd.to_datetime(df['Date'], format='%d.%m.%Y')
    df['Type']=Type
    df['SPL indoor [dBA]']=SPLindoor
    df['SPL outdoor [dBA]']=SPLoutdoor
    df['Refrigerant']=Refrigerant
    df['Mass of Refrigerant [kg]']=Mass
    df['Poff [W]']= Poff
    df['Poff [W]']=df['Poff [W]'].astype(int)
    df['PSB [W]']=Psb
    df['PSB [W]']=df['PSB [W]'].astype(int)
    df['Prated [W]']=Prated

    df['Guideline']=Guideline
    df['Climate']=Climate
    df['T_in [°C]']=T_in
    df['T_in [°C]']=df['T_in [°C]'].astype(int)
    df['T_out [°C]']=T_out
    df['T_out [°C]']=df['T_out [°C]'].astype(int)
    """  
    T_out for Low Temperature
            T-in:   -15 -7  2   7   12

    Cold Climate    32  30  27  25  24
    Average Climate 35  34  30  27  24
    Warm Climate    35  35  35  31  26    


    T_out for Medium Temperature
            T-in:   -15 -7  2   7   12

    Cold Climate    49  44  37  32  28
    Average Climate 55  52  42  36  30
    Warm Climate    55  55  55  46  34                    
    """
    df['P_th [W]']=P_th
    df['P_th [W]']=((df['P_th [W]'].astype(float))*1000).astype(int)
    df['COP']=COP
    df['COP']=round(df['COP'].astype(float),2)
    df['P_el [W]']=round(df['P_th [W]'] / df['COP'])
    df['P_el [W]']=df['P_el [W]'].fillna(0).astype(int)
    df['PSB [W]']=df['PSB [W]'].where(df['PSB [W]'] > df['Poff [W]'], df['Poff [W]']) #Poff should not be bigger than PSB
    df.drop(columns=['Poff [W]'], inplace=True) #not needed anymore
    filt=df['P_th [W]']<50    #P_th too small 
    df.drop(index=df[filt].index , inplace=True) 
    os.chdir("..")
    os.chdir("..")
    df.to_csv(os.getcwd()+r'/output/database_keymark.csv', index=False)
