import os
import pandas as pd
import scipy
import hplib as hpl
import pickle


INPUT_FOLDERS = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'input')
OUTPUT_FOLDERS = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'output')


def import_heating_data(parsed_pdf_folder = "txt_07_22", database_name = 'database_heating.csv'):
    """
    Reads the *.txt files in in the scan folder (parsed_pdf_folder) and saves them as a 
    dataframe to database_name in folder

    Args:
        parsed_pdf_folder (str, optional): Path to the raw .txt files, generated from the heatpump pdfs. Defaults to "txt_07_22".
        database_name (str, optional): Resulting database. Defaults to 'database_heating.csv'.
    """  
    # columns to be filled out
    Modul = []
    Manufacturer = []
    Date = []
    Refrigerant = []
    Mass = []
    Poff = []
    Psb = []
    Prated = []
    SPLindoor = []
    SPLoutdoor = []
    Type = []
    Climate = []
    Guideline = []
    T_in = []
    T_out = []
    P_th = []
    COP = []
    df = pd.DataFrame()
    files_in_folder = os.scandir(os.path.join(INPUT_FOLDERS, parsed_pdf_folder))
    with files_in_folder as files_in_folder: # TODO get rid of this
        for file in files_in_folder:
            with open(file, 'r', encoding='utf-8') as f:
                contents = f.readlines()
                date = 'NaN'
                modul = 'NaN'
                prated_low = 'NaN'
                prated_medium = 'NaN'
                heatpumpType = 'NaN'
                refrigerant = 'NaN'
                splindoor_low = 'NaN'
                splindoor_medium = 'NaN'
                sploutdoor_low = 'NaN'
                sploutdoor_medium = 'NaN'
                poff = 'NaN'
                climate = 'NaN'
                NumberOfTestsPerNorm = []
                NumberOfTestsPerModule = []
                low_medium_swapped=0#indicator if they are swaped
                i = 1  # indicator for the line wich is read
                d = 0  # indicator if only medium Temperature is given
                p = 0  # -15° yes or no
                date = contents[1]
                date = date[61:]
                date = standardize_date(date)
                for lines in contents:
                    i = i + 1
                    # get manufacturer name
                    if (lines.startswith('Name\n') == 1):
                        manufacturer = standardize_maufacturer_name(contents[i])

                    # overwrite date (TODO compare with date definition above)
                    elif (lines.endswith('Date\n') == 1):
                        if contents[i-2].startswith('Phase'):
                            continue
                        date = (contents[i])
                        if (date == 'basis\n'):
                            date = contents[i - 3]
                            date = date[14:]


                    elif (lines.startswith('Model:') == 1):
                        modul = (contents[i - 2])
                        if manufacturer.startswith('Heliotherm'):
                            modul=('1234567'+contents[i-31])

                    elif lines.startswith('Heat Pump Type '):
                        heatpumpType=lines[15:-1]

                    elif lines.endswith('Type\n'):
                        heatpumpType = contents[i][:-1]
                        if heatpumpType.startswith('A'):
                            heatpumpType = 'Outdoor Air/Water'
                        if heatpumpType.startswith('Eau glycol'):
                            heatpumpType = 'Brine/Water'
                    
                    # Sound power level
                    elif (lines.startswith('Sound power level indoor')
                        or lines.startswith('Puissance acoustique intérieure') 
                        or lines.startswith('Potencia sonora de la unidad interior')
                        or lines.startswith('Nivel de Potência sonora interior')
                        or lines.startswith('Livello di potenza acustica interna')):
                        splindoor_low, splindoor_medium = extract_spl_low_medium(contents, i)

                    elif (lines.startswith('Sound power level outdoor') 
                        or lines.startswith('Puissance acoustique extérieure')
                        or lines.startswith('Potencia sonora de la unidad exterior')
                        or lines.startswith('Nivel de Potência sonora exterior')
                        or lines.startswith('Livello di potenza acustica externa')):
                        sploutdoor_low, sploutdoor_medium = extract_spl_low_medium(contents, i)

                    # 
                    elif (lines == 'Refrigerant\n'):
                        if (contents[i - 3] == 'Mass Of\n') or (contents[i - 3] == 'Mass of\n'):
                            continue
                        refrigerant = (contents[i])
                    elif (lines.startswith('Mass Of') == 1 or lines.startswith('Mass of')):
                        if (lines == 'Mass Of\n') or (lines == 'Mass of\n'):
                            mass = contents[i + 1]                    
                        elif (lines.endswith('kg\n') == 1):
                            mass = contents[i - 2]
                            mass = mass[20:]
                        else:
                            mass = contents[i]

                    elif lines.startswith('Average'):
                        climate = 'average'
                    elif lines.startswith('Cold'):
                        climate = 'cold'
                    elif lines.startswith('Warmer Climate'):
                        climate = 'warm'

                    elif (lines.startswith('EN') == 1):
                        if (p == 1):
                            Poff.append(poff)
                            Psb.append(psb)
                        if (p == 2):
                            Poff.append(poff)
                            Poff.append(poff)
                            Psb.append(psb)
                            Psb.append(psb_medium)
                        guideline = (contents[i - 2])
                        d = 0  # Medium or Low Content
                        p = 0  # -15 yes or no

                        NumberOfTestsPerNorm = []
                        if (contents[i - 1].startswith('Low') == 1):
                            d = 0
                            continue
                        if (contents[i - 1] == '\n'):
                            continue
                        if (contents[i - 1].startswith('Medium')):
                            d = 1
                        else:
                            d = 0
                    if lines.startswith('Prated'):
                        prated_low = contents[i][:-4]
                        if (contents[i + 2].endswith('kW\n')):
                            prated_medium = contents[i + 2][:-4]


                    elif (lines.startswith('Pdh Tj = -15°C') == 1):  # check
                        if (contents[i].startswith('Cdh') == 1):  # wrong content
                            continue
                        if (contents[i].startswith('EHPA') == 1):  # wrong content
                            continue
                        if (contents[i].endswith('Cdh\n') == 1):  # wrong content
                            continue
                        elif (contents[i] == '\n'):  # no content
                            continue
                        else:
                            minusfifteen_low = contents[i]
                            if minusfifteen_low.endswith('kW'):
                                P_th.append(minusfifteen_low[:-4])
                            else:
                                P_th.append(minusfifteen_low)
                            T_in.append('-15')
                            if d == 0:  # first low than medium Temperatur
                                if (climate == 'average'):
                                    T_out.append('35')
                                elif (climate == 'cold'):
                                    T_out.append('32')
                                elif (climate == 'warm'):
                                    T_out.append('35')

                            if d == 1:  # first medium Temperature
                                if (climate == 'average'):
                                    T_out.append('55')
                                elif (climate == 'cold'):
                                    T_out.append('49')
                                elif (climate == 'warm'):
                                    T_out.append('55')

                            Modul.append(modul[7:-1])
                            Manufacturer.append(manufacturer[:-1])
                            Date.append(date[:-1])
                            Refrigerant.append(refrigerant[:-1])
                            Mass.append(mass[:-4])
                            Prated.append(prated_low)
                            SPLindoor.append(splindoor_low)
                            # SPLindoor.append(splindoor_medium)
                            SPLoutdoor.append(sploutdoor_low)
                            # SPLoutdoor.append(sploutdoor_medium)
                            Guideline.append(guideline[:-1])
                            Climate.append(climate)

                            Type.append(heatpumpType)
                            if (contents[i + 2].startswith('COP')):  # for PDF without medium heat
                                continue
                            elif (contents[i + 2].startswith('Disclaimer')):  # for PDF without medium heat
                                continue
                            elif (contents[i + 2].startswith('EHPA')):  # End of page
                                if (len(contents)- i)<10:
                                    continue
                                elif (contents[i + 8].startswith('COP')):  # end of page plus no medium heat
                                    continue
                            minusfifteen_medium = contents[i + 2]
                            if minusfifteen_medium.endswith('kW'):
                                P_th.append(minusfifteen_medium[:-4])
                            else:
                                P_th.append(minusfifteen_medium)
                            T_in.append('-15')
                            if (climate == 'average'):
                                T_out.append('55')
                            elif (climate == 'cold'):
                                T_out.append('49')
                            elif (climate == 'warm'):
                                T_out.append('55')
                            Modul.append(modul[7:-1])
                            Manufacturer.append(manufacturer[:-1])
                            Date.append(date[:-1])
                            Refrigerant.append(refrigerant[:-1])
                            Mass.append(mass[:-4])
                            Prated.append(prated_medium)
                            # SPLindoor.append(splindoor_low)
                            SPLindoor.append(splindoor_medium)
                            # SPLoutdoor.append(sploutdoor_low)
                            SPLoutdoor.append(sploutdoor_medium)
                            Type.append(heatpumpType)
                            Guideline.append(guideline[:-1])
                            Climate.append(climate)

                    elif (lines.startswith('COP Tj = -15°C')):
                        if (contents[i] == '\n'):
                            continue
                        if (contents[i].startswith('EHPA')):
                            continue

                        COP.append(contents[i][:-1])
                        
                        NumberOfTestsPerModule.append(i)
                        p = 1

                        if (contents[i + 2].startswith('Pdh')):  # no medium Climate
                            continue
                        if (contents[i + 2].startswith('Cdh')):  # no medium Climate
                            continue
                        if (contents[i + 2].startswith('EHPA')):  # no medium Climate
                            continue
                        
                        COP.append(contents[i + 2][:-1])
                        NumberOfTestsPerModule.append(i)
                        p = 2


                    elif (lines.startswith('Pdh Tj = -7°C') == 1):  # check
                        minusseven_low = contents[i]
                        if 'k' in minusseven_low[:-4]:
                            low_medium_swapped=1
                            if minusseven_low[10]=='.':
                                minusseven_low=(minusseven_low[:-8])
                                minusseven_medium = contents[i][-8:]
                                prated_medium=prated_medium[-4:]
                                prated_low=prated_low[:4]
                            elif minusseven_low[11]=='.':
                                minusseven_low=(minusseven_low[:-9])
                                minusseven_medium = contents[i][-9:]
                                prated_medium=prated_medium[-4:]
                                prated_low=prated_low[:4]
                            P_th.append(minusseven_medium[:-4])
                            T_in.append('-7')
                            if (climate == 'average'):
                                T_out.append('52')
                            elif (climate == 'cold'):
                                T_out.append('44')
                            elif (climate == 'warm'):
                                T_out.append('55')
                            Modul.append(modul[7:-1])
                            Manufacturer.append(manufacturer[:-1])
                            Date.append(date[:-1])
                            Refrigerant.append(refrigerant[:-1])
                            # SPLindoor.append(splindoor_low)
                            SPLindoor.append(splindoor_medium)
                            # SPLoutdoor.append(sploutdoor_low)
                            SPLoutdoor.append(sploutdoor_medium)
                            Mass.append(mass[:-4])
                            Prated.append(prated_medium)
                            Type.append(heatpumpType)
                            Guideline.append(guideline[:-1])
                            Climate.append(climate)
                        P_th.append(minusseven_low[:-4])
                        T_in.append('-7')
                        if d == 0:  # first low than medium Temperatur
                            if (climate == 'average'):
                                T_out.append('34')
                            elif (climate == 'cold'):
                                T_out.append('30')
                            elif (climate == 'warm'):
                                T_out.append('35')

                        if d == 1:  # first medium Temperature
                            if (climate == 'average'):
                                T_out.append('52')
                            elif (climate == 'cold'):
                                T_out.append('44')
                            elif (climate == 'warm'):
                                T_out.append('55')
                        
                        Modul.append(modul[7:-1])
                        Manufacturer.append(manufacturer[:-1])
                        Date.append(date[:-1])
                        Refrigerant.append(refrigerant[:-1])
                        Mass.append(mass[:-4])
                        Prated.append(prated_low)
                        SPLindoor.append(splindoor_low)
                        # SPLindoor.append(splindoor_medium)
                        SPLoutdoor.append(sploutdoor_low)
                        # SPLoutdoor.append(sploutdoor_medium)
                        Type.append(heatpumpType)
                        Guideline.append(guideline[:-1])
                        Climate.append(climate)

                        if (contents[i+2].startswith('EHPA')):  # wrong content
                            continue
                        if (contents[i + 2].startswith('COP') == 1):
                                continue
                        elif (contents[i + 2].startswith('kW')):
                                continue
                        else:
                            minusseven_medium = contents[i + 2]
                            P_th.append(minusseven_medium[:-4])
                            T_in.append('-7')
                            if (climate == 'average'):
                                T_out.append('52')
                            elif (climate == 'cold'):
                                T_out.append('44')
                            elif (climate == 'warm'):
                                T_out.append('55')
                            Modul.append(modul[7:-1])
                            Manufacturer.append(manufacturer[:-1])
                            Date.append(date[:-1])
                            Refrigerant.append(refrigerant[:-1])
                            # SPLindoor.append(splindoor_low)
                            SPLindoor.append(splindoor_medium)
                            # SPLoutdoor.append(sploutdoor_low)
                            SPLoutdoor.append(sploutdoor_medium)
                            Mass.append(mass[:-4])
                            Prated.append(prated_medium)
                            Type.append(heatpumpType)
                            Guideline.append(guideline[:-1])
                            Climate.append(climate)

                    elif (lines.startswith('COP Tj = -7°C')):
                        if low_medium_swapped==1:
                            
                            
                            COP.append(contents[i + 2][:-1])
                            COP.append(contents[i][:-1])
                            NumberOfTestsPerNorm.append(i)
                            NumberOfTestsPerModule.append(i)
                            NumberOfTestsPerNorm.append(i)
                            NumberOfTestsPerModule.append(i)
                            low_medium_swapped=0
                            continue
                        
                        COP.append(contents[i][:-1])
                        NumberOfTestsPerNorm.append(i)
                        NumberOfTestsPerModule.append(i)
                        if (contents[i + 2].startswith('EHPA')):  # no medium Climate
                            continue
                        if (contents[i + 2].startswith('Pdh')):  # no medium Climate
                            continue
                        if (contents[i + 2].startswith('Cdh')):  # no medium Climate
                            continue
                        
                        COP.append(contents[i + 2][:-1])
                        NumberOfTestsPerNorm.append(i)
                        NumberOfTestsPerModule.append(i)


                    elif (lines.startswith('Pdh Tj = +2°C') == 1):
                        if (contents[i].endswith('Cdh\n') == 1):  # wrong content
                            continue
                        if (contents[i] == '\n'):  # no content
                            continue
                        else:
                            plustwo_low = contents[i]
                            if 'k' in plustwo_low[:-4]:
                                low_medium_swapped=1
                                if plustwo_low[10]=='.':
                                    plustwo_low=(plustwo_low[:-8])
                                    plustwo_medium = contents[i][-8:]
                                elif plustwo_low[11]=='.':
                                    plustwo_low=(plustwo_low[:-9])
                                    plustwo_medium = contents[i][-9:]
                                P_th.append(plustwo_medium[:-4])
                                T_in.append('2')
                                if (climate == 'average'):
                                    T_out.append('42')
                                elif (climate == 'cold'):
                                    T_out.append('37')
                                elif (climate == 'warm'):
                                    T_out.append('55')
                                Modul.append(modul[7:-1])
                                Manufacturer.append(manufacturer[:-1])
                                Date.append(date[:-1])
                                Refrigerant.append(refrigerant[:-1])
                                # SPLindoor.append(splindoor_low)
                                SPLindoor.append(splindoor_medium)
                                # SPLoutdoor.append(sploutdoor_low)
                                SPLoutdoor.append(sploutdoor_medium)
                                Mass.append(mass[:-4])
                                Prated.append(prated_medium)
                                Type.append(heatpumpType)
                                Guideline.append(guideline[:-1])
                                Climate.append(climate)
                            P_th.append(plustwo_low[:-4])
                            T_in.append('2')
                            if d == 0:  # first low than medium Temperatur
                                if (climate == 'average'):
                                    T_out.append('30')
                                elif (climate == 'cold'):
                                    T_out.append('27')
                                elif (climate == 'warm'):
                                    T_out.append('35')

                            if d == 1:  # first medium Temperature
                                if (climate == 'average'):
                                    T_out.append('42')
                                elif (climate == 'cold'):
                                    T_out.append('37')
                                elif (climate == 'warm'):
                                    T_out.append('55')
                            Modul.append(modul[7:-1])
                            Manufacturer.append(manufacturer[:-1])
                            Date.append(date[:-1])
                            Refrigerant.append(refrigerant[:-1])
                            SPLindoor.append(splindoor_low)
                            # SPLindoor.append(splindoor_medium)
                            SPLoutdoor.append(sploutdoor_low)
                            # SPLoutdoor.append(sploutdoor_medium)
                            Mass.append(mass[:-4])
                            Prated.append(prated_low)
                            Type.append(heatpumpType)
                            Guideline.append(guideline[:-1])
                            Climate.append(climate)

                            if (contents[i + 2].startswith('COP')):  # for PDF without medium heat
                                continue
                            if (contents[i + 2].startswith('Disclaimer')):  # for PDF without medium heat
                                continue
                            if (contents[i + 2].startswith('EHPA')):  # End of page
                                if (contents[i + 8].startswith('COP')):  # end of page plus no medium heat
                                    continue
                            if (contents[i + 2].startswith('kW')):
                                continue
                            plustwo_medium = contents[i + 2]
                            # if(plustwo_low[:-1].endswith('kW')==0):#test
                            # print(plustwo_low[:-1])
                            # if(plustwo_medium[:-1].endswith('kW')==0):#test
                            # print(file.name)#plustwo_medium[:-1]

                            P_th.append(plustwo_medium[:-4])
                            T_in.append('2')
                            if (climate == 'average'):
                                T_out.append('42')
                            elif (climate == 'cold'):
                                T_out.append('37')
                            elif (climate == 'warm'):
                                T_out.append('55')
                            Modul.append(modul[7:-1])
                            Manufacturer.append(manufacturer[:-1])
                            Date.append(date[:-1])
                            Refrigerant.append(refrigerant[:-1])
                            # SPLindoor.append(splindoor_low)
                            SPLindoor.append(splindoor_medium)
                            # SPLoutdoor.append(sploutdoor_low)
                            SPLoutdoor.append(sploutdoor_medium)
                            Mass.append(mass[:-4])
                            Prated.append(prated_medium)
                            Type.append(heatpumpType)
                            Guideline.append(guideline[:-1])
                            Climate.append(climate)

                    elif (lines.startswith('COP Tj = +2°C')):  # check
                        if (contents[i] == '\n'):  # no infos
                            continue
                        if (contents[i].startswith('EHPA')):  # end of page
                            print(file.name)
                            continue
                        if (contents[i + 2].startswith('Warmer')):  # usless infos
                            continue
                        if (contents[i] == 'n/a\n'):  # usless infos
                            continue
                        if low_medium_swapped==1:
                            
                            COP.append(contents[i + 2][:-1])
                            
                            COP.append(contents[i][:-1])
                            NumberOfTestsPerNorm.append(i)
                            NumberOfTestsPerModule.append(i)
                            NumberOfTestsPerNorm.append(i)
                            NumberOfTestsPerModule.append(i)
                            low_medium_swapped=0
                            continue
                        
                        COP.append(contents[i][:-1])
                        NumberOfTestsPerNorm.append(i)
                        NumberOfTestsPerModule.append(i)

                        if (contents[i + 2].startswith('Pdh')):  # no medium Climate
                            continue
                        if (contents[i + 2].startswith('Cdh')):  # no medium Climate
                            continue
                        if (contents[i + 2].startswith('EHPA')):  # no medium Climate
                            continue
                        
                        COP.append(contents[i + 2][:-1])
                        NumberOfTestsPerNorm.append(i)
                        NumberOfTestsPerModule.append(i)


                    elif (lines.startswith('Pdh Tj = +7°C') == 1):
                        if (contents[i].endswith('Cdh\n') == 1):  # wrong content
                            continue
                        if (contents[i] == '\n'):  # no content
                            continue
                        else:
                            plusseven_low = contents[i]
                            if 'k' in plusseven_low[:-4]:
                                low_medium_swapped=1
                                if plusseven_low[10]=='.':
                                    plusseven_low=(plusseven_low[:-8])
                                    pluseven_medium = contents[i][-8:]
                                elif plusseven_low[11]=='.':
                                    plusseven_low=(plusseven_low[:-9])
                                    pluseven_medium = contents[i][-9:]
                                P_th.append(plusseven_medium[:-4])
                                T_in.append('7')
                                if (climate == 'average'):
                                    T_out.append('36')
                                elif (climate == 'cold'):
                                    T_out.append('32')
                                elif (climate == 'warm'):
                                    T_out.append('46')

                                Modul.append(modul[7:-1])
                                Manufacturer.append(manufacturer[:-1])
                                Date.append(date[:-1])
                                Refrigerant.append(refrigerant[:-1])
                                # SPLindoor.append(splindoor_low)
                                SPLindoor.append(splindoor_medium)
                                # SPLoutdoor.append(sploutdoor_low)
                                SPLoutdoor.append(sploutdoor_medium)
                                Mass.append(mass[:-4])
                                Prated.append(prated_medium)
                                Type.append(heatpumpType)
                                Guideline.append(guideline[:-1])
                                Climate.append(climate)
                            P_th.append(plusseven_low[:-4])
                            T_in.append('7')
                            if d == 0:  # first low than medium Temperatur
                                if (climate == 'average'):
                                    T_out.append('27')
                                elif (climate == 'cold'):
                                    T_out.append('25')
                                elif (climate == 'warm'):
                                    T_out.append('31')

                            if d == 1:  # first medium Temperature
                                if (climate == 'average'):
                                    T_out.append('36')
                                elif (climate == 'cold'):
                                    T_out.append('32')
                                elif (climate == 'warm'):
                                    T_out.append('46')
                            Modul.append(modul[7:-1])
                            Manufacturer.append(manufacturer[:-1])
                            Date.append(date[:-1])
                            Refrigerant.append(refrigerant[:-1])
                            SPLindoor.append(splindoor_low)
                            # SPLindoor.append(splindoor_medium)
                            SPLoutdoor.append(sploutdoor_low)
                            # SPLoutdoor.append(sploutdoor_medium)
                            Mass.append(mass[:-4])
                            Prated.append(prated_low)
                            Type.append(heatpumpType)
                            Guideline.append(guideline[:-1])
                            Climate.append(climate)

                            if (contents[i + 2].startswith('COP')):  # for PDF without medium heat
                                continue
                            if (contents[i + 2].startswith('Disclaimer')):  # for PDF without medium heat
                                continue
                            if (contents[i + 2].startswith('EHPA')):  # End of page
                                if (contents[i + 8].startswith('COP')):  # end of page plus no medium heat
                                    continue
                            if (contents[i + 2].startswith('kW')):
                                continue
                            plusseven_medium = contents[i + 2]

                            P_th.append(plusseven_medium[:-4])
                            T_in.append('7')
                            if (climate == 'average'):
                                T_out.append('36')
                            elif (climate == 'cold'):
                                T_out.append('32')
                            elif (climate == 'warm'):
                                T_out.append('46')

                            Modul.append(modul[7:-1])
                            Manufacturer.append(manufacturer[:-1])
                            Date.append(date[:-1])
                            Refrigerant.append(refrigerant[:-1])
                            # SPLindoor.append(splindoor_low)
                            SPLindoor.append(splindoor_medium)
                            # SPLoutdoor.append(sploutdoor_low)
                            SPLoutdoor.append(sploutdoor_medium)
                            Mass.append(mass[:-4])
                            Prated.append(prated_medium)
                            Type.append(heatpumpType)
                            Guideline.append(guideline[:-1])
                            Climate.append(climate)

                    elif (lines.startswith('COP Tj = +7°C')):  # check
                        if (contents[i] == '\n'):  # no infos
                            continue
                        if (contents[i].startswith('EHPA')):  # end of page
                            continue
                        if (contents[i + 2].startswith('Warmer')):  # usless infos
                            continue
                        if (contents[i] == 'n/a\n'):  # usless infos
                            continue
                        if low_medium_swapped==1:
                            COP.append(contents[i + 2][:-1])
                            
                            
                            COP.append(contents[i][:-1])
                            NumberOfTestsPerNorm.append(i)
                            NumberOfTestsPerModule.append(i)
                            NumberOfTestsPerNorm.append(i)
                            NumberOfTestsPerModule.append(i)
                            low_medium_swapped=0
                            continue
                        
                        COP.append(contents[i][:-1])
                        NumberOfTestsPerNorm.append(i)
                        NumberOfTestsPerModule.append(i)

                        if (contents[i + 2].startswith('Pdh')):  # no medium Climate
                            continue
                        if (contents[i + 2].startswith('Cdh')):  # no medium Climate
                            continue
                        if (contents[i + 2].startswith('EHPA')):  # no medium Climate
                            continue
                        
                        COP.append(contents[i + 2][:-1])
                        NumberOfTestsPerNorm.append(i)
                        NumberOfTestsPerModule.append(i)


                    elif (lines.startswith('Pdh Tj = 12°C') == 1):

                        if (contents[i].endswith('Cdh\n') == 1):  # wrong content
                            continue
                        if (contents[i] == '\n'):  # no content
                            continue
                        if (contents[i].startswith('EHPA Secretariat') == 1):
                            plustwelfe_low = (contents[i - 11])

                            P_th.append(plustwelfe_low[:-4])
                            T_in.append('12')
                            if (climate == 'average'):
                                T_out.append('24')
                            elif (climate == 'cold'):
                                T_out.append('24')
                            elif (climate == 'warm'):
                                T_out.append('26')
                            Modul.append(modul[7:-1])
                            Manufacturer.append(manufacturer[:-1])
                            Date.append(date[:-1])
                            Refrigerant.append(refrigerant[:-1])
                            SPLindoor.append(splindoor_low)
                            # SPLindoor.append(splindoor_medium)
                            SPLoutdoor.append(sploutdoor_low)
                            # SPLoutdoor.append(sploutdoor_medium)
                            Mass.append(mass[:-4])
                            Prated.append(prated_low)
                            Type.append(heatpumpType)
                            Guideline.append(guideline[:-1])
                            Climate.append(climate)

                            plustwelfe_medium = (contents[i - 9])

                            P_th.append(plustwelfe_medium[:-4])
                            T_in.append('12')
                            if (climate == 'average'):
                                T_out.append('30')
                            elif (climate == 'cold'):
                                T_out.append('28')
                            elif (climate == 'warm'):
                                T_out.append('34')
                            Modul.append(modul[7:-1])
                            Manufacturer.append(manufacturer[:-1])
                            Date.append(date[:-1])
                            Refrigerant.append(refrigerant[:-1])
                            # SPLindoor.append(splindoor_low)
                            SPLindoor.append(splindoor_medium)
                            # SPLoutdoor.append(sploutdoor_low)
                            SPLoutdoor.append(sploutdoor_medium)
                            Mass.append(mass[:-4])
                            Prated.append(prated_medium)
                            Type.append(heatpumpType)
                            Guideline.append(guideline[:-1])
                            Climate.append(climate)

                        else:
                            plustwelfe_low = contents[i]
                            if 'k' in plustwelfe_low[:-4]:
                                low_medium_swapped=1
                                if plustwelfe_low[10]=='.':
                                    plustwelfe_low=(plustwelfe_low[:-8])
                                    plustwelfe_medium = contents[i][-8:]
                                elif plustwelfe_low[11]=='.':
                                    plustwelfe_low=(plustwelfe_low[:-9])
                                    plustwelfe_medium = contents[i][-9:]
                                P_th.append(plustwelfe_medium[:-4])
                                T_in.append('12')
                                if (climate == 'average'):
                                    T_out.append('30')
                                elif (climate == 'cold'):
                                    T_out.append('28')
                                elif (climate == 'warm'):
                                    T_out.append('34')
                                Modul.append(modul[7:-1])
                                Manufacturer.append(manufacturer[:-1])
                                Date.append(date[:-1])
                                Refrigerant.append(refrigerant[:-1])
                                # SPLindoor.append(splindoor_low)
                                SPLindoor.append(splindoor_medium)

                                SPLoutdoor.append(sploutdoor_medium)
                                Mass.append(mass[:-4])
                                Prated.append(prated_medium)
                                Type.append(heatpumpType)
                                Guideline.append(guideline[:-1])
                                Climate.append(climate)
                            P_th.append(plustwelfe_low[:-4])
                            T_in.append('12')
                            if d == 0:  # first low than medium Temperatur
                                if (climate == 'average'):
                                    T_out.append('24')
                                elif (climate == 'cold'):
                                    T_out.append('24')
                                elif (climate == 'warm'):
                                    T_out.append('26')

                            if d == 1:  # first medium Temperature
                                if (climate == 'average'):
                                    T_out.append('30')
                                elif (climate == 'cold'):
                                    T_out.append('28')
                                elif (climate == 'warm'):
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

                            if (contents[i + 2].startswith('COP')):  # for PDF without medium heat
                                continue
                            if (contents[i + 2].startswith('Disclaimer')):  # for PDF without medium heat
                                continue
                            if (contents[i + 2].startswith('EHPA')):  # End of page
                                if (contents[i + 8].startswith('COP')):  # end of page plus no medium heat
                                    continue
                            if (contents[i + 2].startswith('kW')):
                                continue
                            plustwelfe_medium = contents[i + 2]
                            P_th.append(plustwelfe_medium[:-4])
                            T_in.append('12')
                            if (climate == 'average'):
                                T_out.append('30')
                            elif (climate == 'cold'):
                                T_out.append('28')
                            elif (climate == 'warm'):
                                T_out.append('34')
                            Modul.append(modul[7:-1])
                            Manufacturer.append(manufacturer[:-1])
                            Date.append(date[:-1])
                            Refrigerant.append(refrigerant[:-1])
                            # SPLindoor.append(splindoor_low)
                            SPLindoor.append(splindoor_medium)

                            SPLoutdoor.append(sploutdoor_medium)
                            Mass.append(mass[:-4])
                            Prated.append(prated_medium)
                            Type.append(heatpumpType)
                            Guideline.append(guideline[:-1])
                            Climate.append(climate)

                    elif (lines.startswith('COP Tj = 12°C')):  # check
                        if (contents[i] == '\n'):  # no infos
                            continue
                        if (contents[i].startswith('EHPA')):  # end of page
                            print('W')
                            continue
                        if (contents[i + 2].startswith('Warmer')):  # usless infos
                            continue
                        if (contents[i] == 'n/a\n'):  # usless infos
                            continue
                        if low_medium_swapped==1:
                            
                            
                            COP.append(contents[i + 2][:-1])
                            COP.append(contents[i][:-1])
                            NumberOfTestsPerNorm.append(i)
                            NumberOfTestsPerModule.append(i)
                            NumberOfTestsPerNorm.append(i)
                            NumberOfTestsPerModule.append(i)
                            low_medium_swapped=0
                            continue
                        
                        COP.append(contents[i][:-1])
                        NumberOfTestsPerNorm.append(i)
                        NumberOfTestsPerModule.append(i)

                        if (contents[i + 2].startswith('Pdh')):  # no medium Climate
                            continue
                        if (contents[i + 2].startswith('Cdh')):  # no medium Climate
                            continue
                        if (contents[i + 2].startswith('EHPA')):  # no medium Climate
                            continue
                        
                        COP.append(contents[i + 2][:-1])
                        NumberOfTestsPerNorm.append(i)
                        NumberOfTestsPerModule.append(i)


                    elif (lines.startswith('Poff')):
                        l = 0  # l shows if Poff Medium is different to Poff Low Temperature
                        c = 2  # c is just an iterator to print every second Poff
                        poff = contents[i][:-2]
                        if poff.endswith(' '):
                            poff = poff[:-1]
                            if poff.endswith('.00'):
                                poff = poff[:-3]
                        second_poff = contents[i + 2][:-2]
                        if second_poff.endswith(' '):
                            second_poff = second_poff[:-1]
                            if second_poff.endswith('.00'):
                                second_poff = second_poff[:-3]
                        if (poff != second_poff):  # see if Poff Medium to Poff low
                            if (contents[i + 2].endswith('W\n')):
                                if (contents[i + 2] != 'W\n'):
                                    l = 1
                        for Tests in NumberOfTestsPerNorm:
                            if l == 0:
                                Poff.append(poff)
                            if l == 1:
                                c += 1
                                if c % 2 == 1:
                                    Poff.append(poff)
                                if c % 2 == 0:
                                    Poff.append(second_poff)
                    elif (lines.startswith('PSB')):
                        l = 0  # l shows if Poff Medium is different to Poff Low Temperature
                        c = 2  # c is just an iterator to print every second Poff
                        psb = contents[i][:-2]
                        if psb.endswith(' '):
                            psb = psb[:-1]
                            if psb.endswith('.00'):
                                psb = psb[:-3]
                        psb_medium = contents[i + 2][:-2]
                        if psb_medium.endswith(' '):
                            psb_medium = psb_medium[:-1]
                            if psb_medium.endswith('.00'):
                                psb_medium = psb_medium[:-3]
                        if (psb != psb_medium):  # see if Poff Medium to Poff low
                            if (contents[i + 2].endswith('W\n')):
                                if (contents[i + 2] != 'W\n'):
                                    l = 1

                        for Tests in NumberOfTestsPerNorm:
                            if l == 0:
                                Psb.append(psb)
                            if l == 1:
                                c += 1
                                if c % 2 == 1:
                                    Psb.append(psb)
                                if c % 2 == 0:
                                    Psb.append(psb_medium)

                if p == 1:
                    Poff.append(poff)
                    Psb.append(psb)
                if p == 2:
                    Poff.append(poff)
                    Poff.append(second_poff)
                    Psb.append(psb)
                    Psb.append(psb_medium)
    df['Manufacturer'] = Manufacturer
    df['Model'] = Modul
    df['Date'] = Date
    df['Date'] = pd.to_datetime(df['Date'], format='%d.%m.%Y')
    df['Type'] = Type
    df['SPL indoor [dBA]'] = SPLindoor
    df['SPL outdoor [dBA]'] = SPLoutdoor
    df['Refrigerant'] = Refrigerant
    df['Mass of Refrigerant [kg]'] = Mass
    df['Poff [W]'] = Poff
    df['Poff [W]'] = df['Poff [W]'].astype(int)
    df['PSB [W]'] = Psb
    df['PSB [W]'] = df['PSB [W]'].astype(int)
    df['Prated [W]'] = Prated

    df['Guideline'] = Guideline
    df['Climate'] = Climate
    df['T_in [°C]'] = T_in
    df['T_in [°C]'] = df['T_in [°C]'].astype(int)
    df['T_out [°C]'] = T_out
    df['T_out [°C]'] = df['T_out [°C]'].astype(int)
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
    df['P_th [W]'] = P_th
    df['P_th [W]'] = ((df['P_th [W]'].astype(float)) * 1000).astype(int)
    df['COP'] = COP
    df['COP'] = round(df['COP'].astype(float), 2)
    df['P_el [W]'] = round(df['P_th [W]'] / df['COP'])
    df['P_el [W]'] = df['P_el [W]'].fillna(0).astype(int)
    df['PSB [W]'] = df['PSB [W]'].where(df['PSB [W]'] > df['Poff [W]'],
                                    df['Poff [W]'])  # Poff should not be bigger than PSB
    df.drop(columns=['Poff [W]'], inplace=True)  # not needed anymore
    filt = df['P_th [W]'] < 50  # P_th too small
    df.drop(index=df[filt].index, inplace=True)
    # add T_amb and change T_in to right values
    df['T_amb [°C]'] = df['T_in [°C]']
    filt = df['Type'] == 'Brine/Water'
    df.loc[filt, 'T_in [°C]'] = 0
    filt = df['Type'] == 'Water/Water'
    df.loc[filt, 'T_in [°C]'] = 10
    df = df[
    ['Manufacturer', 'Model', 'Date', 'Type', 'Refrigerant', 'Mass of Refrigerant [kg]', 'PSB [W]', 'Prated [W]',
            'SPL indoor [dBA]', 'SPL outdoor [dBA]', 'Climate', 'T_amb [°C]', 'T_in [°C]', 'T_out [°C]', 'P_th [W]',
            'P_el [W]', 'COP']]
    df.sort_values(by=['Model'], inplace=True)
    df.sort_values(by=['Manufacturer'], inplace=True,key=lambda col: col.str.lower())

    df.to_csv(os.path.join(OUTPUT_FOLDERS, database_name), index=False)

