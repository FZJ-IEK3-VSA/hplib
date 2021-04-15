import os
import pandas as pd

Modul=[]
Manufacturer=[]
Date=[]
Refrigerant=[]
Mass=[]
Type=[]
Pdesignc=[]
Temperatur=[]
T_outside=[]
PDC=[]
EER=[]
df=pd.DataFrame()
Scanordner=(os.path.dirname(__file__)+r'\input\txt')
os.chdir(Scanordner)
Scan = os.scandir(os.getcwd())
with Scan as dir1:
    for file in dir1:
        with open (file, 'r',encoding='utf-8') as f:
            contents=f.readlines()
            T=0
            i=1#indicator for the line wich is read
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
                    manufacturer = (contents[i][:-1])
                    if (manufacturer.find('(')>0):
                        manufacturer=manufacturer.split('(', 1)[1].split(')')[0]
                    elif manufacturer.startswith('NIBE'):
                        manufacturer='Nibe'
                    elif manufacturer.startswith('Nibe'):
                        manufacturer='Nibe'
                    elif manufacturer.startswith('Mitsubishi'):
                        manufacturer='Mitsubishi'
                    elif manufacturer.startswith('Ochsner'):
                        manufacturer='Ochsner'
                    elif manufacturer.startswith('OCHSNER'):
                        manufacturer='Ochsner' 
                    elif manufacturer.startswith('Viessmann'):
                        manufacturer='Viessmann'   
                elif(lines.endswith('Date\n')==1):
                    date = (contents[i])
                    if (date=='basis\n'):
                        date = contents[i-3]
                        date = date[14:] 
                elif(lines.startswith('Model')==1):
                    modul = (contents[i-2][7:-1])
                    temperatur2=''
                elif lines.endswith('Type\n'):
                    heatpumpType=contents[i][:-1]
                    if heatpumpType.startswith('A'):
                        heatpumpType= 'Outdoor Air/Water'
                    if heatpumpType.startswith('Eau glycol'):
                        heatpumpType= 'Brine/Water'
                elif(lines=='Refrigerant\n'):
                    if(contents[i-3]=='Mass Of\n'):
                        continue
                    refrigerant = (contents[i][:-1])
                elif(lines.startswith('Mass Of')==1):
                    if (lines=='Mass Of\n'):
                        mass=contents[i+1][:-4]
                    elif(lines.endswith('kg\n')==1):
                        mass=contents[i-2]
                        mass=mass[20:-4]
                    else:
                        mass=contents[i][:-4]


                elif lines.startswith('+'):
                    if T==0:
                        temperatur1=contents[i-2][:-1]
                        if(contents[i].startswith('+')):
                            temperatur2=contents[i][:-1]
                            T=1
                            temperatur2=(temperatur2[1:3])
                        temperatur1=(temperatur1[1:2])
                    else:
                        T=0
                elif lines.startswith('Pdesignc'):
                    pdesignc1=contents[i][:-4]
                    if temperatur2!='':
                        pdesignc2=contents[i+2][:-4]

                elif lines.startswith('Pdc Tj = 30°C'):
                    pdcT1_30=contents[i][:-4]
                    
                    if contents[i+2].endswith('W\n'):
                        pdcT2_30= contents[i+2][:-4]
            
                        
                elif lines.startswith('EER Tj = 30°C'):
                    
                    eerT1_30=(contents[i][:-1])
                    EER.append(eerT1_30)
                    PDC.append(pdcT1_30)
                    T_outside.append('30')
                    Pdesignc.append(pdesignc1)
                    Temperatur.append(temperatur1)
                    Modul.append(modul)
                    Manufacturer.append(manufacturer)
                    Date.append(date)
                    Refrigerant.append(refrigerant)
                    Mass.append(mass)
                    Type.append(heatpumpType)
                    
                    if temperatur2!='':
                        eerT2_30=contents[i+2][:-1]
                        EER.append(eerT2_30)
                        PDC.append(pdcT2_30)
                        T_outside.append('30')
                        Pdesignc.append(pdesignc2)
                        Temperatur.append(temperatur2)
                        Modul.append(modul)
                        Manufacturer.append(manufacturer)
                        Date.append(date)
                        Refrigerant.append(refrigerant)
                        Mass.append(mass)
                        Type.append(heatpumpType)
        
                elif lines.startswith('Pdc Tj = 35°C'):
                    pdcT1_35=contents[i][:-4]
                    if contents[i+2].endswith('W\n'):
                        pdcT2_35= contents[i+2][:-4]
                        
                elif lines.startswith('EER Tj = 35°C'):
                    eerT1_35=(contents[i][:-1])
                    EER.append(eerT1_35)
                    PDC.append(pdcT1_35)
                    T_outside.append('35')
                    Pdesignc.append(pdesignc1)
                    Temperatur.append(temperatur1)
                    Modul.append(modul)
                    Manufacturer.append(manufacturer)
                    Date.append(date)
                    Refrigerant.append(refrigerant)
                    Mass.append(mass)
                    Type.append(heatpumpType)
                    if temperatur2!='':
                        eerT2_35=contents[i+2][:-1]
                        EER.append(eerT2_35)
                        PDC.append(pdcT2_35)
                        T_outside.append('35')
                        Pdesignc.append(pdesignc2)
                        Temperatur.append(temperatur2)
                        Modul.append(modul)
                        Manufacturer.append(manufacturer)
                        Date.append(date)
                        Refrigerant.append(refrigerant)
                        Mass.append(mass)
                        Type.append(heatpumpType)
                elif lines.startswith('Pdc Tj = 25°C'):
                    pdcT1_25=contents[i][:-4]
                    if contents[i+2].endswith('W\n'):
                        pdcT2_25= contents[i+2][:-4]
                        
                elif lines.startswith('EER Tj = 25°C'):
                    eerT1_25=(contents[i][:-1])
                    EER.append(eerT1_25)
                    PDC.append(pdcT1_25)
                    T_outside.append('25')
                    Pdesignc.append(pdesignc1)
                    Temperatur.append(temperatur1)
                    Modul.append(modul)
                    Manufacturer.append(manufacturer)
                    Date.append(date)
                    Refrigerant.append(refrigerant)
                    Mass.append(mass)
                    Type.append(heatpumpType)
                    if temperatur2!='':
                        eerT2_25=contents[i+2][:-1]
                        EER.append(eerT2_25)
                        PDC.append(pdcT2_25)
                        T_outside.append('25')
                        Pdesignc.append(pdesignc2)
                        Temperatur.append(temperatur2)
                        Modul.append(modul)
                        Manufacturer.append(manufacturer)
                        Date.append(date)
                        Refrigerant.append(refrigerant)
                        Mass.append(mass)
                        Type.append(heatpumpType)

                elif lines.startswith('Pdc Tj = 20°C'):
                    pdcT1_20=contents[i][:-4]
                    if contents[i+2].endswith('W\n'):
                        pdcT2_20= contents[i+2][:-4]
                        
                elif lines.startswith('EER Tj = 20°C'):
                    eerT1_20=(contents[i][:-1])
                    EER.append(eerT1_20)
                    PDC.append(pdcT1_20)
                    T_outside.append('20')
                    Pdesignc.append(pdesignc1)
                    Temperatur.append(temperatur1)
                    Modul.append(modul)
                    Manufacturer.append(manufacturer)
                    Date.append(date)
                    Refrigerant.append(refrigerant)
                    Mass.append(mass)
                    Type.append(heatpumpType)
                    if temperatur2!='':
                        eerT2_20=contents[i+2][:-1]
                        EER.append(eerT2_20)
                        PDC.append(pdcT2_20)
                        T_outside.append('20')
                        Pdesignc.append(pdesignc2)
                        Temperatur.append(temperatur2)
                        Modul.append(modul)
                        Manufacturer.append(manufacturer)
                        Date.append(date)
                        Refrigerant.append(refrigerant)
                        Mass.append(mass)
                        Type.append(heatpumpType)
df['Manufacturer']=Manufacturer
df['Model']=Modul                 
df['Date']=Date
df['Date'] = pd.to_datetime(df['Date'], format='%d.%m.%Y\n')
df['Type']=Type
df['Refrigerant']=Refrigerant
df['Mass of Refrigerant [kg]']=Mass
df['Pdesignc']=Pdesignc
df['T_outside [°C]']=T_outside
df['T_out [°C]']=Temperatur 

df['Pdc [kW]']=PDC
df['EER']=EER

filt=df['EER']=='Cdc'    #P_th too small 
df.drop(index=df[filt].index , inplace=True)
filt=df['EER']=='Pdc Tj = 30°C'    #P_th too small 
df.drop(index=df[filt].index , inplace=True)
df.to_csv(os.path.dirname(__file__)+r'/hplib-database_cooling.csv', index=False)