import os
import pandas as pd

Modul=[]
Manufacturer=[]
Date=[]
Refrigerant=[]
Mass=[]
Poff=[]
Psb=[]
SPLind=[]
SPLoutdoor=[]
Type=[]
Mode=[]
Climate=[]
Guideline=[]
T_in=[]
T_out=[]

P_th=[]
COP=[]
df=pd.DataFrame()
Scanordner=(os.path.dirname(__file__)+r'\input\txt')
os.chdir(Scanordner)
Scan = os.scandir(os.getcwd())
with Scan as dir1:
    for file in dir1:
        with open (file, 'r',encoding='utf-8') as f:
            contents=f.readlines()
            
            date=''
            modul=''
            heatpumpType=''
            refrigerant=''
            poff=''
            climate=''
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
                if(lines.endswith('Date\n')==1):
                    date = (contents[i])
                    if (date=='basis\n'):
                        date = contents[i-3]
                        date = date[14:] 
                if(lines.startswith('Model')==1):
                    modul = (contents[i-2])
                if lines.endswith('Type\n'):
                    heatpumpType=contents[i][:-1]
                if(lines=='Refrigerant\n'):
                    if(contents[i-3]=='Mass Of\n'):
                        continue
                    refrigerant = (contents[i])
                if(lines.startswith('Mass Of')==1):
                    if (lines=='Mass Of\n'):
                        mass=contents[i+1]
                    elif(lines.endswith('kg\n')==1):
                        mass=contents[i-2]
                        mass=mass[20:]
                    else:
                        mass=contents[i]
                
                if lines.startswith('Average'):
                    climate='average'
                if lines.startswith('Cold'):
                    climate='cold'
                if lines.startswith('Warmer Climate'):
                    climate='warm'
                       
                if(lines.startswith('EN')==1):
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
                    NumberOfTestsPerModule=[]
                    NumberOfTestsPerModule=[]
                    if(contents[i-1].startswith('Low')==1):
                        d=0
                        continue
                    if(contents[i-1]=='\n'):

                        continue
                    if(contents[i-1].startswith('Medium')):
                        d=1
                    else: 
                        d=0
                if(lines.startswith('Pdh Tj = -15°C')==1): #check
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
                        Type.append(heatpumpType)
                        Guideline.append(guideline[:-1])
                        Climate.append(climate)
                if(lines.startswith('COP Tj = -15°C')):
                    if(contents[i]=='\n'):
                        continue
                    if(contents[i].startswith('EHPA')):
                        continue
                    COP.append(contents[i][:-1])
                    p=1
            
                    if(contents[i+2].startswith('Pdh')):#no medium Climate
                        continue
                    if(contents[i+2].startswith('Cdh')):#no medium Climate
                        continue
                    if(contents[i+2].startswith('EHPA')):#no medium Climate
                        continue
                    COP.append(contents[i+2][:-1])
                    p=2


                if(lines.startswith('Pdh Tj = -7°C')==1):#check
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
                        Mass.append(mass[:-4])
                        Type.append(heatpumpType)
                        Guideline.append(guideline[:-1])
                        Climate.append(climate)
                if(lines.startswith('COP Tj = -7°C')):
                    COP.append(contents[i][:-1])
                    NumberOfTestsPerModule.append(i)
                    if(contents[i+2].startswith('Pdh')):#no medium Climate
                        continue
                    if(contents[i+2].startswith('Cdh')):#no medium Climate
                        continue
                    COP.append(contents[i+2][:-1])
                    NumberOfTestsPerModule.append(i)


                if(lines.startswith('Pdh Tj = +2°C')==1): 
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
                        Mass.append(mass[:-4])
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
                        Mass.append(mass[:-4])
                        Type.append(heatpumpType)
                        Guideline.append(guideline[:-1])
                        Climate.append(climate)
                if(lines.startswith('COP Tj = +2°C')):#check
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
                    NumberOfTestsPerModule.append(i)

                    if(contents[i+2].startswith('Pdh')):#no medium Climate
                        continue
                    if(contents[i+2].startswith('Cdh')):#no medium Climate
                        continue
                    if(contents[i+2].startswith('EHPA')):#no medium Climate
                        continue
                    COP.append(contents[i+2][:-1])
                    NumberOfTestsPerModule.append(i)


                if(lines.startswith('Pdh Tj = +7°C')==1):
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
                        Mass.append(mass[:-4])
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
                        Mass.append(mass[:-4])
                        Type.append(heatpumpType)
                        Guideline.append(guideline[:-1])
                        Climate.append(climate)
                if(lines.startswith('COP Tj = +7°C')):#check
                    if(contents[i]=='\n'):#no infos
                        continue
                    if(contents[i].startswith('EHPA')):#end of page
                        continue
                    if(contents[i+2].startswith('Warmer')):#usless infos
                        continue
                    if(contents[i]=='n/a\n'):#usless infos
                        continue
                    COP.append(contents[i][:-1])
                    NumberOfTestsPerModule.append(i)

                    if(contents[i+2].startswith('Pdh')):#no medium Climate
                        continue
                    if(contents[i+2].startswith('Cdh')):#no medium Climate
                        continue
                    if(contents[i+2].startswith('EHPA')):#no medium Climate
                        continue
                    COP.append(contents[i+2][:-1])
                    NumberOfTestsPerModule.append(i)


                if(lines.startswith('Pdh Tj = 12°C')==1):
                    
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
                        Mass.append(mass[:-4])
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
                        Mass.append(mass[:-4])
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
                        Mass.append(mass[:-4])
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
                        Mass.append(mass[:-4])
                        Type.append(heatpumpType)
                        Guideline.append(guideline[:-1])
                        Climate.append(climate)
                if(lines.startswith('COP Tj = 12°C')):#check
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
                    NumberOfTestsPerModule.append(i)

                    if(contents[i+2].startswith('Pdh')):#no medium Climate
                        continue
                    if(contents[i+2].startswith('Cdh')):#no medium Climate
                        continue
                    if(contents[i+2].startswith('EHPA')):#no medium Climate
                        continue
                    COP.append(contents[i+2][:-1])
                    NumberOfTestsPerModule.append(i)


                if(lines.startswith('Poff')):
                    l=0 #l shows if Poff Medium is different to Poff Low Temperature
                    c=2 # c is just an iterator to print every second Poff
                    poff=contents[i][:-2]
                    second_poff=contents[i+2][:-2]
                    if(poff!=second_poff): #see if Poff Medium to Poff low
                        if(contents[i+2].endswith('W\n')):
                            if (contents[i+2]!='W\n'):
                                l=1
                    for Tests in NumberOfTestsPerModule:
                        if l==0:
                            Poff.append(poff)
                            SPLind.append(file.name)
                        if l==1:
                            c+=1
                            if c%2==1:
                                Poff.append(poff)
                                SPLind.append(file.name)
                            if c%2==0:
                                Poff.append(second_poff)
                                SPLind.append(file.name)
                if(lines.startswith('PSB')):
                    l=0 #l shows if Poff Medium is different to Poff Low Temperature
                    c=2 # c is just an iterator to print every second Poff
                    psb=contents[i][:-2]
                    psb_medium=contents[i+2][:-2]
                    if(psb!=psb_medium): #see if Poff Medium to Poff low
                        if(contents[i+2].endswith('W\n')):
                            if (contents[i+2]!='W\n'):
                                l=1
                    for Tests in NumberOfTestsPerModule:
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
df['Refrigerant']=Refrigerant
df['Mass of Refrigerant [kg]']=Mass
df['Poff [W]']= Poff
df['PSB [W]']=Psb



df['Guideline']=Guideline
df['Climate']=Climate
df['T_in']=T_in
df['T_in']=df['T_in'].astype(int)
df['T_out']=T_out
df['T_out']=df['T_out'].astype(int)
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
df['P_th']=P_th
df['P_th']=df['P_th'].astype(float)
df['COP']=COP
df['COP']=df['COP'].astype(float)
df['P_el']=round((df['P_th'] / df['COP']),2)

df.to_csv(os.path.dirname(__file__)+r'/data_heatpumpkeymark.csv')