def extract_spl_low_medium(contents, i):
    """Extract sound pressure level (SPL)

    Args:
        contents (TODO): _description_
        i (int): Line number

    Returns:
        spl_low, spl_medium: Sound pressure level low and medium
    """

    if (contents[i].startswith('Low')):
        if contents[i + 2].startswith('Medium'):
            spl_low = contents[i + 4][:-7]
            spl_medium = contents[i + 6][:-7]
    if contents[i].startswith('Medium'):
        spl_medium = contents[i + 4][:-7]
        spl_low = contents[i + 6][:-7]
    elif (contents[i].endswith('dB(A)\n')):
        if (contents[i - 3].startswith('Low')):
            spl_low = contents[i][:-7]
        if (contents[i - 3].startswith('Medium')):
            spl_medium = contents[i][:-7]
        if (contents[i - 6].startswith('Low')):
            spl_low = contents[i][:-7]
        if (contents[i - 6].startswith('Medium')):
            spl_medium = contents[i + 2][:-7]
        if (contents[i - 4].startswith('Low')):
            spl_low = contents[i][:-7]
        if (contents[i - 4].startswith('Medium')):
            spl_medium = contents[i + 2][:-7]
        else:
            spl_low = contents[i][:-7]
            spl_medium = contents[i][:-7]
    return spl_low,spl_medium

def standardize_maufacturer_name(manufacturer):
    if (manufacturer.find('(') > 0):
        manufacturer = manufacturer.split('(', 1)[1].split('\n')[0]
    if manufacturer.endswith('GmbH\n'):
        manufacturer = manufacturer[:-5]
    if manufacturer.endswith('S.p.A.\n'):
        manufacturer = manufacturer[:-6]
    if manufacturer.endswith('s.p.a.\n'):
        manufacturer = manufacturer[:-6]
    if manufacturer.endswith('S.p.A\n'):
        manufacturer = manufacturer[:-5]
    if manufacturer.endswith('S.L.U.\n'):
        manufacturer = manufacturer[:-6]
    if manufacturer.endswith('s.r.o.\n'):
        manufacturer = manufacturer[:-6]
    if manufacturer.endswith('S.A.\n'):
        manufacturer = manufacturer[:-4]
    if manufacturer.endswith('S.L.\n'):
        manufacturer = manufacturer[:-4]
    if manufacturer.endswith('B.V.\n'):
        manufacturer = manufacturer[:-4]
    if manufacturer.endswith('N.V.\n'):
        manufacturer = manufacturer[:-4]
    if manufacturer.endswith('GmbH & Co KG\n'):
        manufacturer = manufacturer[:-12]
    elif manufacturer.startswith('NIBE'):
        manufacturer = 'Nibe\n'
    elif manufacturer.startswith('Nibe'):
        manufacturer = 'Nibe\n'
    elif manufacturer.startswith('Mitsubishi'):
        manufacturer = 'Mitsubishi\n'
    elif manufacturer.startswith('Ochsner'):
        manufacturer = 'Ochsner\n'
    elif manufacturer.startswith('OCHSNER'):
        manufacturer = 'Ochsner\n'
    elif manufacturer.startswith('Viessmann'):
        manufacturer = 'Viessmann\n'
    return manufacturer



def standardize_date(date):
    if (date == '17 Dec 2020\n'):
        date = '17.12.2020\n'
    elif (date == '18 Dec 2020\n'):
        date = '18.12.2020\n'
    elif (date.startswith('5 Mar 2021')):
        date = '05.03.2021\n'
    elif (date.startswith('15 Feb 2021')):
        date = '15.02.2021\n'
    elif (date.startswith('22 Feb 2021')):
        date = '22.02.2021\n'
    elif (date.startswith('18 Mar 2022')):
        date = '18.03.2022\n'
    elif date.startswith('7 Jul 2022'):
        date='07.07.2022\n'
    if ' Jun ' in date:
        date=date.replace(' Jun ','.06.')
    if ' Jul ' in date:
        date=date.replace(' Jul ','.07.')
    return date


def import_cooling_data(parsed_pdf_folder = "txt_07_22", database_name = 'database_cooling.csv'):
    # read in keymark data from *.txt files in /input/txt/
    # save a dataframe to database_heating.csv in folder /output/
    Modul = []
    Manufacturer = []
    Date = []
    Refrigerant = []
    Mass = []
    Type = []
    Pdesignc = []
    Temperatur = []
    T_outside = []
    PDC = []
    EER = []
    df = pd.DataFrame()
    files_in_folder = os.scandir(os.path.join(INPUT_FOLDERS, parsed_pdf_folder))
    with files_in_folder as files_in_folder: # TODO get rid of this
        for file in files_in_folder:
            with open(file, 'r', encoding='utf-8') as f:
                contents = f.readlines()
                T = 0
                i = 1  # indicator for the line wich is read
                date = contents[1]
                date = date[61:]
                date = standardize_date(date)
                for lines in contents:
                    i = i + 1
                    if (lines.startswith('Name\n') == 1):
                        manufacturer = (contents[i][:-1])
                        manufacturer = standardize_maufacturer_name(manufacturer)
                    elif (lines.endswith('Date\n') == 1):
                        date = (contents[i])
                        if (date == 'basis\n'):
                            date = contents[i - 3]
                            date = date[14:]
                    elif (lines.startswith('Model:') == 1):
                        modul = (contents[i - 2][7:-1])
                        temperatur2 = ''
                        if manufacturer.startswith('Heliotherm'):
                            modul=('1234567'+contents[i-31])    
                    elif lines.endswith('Type\n'):
                        heatpumpType = contents[i][:-1]
                        if heatpumpType.startswith('A'):
                            heatpumpType = 'Outdoor Air/Water'
                        if heatpumpType.startswith('Eau glycol'):
                            heatpumpType = 'Brine/Water'
                    elif (lines == 'Refrigerant\n'):
                        if (contents[i - 3] == 'Mass Of\n') or (contents[i - 3] == 'Mass of\n'):
                            continue
                        refrigerant = (contents[i][:-1])
                    elif (lines.startswith('Mass Of') == 1 or lines.startswith('Mass of')):
                        if (lines == 'Mass Of\n') or (lines == 'Mass of\n'):
                            mass = contents[i + 1][:-4]
                        elif (lines.endswith('kg\n') == 1):
                            mass = contents[i - 2]
                            mass = mass[20:-4]
                        else:
                            mass = contents[i][:-4]

                    elif lines.startswith('+'):
                        if T == 0:
                            temperatur1 = contents[i - 2][:-1]
                            if (contents[i].startswith('+')):
                                temperatur2 = contents[i][:-1]
                                T = 1
                                temperatur2 = (temperatur2[1:3])
                            temperatur1 = (temperatur1[1:2])
                        else:
                            T = 0
                    elif lines.startswith('Pdesignc'):
                        pdesignc1 = contents[i][:-4]
                        if temperatur2 != '':
                            pdesignc2 = contents[i + 2][:-4]

                    elif lines.startswith('Pdc Tj = 30°C'):
                        pdcT1_30 = contents[i][:-4]

                        if contents[i + 2].endswith('W\n'):
                            pdcT2_30 = contents[i + 2][:-4]


                    elif lines.startswith('EER Tj = 30°C'):

                        eerT1_30 = (contents[i][:-1])
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

                        if temperatur2 != '':
                            eerT2_30 = contents[i + 2][:-1]
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
                        pdcT1_35 = contents[i][:-4]
                        if contents[i + 2].endswith('W\n'):
                            pdcT2_35 = contents[i + 2][:-4]

                    elif lines.startswith('EER Tj = 35°C'):
                        eerT1_35 = (contents[i][:-1])
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
                        if temperatur2 != '':
                            eerT2_35 = contents[i + 2][:-1]
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
                        pdcT1_25 = contents[i][:-4]
                        if contents[i + 2].endswith('W\n'):
                            pdcT2_25 = contents[i + 2][:-4]

                    elif lines.startswith('EER Tj = 25°C'):
                        eerT1_25 = (contents[i][:-1])
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
                        if temperatur2 != '':
                            eerT2_25 = contents[i + 2][:-1]
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
                        pdcT1_20 = contents[i][:-4]
                        if contents[i + 2].endswith('W\n'):
                            pdcT2_20 = contents[i + 2][:-4]

                    elif lines.startswith('EER Tj = 20°C'):
                        eerT1_20 = (contents[i][:-1])
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
                        if temperatur2 != '':
                            eerT2_20 = contents[i + 2][:-1]
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
    df['Manufacturer'] = Manufacturer
    df['Model'] = Modul
    df['Date'] = Date
    df['Date'] = pd.to_datetime(df['Date'], format='%d.%m.%Y\n')
    df['Type'] = Type
    df['Refrigerant'] = Refrigerant
    df['Mass of Refrigerant [kg]'] = Mass
    df['Pdesignc'] = Pdesignc
    df['T_outside [°C]'] = T_outside
    df['T_out [°C]'] = Temperatur

    df['Pdc [kW]'] = PDC
    df['EER'] = EER

    filt = df['EER'] == 'Cdc'  # P_th too small
    df.drop(index=df[filt].index, inplace=True)
    filt = df['EER'] == 'Cdc Tj = 20 °C'  # No Data
    df.drop(index=df[filt].index, inplace=True)
    filt = df['EER'] == 'Cdc Tj = 25 °C'  # No Data
    df.drop(index=df[filt].index, inplace=True)
    filt = df['EER'] == 'Cdc Tj = 30 °C'  # No Data
    df.drop(index=df[filt].index, inplace=True)
    filt = df['EER'] == 'Pdc Tj = 30°C'  # P_th too small
    df.drop(index=df[filt].index, inplace=True)
    df.sort_values(by=['Model'], inplace=True)
    df.sort_values(by=['Manufacturer'], inplace=True,key=lambda col: col.str.lower())

    df.to_csv(os.path.join(OUTPUT_FOLDERS, database_name), index=False)

def reduce_heating_data(filename, climate):
    # reduce the hplib_database_heating to a specific climate measurement series (average, warm, cold)
    # delete redundant entries
    # climate = average, warm or cold
    df = pd.read_csv(r'../output/' + filename)
    data_key = df.loc[df['Climate'] == climate]
    delete = []
    Models = data_key['Model'].values.tolist()
    Models = list(dict.fromkeys(Models))
    for model in Models:
        Modeldf = data_key.loc[data_key['Model'] == model, :]
        if Modeldf.shape[0] != 8:  # Models with more ar less than 8 datapoints are deleted
            delete.append('delete')
        else:
            delete.append('keep')
    deletemodels = pd.DataFrame()
    deletemodels['delete'] = delete
    deletemodels['Model'] = Models
    data_key = data_key.merge(deletemodels, how='inner', on='Model')
    data_key = data_key.loc[data_key['delete'] == 'keep']
    data_key.drop(columns=['delete'], inplace=True)
    data_key.to_csv(r'../output/database_heating_' + climate + '.csv', index=False)


def normalize_heating_data(filename):
    data_key = pd.read_csv(r'../output/' + filename)  # read Dataframe of all models
    Models = data_key['Model'].values.tolist()
    Models = list(dict.fromkeys(Models))
    new_df = pd.DataFrame()
    for model in Models:
        data_key = pd.read_csv(r'../output/' + filename)  # read Dataframe of all models
        data = data_key.loc[((data_key['Model'] == model) & (
                    data_key['T_out [°C]'] == 52))]  # only use data of model and ref point -7/52
        Pel_ref = data['P_el [W]'].array[0]  # ref Point Pel
        Pth_ref = data['P_th [W]'].array[0]  # ref Point Pth
        data_key = data_key.loc[data_key['Model'] == model]  # only use data of model
        data_key.loc[:, ['P_th_n']] = data_key['P_th [W]'] / Pth_ref  # get normalized Value P_th_n
        data_key.loc[:, ['P_el_n']] = data_key['P_el [W]'] / Pel_ref  # get normalized Value P_el_n
        new_df = pd.concat([new_df, data_key])  # merge new Dataframe with old one
    filt1 = (new_df['P_th_n'] >= 2) & (new_df['T_out [°C]'] == 34)
    deletemodels = new_df.loc[filt1, ['Model']].values.tolist()
    for model in deletemodels:
        new_df = new_df.loc[new_df['Model'] != model[0]]

    new_df.to_csv(r'../output/' + filename[:-4] + '_normalized.csv', encoding='utf-8', index=False)


def get_subtype(P_th_minus7_34, P_th_2_30, P_th_7_27, P_th_12_24):
    if (P_th_minus7_34 <= P_th_2_30):
        if (P_th_2_30 <= P_th_7_27):
            if (P_th_7_27 <= P_th_12_24):
                modus = 'On-Off'
            else:
                modus = 'Regulated'  # Inverter, 2-Stages, etc.
        else:
            modus = 'Regulated'  # Inverter, 2-Stages, etc.
    else:
        modus = 'Regulated'  # Inverter, 2-Stages, etc.
    return modus


def identify_subtypes(filename):
    # Identify Subtype like On-Off or Regulated by comparing the thermal Power output at different temperature levels:
    # -7/34 |  2/30  |  7/27  |  12/24
    # assumptions for On-Off Heatpump: if temperature difference is bigger, thermal Power output is smaller
    # assumptions for Regulated: everythin else

    data_key = pd.read_csv(r'../output/' + filename)  # read Dataframe of all models
    Models = data_key['Model'].values.tolist()
    Models = list(dict.fromkeys(Models))
    data_keymark = data_key.rename(
        columns={'P_el [W]': 'P_el', 'P_th [W]': 'P_th', 'T_in [°C]': 'T_in', 'T_out [°C]': 'T_out'})
    data_keymark['deltaT'] = data_keymark['T_out'] - data_keymark['T_in']

    Subtypelist = []
    for model in Models:
        try:
            P_thermal = []
            filt1 = data_keymark['T_out'] == 34
            Tin_minus_seven = data_keymark.loc[filt1]
            filt2 = Tin_minus_seven['Model'] == model
            Model_minus_seven = Tin_minus_seven[filt2]
            P_th_minus_seven = Model_minus_seven['P_th'].array[0]
            P_thermal.append(P_th_minus_seven)

            filt1 = data_keymark['T_out'] == 30
            T_in_plus_two = data_keymark.loc[filt1]
            filt2 = T_in_plus_two['Model'] == model
            Model_plus_two = T_in_plus_two[filt2]
            P_th_plus_two = Model_plus_two['P_th'].array[0]
            P_thermal.append(P_th_plus_two)

            filt1 = data_keymark['T_out'] == 27
            Tin_plus_seven = data_keymark.loc[filt1]
            filt2 = Tin_plus_seven['Model'] == model
            Model_plus_seven = Tin_plus_seven[filt2]
            P_th_plus_seven = Model_plus_seven['P_th'].array[0]
            P_thermal.append(P_th_plus_seven)

            filt1 = data_keymark['T_out'] == 24
            Tin_plus_twelfe = data_keymark.loc[filt1]
            filt2 = Tin_plus_twelfe['Model'] == model
            Model_plus_twelfe = Tin_plus_twelfe[filt2]
            P_th_plus_twelfe = Model_plus_twelfe['P_th'].array[0]
            P_thermal.append(P_th_plus_twelfe)
            P_thermal
            Modus = get_subtype(P_thermal[0], P_thermal[1], P_thermal[2], P_thermal[3])
        except:
            print(model)
        Subtypelist.append(Modus)
    Subtype_df = pd.DataFrame()
    Subtype_df['Model'] = Models
    Subtype_df['Subtype'] = Subtypelist
    Subtype_df
    data_key = pd.read_csv(r'../output/' + filename)  # read Dataframe of all models
    data_key = data_key.merge(Subtype_df, how='inner', on='Model')

    ##assign group:

    filt1 = (data_key['Type'] == 'Outdoor Air/Water') & (data_key['Subtype'] == 'Regulated')
    data_key.loc[filt1, 'Group'] = 1
    filt1 = (data_key['Type'] == 'Exhaust Air/Water') & (data_key['Subtype'] == 'Regulated')
    data_key.loc[filt1, 'Group'] = 7
    filt1 = (data_key['Type'] == 'Brine/Water') & (data_key['Subtype'] == 'Regulated')
    data_key.loc[filt1, 'Group'] = 2
    filt1 = (data_key['Type'] == 'Water/Water') & (data_key['Subtype'] == 'Regulated')
    data_key.loc[filt1, 'Group'] = 3

    filt1 = (data_key['Type'] == 'Outdoor Air/Water') & (data_key['Subtype'] == 'On-Off')
    data_key.loc[filt1, 'Group'] = 4
    filt1 = (data_key['Type'] == 'Exhaust Air/Water') & (data_key['Subtype'] == 'On-Off')
    data_key.loc[filt1, 'Group'] = 7
    filt1 = (data_key['Type'] == 'Brine/Water') & (data_key['Subtype'] == 'On-Off')
    data_key.loc[filt1, 'Group'] = 5
    filt1 = (data_key['Type'] == 'Water/Water') & (data_key['Subtype'] == 'On-Off')
    data_key.loc[filt1, 'Group'] = 6

    data_key = data_key[
        ['Manufacturer', 'Model', 'Date', 'Type', 'Subtype', 'Group', 'Refrigerant', 'Mass of Refrigerant [kg]',
         'SPL indoor [dBA]', 'SPL outdoor [dBA]', 'PSB [W]', 'Climate', 'T_amb [°C]', 'T_in [°C]', 'T_out [°C]',
         'P_th [W]', 'P_el [W]', 'COP', 'P_th_n', 'P_el_n']]
    filt1 = data_key['Group'] != 7
    data_key = data_key.loc[filt1]
    data_key.to_csv(r'../output/' + filename[:-4] + '_subtypes.csv', encoding='utf-8', index=False)


def fit_simple(w, x, y, z):
    p0 = [0.1, 0.001, 0.1, 1.]  # starting values
    a = (w, x, y, z)
    para, _ = scipy.optimize.leastsq(func_simple_zero, p0, args=a)
    return para


def func_simple_zero(para, w, x, y, z):
    k1, k2, k3, k4 = para
    z_calc = k1 * w + k2 * x + k3 + k4 * y
    z_diff = z_calc - z
    return z_diff


def func_simple(para, w, x, y):
    # Function to calculate z using parameters and any x and y:
    k1, k2, k3, k4 = para
    z = k1 * w + k2 * x + k3 + k4 * y
    return z


def calculate_heating_parameters(filename):
    # Calculate function parameters from normalized values
    data_key = pd.read_csv('../output/' + filename)
    Models = data_key['Model'].values.tolist()
    Models = list(dict.fromkeys(Models))  # get models

    Group = []
    Pel_ref = []
    Pth_ref = []
    p1_P_th = []
    p2_P_th = []
    p3_P_th = []
    p4_P_th = []
    p1_P_el = []
    p2_P_el = []
    p3_P_el = []
    p4_P_el = []
    p1_COP = []
    p2_COP = []
    p3_COP = []
    p4_COP = []

    for model in Models:
        data_key = pd.read_csv('../output/' + filename)
        data_key = data_key.rename(
            columns={'P_el [W]': 'P_el', 'P_th [W]': 'P_th', 'T_in [°C]': 'T_in', 'T_out [°C]': 'T_out',
                     'T_amb [°C]': 'T_amb'})
        data_key = data_key.loc[data_key['Model'] == model]  # get data of model
        group = data_key.Group.array[0]  # get Group of model
        if group > 1 and group != 4:  # give another point at different Temperature of Brine/Water
            data_key1 = data_key.loc[data_key['Model'] == model]
            data_key1['T_in'] = data_key1['T_in'] + 1
            data_key1['T_out'] = data_key1['T_out'] + 1
            data_key = pd.concat([data_key, data_key1])
        Pel_REF = data_key.loc[data_key['P_el_n'] == 1, ['P_el']].values.tolist()[0][0]
        Pth_REF = data_key.loc[data_key['P_th_n'] == 1, ['P_th']].values.tolist()[0][0]
        data_key.fillna(0, inplace=True)

        if group == 1 or group == 2 or group == 3:
            data = data_key.loc[((data_key['T_amb'] != 12) & (data_key['T_amb'] != 7))]
            P_el_n_para_key = fit_simple(data['T_in'], data['T_out'], data['T_amb'], data['P_el_n'])
            P_th_n_para_key = fit_simple(data_key['T_in'], data_key['T_out'], data_key['T_amb'], data_key['P_th_n'])
            COP_para_key = fit_simple(data_key['T_in'], data_key['T_out'], data_key['T_amb'], data_key['COP'])
        else:
            P_el_n_para_key = fit_simple(data_key['T_in'], data_key['T_out'], data_key['T_amb'], data_key['P_el_n'])
            P_th_n_para_key = fit_simple(data_key['T_in'], data_key['T_out'], data_key['T_amb'], data_key['P_th_n'])
            COP_para_key = fit_simple(data_key['T_in'], data_key['T_out'], data_key['T_amb'], data_key['COP'])

        # write Parameters in List
        p1_P_th.append(P_th_n_para_key[0])
        p2_P_th.append(P_th_n_para_key[1])
        p3_P_th.append(P_th_n_para_key[2])
        p4_P_th.append(P_th_n_para_key[3])
        p1_P_el.append(P_el_n_para_key[0])
        p2_P_el.append(P_el_n_para_key[1])
        p3_P_el.append(P_el_n_para_key[2])
        p4_P_el.append(P_el_n_para_key[3])
        p1_COP.append(COP_para_key[0])
        p2_COP.append(COP_para_key[1])
        p3_COP.append(COP_para_key[2])
        p4_COP.append(COP_para_key[3])
        Group.append(group)
        Pel_ref.append(Pel_REF)
        Pth_ref.append(Pth_REF)

    # write List  in Dataframe

    paradf = pd.DataFrame()
    paradf['Model'] = Models
    paradf['p1_P_th [1/°C]'] = p1_P_th
    paradf['p2_P_th [1/°C]'] = p2_P_th
    paradf['p3_P_th [-]'] = p3_P_th
    paradf['p4_P_th [1/°C]'] = p4_P_th
    paradf['p1_P_el_h [1/°C]'] = p1_P_el
    paradf['p2_P_el_h [1/°C]'] = p2_P_el
    paradf['p3_P_el_h [-]'] = p3_P_el
    paradf['p4_P_el_h [1/°C]'] = p4_P_el
    paradf['p1_COP [-]'] = p1_COP
    paradf['p2_COP [-]'] = p2_COP
    paradf['p3_COP [-]'] = p3_COP
    paradf['p4_COP [-]'] = p4_COP
    paradf['Group'] = Group
    paradf['P_el_ref'] = Pel_ref
    paradf['P_th_ref'] = Pth_ref


    para = paradf
    key = pd.read_csv('../output/' + filename)
    key = key.loc[key['T_out [°C]'] == 52]
    parakey = para.merge(key, how='left', on='Model')
    parakey = parakey.rename(columns={'Group_x': 'Group', 'P_el_ref': 'P_el_h_ref [W]', 'P_th_ref': 'P_th_h_ref [W]'})
    parakey['COP_ref'] = parakey['P_th_h_ref [W]'] / parakey['P_el_h_ref [W]']
    table = parakey[
        ['Manufacturer', 'Model', 'Date', 'Type', 'Subtype', 'Group', 'Refrigerant', 'Mass of Refrigerant [kg]',
         'SPL indoor [dBA]', 'SPL outdoor [dBA]', 'PSB [W]', 'Climate', 'P_el_h_ref [W]', 'P_th_h_ref [W]', 'COP_ref',
         'p1_P_th [1/°C]', 'p2_P_th [1/°C]', 'p3_P_th [-]', 'p4_P_th [1/°C]', 'p1_P_el_h [1/°C]', 'p2_P_el_h [1/°C]',
         'p3_P_el_h [-]', 'p4_P_el_h [1/°C]', 'p1_COP [-]', 'p2_COP [-]', 'p3_COP [-]', 'p4_COP [-]']]
    table.sort_values(by=['Model'], inplace=True)
    table.sort_values(by=['Manufacturer'], inplace=True,key=lambda col: col.str.lower())
    table.to_csv('hplib_database_all.csv', encoding='utf-8', index=False)
    table.to_csv('hplib_database.csv', encoding='utf-8', index=False)
    table.to_csv('../output/hplib_database_heating.csv', encoding='utf-8', index=False)


def validation_relative_error_heating():
    # Simulate every set point for every heat pump and save csv file
    df=pd.read_csv('../output/database_heating_average_normalized_subtypes.csv')
    i=0
    prev_model='first Model'
    while i<len(df): 
        Model=df.iloc[i,1]
        T_amb=df.iloc[i,12]
        T_in=df.iloc[i,13]
        T_out=df.iloc[i,14]
        P_th=df.iloc[i,15]
        P_el=df.iloc[i,16]
        COP=df.iloc[i,17] 
        try:
            if prev_model!=Model:
                para=hpl.get_parameters(Model)
            results=hpl.simulate(T_in,T_out-5,para,T_amb)
            df.loc[i,'P_th_sim']=results.P_th[0]
            df.loc[i,'P_el_sim']=results.P_el[0]
            df.loc[i,'COP_sim']=results.COP[0]
            prev_model=Model
            i=i+1
        except:
            i=i+1
            pass
    
    # Relative error (RE) for every set point
    df['RE_P_th']=(df['P_th_sim']/df['P_th [W]']-1)*100
    df['RE_P_el']=(df['P_el_sim']/df['P_el [W]']-1)*100
    df['RE_COP']=(df['COP_sim']/df['COP']-1)*100
    df.to_csv('../output/database_heating_average_normalized_subtypes_validation.csv', encoding='utf-8', index=False)


def validation_mape_heating():
    #calculate the mean absolute percentage error for every heat pump and save in hplib_database.csv
    df=pd.read_csv('../output/database_heating_average_normalized_subtypes_validation.csv')
    para=pd.read_csv('../output/hplib_database_heating.csv', delimiter=',')
    para=para.loc[para['Model']!='Generic']
    Models = para['Model'].values.tolist()
    Models = list(dict.fromkeys(Models))
    mape_cop=[]
    mape_pel=[]
    mape_pth=[]
    for model in Models:
        df_model=df.loc[df['Model']==model]
        mape_pth.append((((df_model['P_th [W]']-df_model['P_th_sim']).abs())/df_model['P_th [W]']*100).mean())
        mape_pel.append((((df_model['P_el [W]']-df_model['P_el_sim']).abs())/df_model['P_el [W]']*100).mean())
        mape_cop.append((((df_model['COP']-df_model['COP_sim']).abs())/df_model['COP']*100).mean())
    para['MAPE_P_el']=mape_pel
    para['MAPE_COP']=mape_cop
    para['MAPE_P_th']=mape_pth
    para.to_csv('../output/hplib_database_heating.csv', encoding='utf-8', index=False)


def add_generic():
    data_key = pd.read_csv('hplib_database.csv', delimiter=',')
    data_key = data_key.loc[data_key['Model'] != 'Generic']
    Groups = [1, 2, 3, 4, 5, 6]
    for group in Groups:
        if group == 1:
            Type = 'Outdoor Air/Water'
            modus = 'Regulated'
        elif group == 2:
            Type = 'Brine/Water'
            modus = 'Regulated'
        elif group == 3:
            Type = 'Water/Water'
            modus = 'Regulated'
        elif group == 4:
            Type = 'Outdoor Air/Water'
            modus = 'On-Off'
        elif group == 5:
            Type = 'Brine/Water'
            modus = 'On-Off'
        elif group == 6:
            Type = 'Water/Water'
            modus = 'On-Off'

        Group1 = data_key.loc[data_key['Group'] == group] 
        Group1=Group1.loc[Group1['MAPE_P_el']<=25]
        p1_P_th_average = pd.unique(Group1['p1_P_th [1/°C]']).mean(0)
        p2_P_th_average = pd.unique(Group1['p2_P_th [1/°C]']).mean(0)
        p3_P_th_average = pd.unique(Group1['p3_P_th [-]']).mean(0)
        p4_P_th_average = pd.unique(Group1['p4_P_th [1/°C]']).mean(0)
        p1_P_el_average = pd.unique(Group1['p1_P_el_h [1/°C]']).mean(0)
        p2_P_el_average = pd.unique(Group1['p2_P_el_h [1/°C]']).mean(0)
        p3_P_el_average = pd.unique(Group1['p3_P_el_h [-]']).mean(0)
        p4_P_el_average = pd.unique(Group1['p4_P_el_h [1/°C]']).mean(0)
        p1_COP_average = pd.unique(Group1['p1_COP [-]']).mean(0)
        p2_COP_average = pd.unique(Group1['p2_COP [-]']).mean(0)
        p3_COP_average = pd.unique(Group1['p3_COP [-]']).mean(0)
        p4_COP_average = pd.unique(Group1['p4_COP [-]']).mean(0)
        p1_Pdc_average = Group1['p1_Pdc [1/°C]'].mean(0)
        p2_Pdc_average = Group1['p2_Pdc [1/°C]'].mean(0)
        p3_Pdc_average = Group1['p3_Pdc [-]'].mean(0)
        p4_Pdc_average = Group1['p4_Pdc [1/°C]'].mean(0)
        p5_P_el_average = Group1['p1_P_el_c [1/°C]'].mean(0)
        p6_P_el_average = Group1['p2_P_el_c [1/°C]'].mean(0)
        p7_P_el_average = Group1['p3_P_el_c [-]'].mean(0)
        p8_P_el_average = Group1['p4_P_el_c [1/°C]'].mean(0)
        p1_EER_average = Group1['p1_EER [-]'].mean(0)
        p2_EER_average = Group1['p2_EER [-]'].mean(0)
        p3_EER_average = Group1['p3_EER [-]'].mean(0)
        p4_EER_average = Group1['p4_EER [-]'].mean(0)
        if group == 1 or group == 4:
            COP_ref = -7 * p1_COP_average + 52 * p2_COP_average + p3_COP_average - 7 * p4_COP_average
        elif group == 2 or group == 5:
            COP_ref = 0 * p1_COP_average + 52 * p2_COP_average + p3_COP_average - 7 * p4_COP_average
        elif group == 3 or group == 6:
            COP_ref = 10 * p1_COP_average + 52 * p2_COP_average + p3_COP_average - 7 * p4_COP_average
        data_key.loc[len(data_key.index)] = ['Generic', 'Generic', '', Type, modus, group, '', '', '', '', '',
                                                'average', '', '', COP_ref,'', '', p1_P_th_average, p2_P_th_average,
                                                 p3_P_th_average, p4_P_th_average, p1_P_el_average, p2_P_el_average,
                                                 p3_P_el_average, p4_P_el_average, p1_COP_average, p2_COP_average,
                                                 p3_COP_average, p4_COP_average, '', '', '',
                                                 p1_Pdc_average, p2_Pdc_average, p3_Pdc_average, p4_Pdc_average,
                                                 p5_P_el_average,p6_P_el_average ,p7_P_el_average ,p8_P_el_average ,
                                                 p1_EER_average,p2_EER_average ,p3_EER_average ,p4_EER_average, 
                                                 '', '', '']
    data_key['COP_ref'] = data_key['COP_ref'].round(2)
    data_key.to_csv('hplib_database.csv', encoding='utf-8', index=False)


def reduce_to_unique():
    # Many heat pump models have several entries 
    # because of different controller or storage configurations. 
    # Reduce to unique heat pump models.
    df = pd.read_csv('../output/hplib_database_heating.csv', delimiter=',')
    df_cool=pd.read_csv('../output/database_cooling.csv')
    cooling_Models=df_cool['Model'].unique()
    Models = []
    built_type={}
    unique_values = pd.unique(df['p3_COP [-]']).tolist()
    for values in unique_values:
        modelnames = df.loc[df['p3_COP [-]'] == values, ['Model']]
        equal_Models=[]
        for model in (modelnames.Model.values):
            equal_Models.append(model)
            for cooling_model in cooling_Models:
                if model==cooling_model:
                    modelnames.Model.values[0]=model    
        Models.append(modelnames.Model.values[0])
        built_type[modelnames.Model.values[0]]=equal_Models
    new_df = pd.DataFrame()
    new_df1 = pd.DataFrame()
    for model in Models:
        new_df1 = df.loc[df['Model'] == model]
        new_df = pd.concat([new_df, new_df1])
    # create a binary pickle file 
    f = open("same_built_type.pkl","wb")
    # write the python object (dict) to pickle file
    pickle.dump(built_type,f)
    # close file
    f.close()
    new_df.sort_values(by=['Model'], inplace=True)
    new_df.sort_values(by=['Manufacturer'], inplace=True,key=lambda col: col.str.lower())
    new_df.to_csv('../output/hplib_database_heating.csv', encoding='utf-8', index=False)
    new_df.to_csv('hplib_database.csv', encoding='utf-8', index=False)


def reduce_cooling_data():
    df_cool=pd.read_csv('../output/database_cooling.csv')
    df_heat=pd.read_csv('../output/hplib_database_heating.csv')
    df = df_cool.merge(df_heat, on='Model', how='left')#merge with the ones from heating to get Group Number
    df=df.iloc[:,:16]
    df['Pdc [W]']=df['Pdc [kW]']*1000#get W
    df.drop(columns=['Pdc [kW]','Date_y','Type_y','Manufacturer_y','Subtype','Pdesignc','Refrigerant_x','Mass of Refrigerant [kg]_x','Type_x','Date_x'], inplace=True)
    df = df.rename(columns={'Manufacturer_x': 'Manufacturer','T_out [°C]_x':'T_out [°C]'}) 
    df=df.loc[df['Group']==1]
    df['P_el [W]']=df['Pdc [W]']/df['EER']#add P_el
    df.to_csv('../output/database_cooling_reduced.csv',encoding='utf-8', index=False)


def normalize_and_add_cooling_data():
    df = pd.read_csv(r'../output/database_cooling_reduced.csv')
    Models = df['Model'].values.tolist()
    Models = list(dict.fromkeys(Models))
    new_df = pd.DataFrame()
    for model in Models:   
        data_key = pd.read_csv(r'../output/database_cooling_reduced.csv')
        data_key = data_key.loc[data_key['Model'] == model]  # get data of model
        group = data_key.Group.array[0]  # get Group of model
        if len(data_key)==4:  
            data_key1 = data_key.loc[data_key['Model'] == model]
            data_key1['T_out [°C]'] = data_key1['T_out [°C]'] + 11#the following values are based on 3 heatpumps, which have those values in the keymark
            data_key1.loc[data_key1['T_outside [°C]']==35,'P_el [W]']=data_key1.loc[data_key1['T_outside [°C]']==35,'P_el [W]'] * 0.85
            data_key1.loc[data_key1['T_outside [°C]']==30,'P_el [W]']=data_key1.loc[data_key1['T_outside [°C]']==30,'P_el [W]'] * 0.82
            data_key1.loc[data_key1['T_outside [°C]']==25,'P_el [W]']=data_key1.loc[data_key1['T_outside [°C]']==25,'P_el [W]'] * 0.77
            data_key1.loc[data_key1['T_outside [°C]']==20,'P_el [W]']=data_key1.loc[data_key1['T_outside [°C]']==20,'P_el [W]'] * 0.63
            data_key1.loc[data_key1['T_outside [°C]']==35,'EER']=data_key1.loc[data_key1['T_outside [°C]']==35,'EER'] * 1.21
            data_key1.loc[data_key1['T_outside [°C]']==30,'EER']=data_key1.loc[data_key1['T_outside [°C]']==30,'EER'] * 1.21
            data_key1.loc[data_key1['T_outside [°C]']==25,'EER']=data_key1.loc[data_key1['T_outside [°C]']==25,'EER'] * 1.20
            data_key1.loc[data_key1['T_outside [°C]']==20,'EER']=data_key1.loc[data_key1['T_outside [°C]']==20,'EER'] * 0.95
            data_key1['Pdc [W]']=data_key1['P_el [W]']*data_key1['EER']
            data_key = pd.concat([data_key, data_key1])
        df_ref_pdc=data_key.loc[(data_key['T_outside [°C]']==35) & (data_key['T_out [°C]']==7),'Pdc [W]'].values[0]
        data_key['Pdc_n']=data_key['Pdc [W]']/df_ref_pdc
        df_ref_p_el=data_key.loc[(data_key['T_outside [°C]']==35) & (data_key['T_out [°C]']==7),'P_el [W]'].values[0]
        data_key['P_el_n']=data_key['P_el [W]']/df_ref_p_el
        new_df = pd.concat([new_df, data_key])  # merge new Dataframe with old one
    new_df.to_csv('../output/database_cooling_reduced_normalized.csv',encoding='utf-8', index=False)


def calculate_cooling_parameters():
    # Calculate function parameters from normalized values
    data_key = pd.read_csv('../output/database_cooling_reduced_normalized.csv')
    Models = data_key['Model'].values.tolist()
    Models = list(dict.fromkeys(Models))  # get models

    Group = []
    Pel_ref = []
    Pdc_ref = []
    p1_Pdc = []
    p2_Pdc = []
    p3_Pdc = []
    p4_Pdc = []
    p1_P_el = []
    p2_P_el = []
    p3_P_el = []
    p4_P_el = []
    p1_EER = []
    p2_EER = []
    p3_EER = []
    p4_EER = []

    for model in Models:
        data_key = pd.read_csv('../output/database_cooling_reduced_normalized.csv')
        data_key = data_key.rename(
            columns={'P_el [W]': 'P_el', 'Pdc [W]': 'Pdc', 'T_outside [°C]': 'T_in', 'T_out [°C]': 'T_out'})
        data_key = data_key.loc[data_key['Model'] == model]  # get data of model
        group = data_key.Group.array[0]  # get Group of model
        Pel_REF = data_key.loc[data_key['P_el_n'] == 1, ['P_el']].values.tolist()[0][0]
        Pdc_REF = data_key.loc[data_key['Pdc_n'] == 1, ['Pdc']].values.tolist()[0][0]
        data_key.fillna(0, inplace=True)
        data_key['T_amb']=data_key['T_in']
        data = data_key.loc[data_key['T_in'] > 24] #& (data_key['T_in'] != ))]
        P_el_n_para_key = fit_simple(data['T_in'], data['T_out'], data['T_amb'], data['P_el_n'])
        #P_el_n_para_key = fit_simple(data_key['T_in'], data_key['T_out'], data_key['T_amb'], data_key['P_el_n'])
        Pdc_n_para_key = fit_simple(data_key['T_in'], data_key['T_out'], data_key['T_amb'], data_key['Pdc_n'])
        EER_para_key = fit_simple(data_key['T_in'], data_key['T_out'], data_key['T_amb'], data_key['EER'])

        # write Parameters in List
        p1_Pdc.append(Pdc_n_para_key[0])
        p2_Pdc.append(Pdc_n_para_key[1])
        p3_Pdc.append(Pdc_n_para_key[2])
        p4_Pdc.append(Pdc_n_para_key[3])
        p1_P_el.append(P_el_n_para_key[0])
        p2_P_el.append(P_el_n_para_key[1])
        p3_P_el.append(P_el_n_para_key[2])
        p4_P_el.append(P_el_n_para_key[3])
        p1_EER.append(EER_para_key[0])
        p2_EER.append(EER_para_key[1])
        p3_EER.append(EER_para_key[2])
        p4_EER.append(EER_para_key[3])
        Group.append(group)
        Pel_ref.append(Pel_REF)
        Pdc_ref.append(Pdc_REF)

    # write List  in Dataframe

    paradf = pd.DataFrame()
    paradf['Model'] = Models
    paradf['p1_Pdc [1/°C]'] = p1_Pdc
    paradf['p2_Pdc [1/°C]'] = p2_Pdc
    paradf['p3_Pdc [-]'] = p3_Pdc
    paradf['p4_Pdc [1/°C]'] = p4_Pdc
    paradf['p1_P_el_c [1/°C]'] = p1_P_el
    paradf['p2_P_el_c [1/°C]'] = p2_P_el
    paradf['p3_P_el_c [-]'] = p3_P_el
    paradf['p4_P_el_c [1/°C]'] = p4_P_el
    paradf['p1_EER [-]'] = p1_EER
    paradf['p2_EER [-]'] = p2_EER
    paradf['p3_EER [-]'] = p3_EER
    paradf['p4_EER [-]'] = p4_EER
    paradf['P_el_cooling_ref'] = Pel_ref
    paradf['Pdc_ref'] = Pdc_ref
    hplib=pd.read_csv('../output/hplib_database_heating.csv')
    os.remove('../output/hplib_database_heating.csv')        
    para = hplib.merge(paradf, how='left', on='Model')
    para.rename(columns={'P_el_cooling_ref': 'P_el_c_ref [W]', 'Pdc_ref': 'P_th_c_ref [W]'}, inplace=True)
    para=para[['Manufacturer', 'Model', 'Date', 'Type', 'Subtype', 'Group',
       'Refrigerant', 'Mass of Refrigerant [kg]', 'SPL indoor [dBA]',
       'SPL outdoor [dBA]', 'PSB [W]', 'Climate', 'P_el_h_ref [W]',
       'P_th_h_ref [W]', 'COP_ref', 'P_el_c_ref [W]', 'P_th_c_ref [W]',
       'p1_P_th [1/°C]', 'p2_P_th [1/°C]', 'p3_P_th [-]', 'p4_P_th [1/°C]',
       'p1_P_el_h [1/°C]', 'p2_P_el_h [1/°C]', 'p3_P_el_h [-]', 'p4_P_el_h [1/°C]',
       'p1_COP [-]', 'p2_COP [-]', 'p3_COP [-]', 'p4_COP [-]', 'MAPE_P_el',
       'MAPE_COP', 'MAPE_P_th', 'p1_Pdc [1/°C]', 'p2_Pdc [1/°C]', 'p3_Pdc [-]',
       'p4_Pdc [1/°C]', 'p1_P_el_c [1/°C]', 'p2_P_el_c [1/°C]', 'p3_P_el_c [-]',
       'p4_P_el_c [1/°C]', 'p1_EER [-]', 'p2_EER [-]', 'p3_EER [-]',
       'p4_EER [-]']]
    para.to_csv('hplib_database.csv', encoding='utf-8', index=False)


def validation_relative_error_cooling():
    # Simulate every set point for every heat pump and save csv file
    df=pd.read_csv('../output/database_cooling_reduced.csv')
    i=0
    prev_model='first Model'
    while i<len(df): 
        Model=df.iloc[i,1]
        T_amb=df.iloc[i,2]
        T_in=df.iloc[i,2]
        T_out=df.iloc[i,3]
        P_th=df.iloc[i,6]
        P_el=df.iloc[i,7]
        COP=df.iloc[i,4]
        try:
            if prev_model!=Model:
                para=hpl.get_parameters(Model)
            results=hpl.simulate(T_in,T_out+5,para,T_amb,2)
            df.loc[i,'Pdc_sim']=-results.P_th[0]
            df.loc[i,'P_el_sim']=results.P_el[0]
            df.loc[i,'EER_sim']=results.EER[0]
            prev_model=Model
            i=i+1
        except:
            i=i+1
            pass
        
    # Relative error (RE) for every set point
    df['RE_Pdc']=(df['Pdc_sim']/df['Pdc [W]']-1)*100
    df['RE_P_el']=(df['P_el_sim']/df['P_el [W]']-1)*100
    df['RE_EER']=(df['EER_sim']/df['EER']-1)*100
    df.to_csv('../output/database_cooling_reduced_normalized_validation.csv', encoding='utf-8', index=False)


def validation_mape_cooling():
    #calculate the mean absolute percentage error for every heat pump and save in hplib_database.csv
    df=pd.read_csv('../output/database_cooling_reduced_normalized_validation.csv')
    para=pd.read_csv('hplib_database.csv', delimiter=',')
    para=para.loc[para['Model']!='Generic']
    Models = para['Model'].values.tolist()
    Models = list(dict.fromkeys(Models))
    mape_eer=[]
    mape_pel=[]
    mape_pdc=[]
    for model in Models:
        df_model=df.loc[df['Model']==model]
        mape_pdc.append((((df_model['Pdc [W]']-df_model['Pdc_sim']).abs())/df_model['Pdc [W]']*100).mean())
        mape_pel.append((((df_model['P_el [W]']-df_model['P_el_sim']).abs())/df_model['P_el [W]']*100).mean())
        mape_eer.append((((df_model['EER']-df_model['EER_sim']).abs())/df_model['EER']*100).mean())
    para['MAPE_P_el_cooling']=mape_pel
    para['MAPE_EER']=mape_eer
    para['MAPE_Pdc']=mape_pdc
    para.to_csv('hplib_database.csv', encoding='utf-8', index=False)
    