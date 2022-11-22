# Import packages
import os
import pandas as pd
import scipy
from scipy.optimize import curve_fit
import hplib as hpl
import pickle
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from csv import writer
# Functions

def import_keymark_data(i=0):
    #create folder to save csv files
    month=str(datetime.now().month)
    year=str(datetime.now().year)
    try:
        os.mkdir('../input/csv_'+month+'_'+year)
    except:
        pass
    #open main page of EHPA
    manufacturers_info = BeautifulSoup(requests.get('https://www.heatpumpkeymark.com/?type=109126').content, 'html.parser')
    #look for all manufacturers
    for manufacturer_info in manufacturers_info.find_all('td')[i:]:
        i+=1                                                       
        print('Progress: ',i, ' / ', len(manufacturers_info.find_all('td')),' In case of error: restart function with ', i, ' as input of function')        
        manufacturer=manufacturer_info.text
        models_info= BeautifulSoup(requests.get('https://www.heatpumpkeymark.com/'+manufacturer_info.a.get('href')).content, 'html.parser')
        #look for models:
        for model in models_info.find_all('td'):
            if model.text!=manufacturer:
                try:
                    model_info = BeautifulSoup(requests.get('https://www.heatpumpkeymark.com/'+model.a.get('href')).content, 'html.parser')
                except:
                    continue
                for info_col in model_info.find_all(class_='info-coll'):
                    if (info_col.find(class_='info-label').span.text)==('Refrigerant'):
                        ref = (info_col.find(class_='info-data').text.replace(' ','').replace('\n',''))
                    if (info_col.find(class_='info-label').span.text)==('Mass of Refrigerant'):
                        mass_of_ref = (info_col.find(class_='info-data').text.replace('\n',''))
                    if (info_col.find(class_='info-label').span.text)==('Certification Date'):
                        date = (info_col.find(class_='info-data').text.replace(' ','').replace('\n',''))
                #choose correct export method (csv preffered) and get basic data TODO
                for export_method in model_info.find_all('a'):
                    if export_method.text.startswith('Export'):
                        soup3 = BeautifulSoup(requests.get('https://www.heatpumpkeymark.com/'+export_method.get('href')).content,'html.parser')
                        #open Download link
                        for link in soup3.find_all('a'):
                            if link.text=='Download':
                                #write to csv
                                foldername='csv_'+month+'_'+year+'/'
                                filename=manufacturer+model.text.replace('/','_')
                                filename=filename.replace(' ','_')
                                csv_content = requests.get('https://www.heatpumpkeymark.com/'+link.get('href')).content
                                with open('../input/'+foldername+filename+'.csv', 'wb') as file:
                                    file.write(csv_content)
                                with open('../input/'+foldername+filename+'.csv', 'a') as f:
                                    f.write('"","Refrigerant","'+str(ref)+'","0","0","0","0"\r\n')
                                    f.write('"","Mass of Refrigerant","'+str(mass_of_ref)+'","0","0","0","0"\r\n')
                                    f.write('"","Date","'+str(date)+'","0","0","0","0"\r\n')
                                    f.write('"","Manufacturer","'+manufacturer+'","0","0","0","0"\r\n')
                                    f.write('"","Modelname","'+model.text+'","0","0","0","0"\r\n')

def combine_raw_csv():
    df_all=pd.DataFrame()
    manufacturers, models, titels, dates, types, refrigerants, mass_of_refrigerants, spl_indoors, spl_outdoors, eta, p_rated, scop, t_biv, tol, p_th_minus7, cop_minus7, p_th_2, cop_2, p_th_7, cop_7, p_th_12, cop_12, p_th_tbiv, cop_tbiv, p_th_tol, cop_tol, rated_airflows, wtols, poffs, ptos, psbs, pcks, supp_energy_types, p_sups, p_design_cools, seers, pdcs_35, eer_35, pdcs_30, eer_30, pdcs_25, eer_25, pdcs_20, eer_20, temperatures= ([] for i in range(45))
    lists=[manufacturers, models, titels, dates, types, refrigerants, mass_of_refrigerants, spl_indoors, spl_outdoors, eta, p_rated, scop, t_biv, tol, p_th_minus7, cop_minus7, p_th_2, cop_2, p_th_7, cop_7, p_th_12, cop_12, p_th_tbiv, cop_tbiv, p_th_tol, cop_tol, rated_airflows, wtols, poffs, ptos, psbs, pcks, supp_energy_types, p_sups, p_design_cools, seers, pdcs_35, eer_35, pdcs_30, eer_30, pdcs_25, eer_25, pdcs_20, eer_20, temperatures]
    values=['Manufacturer','Modelname','title','Date','application','Refrigerant','Mass of Refrigerant','EN12102_1_001','EN12102_1_002','EN14825_001','EN14825_002','EN14825_003','EN14825_004','EN14825_005','EN14825_008','EN14825_009','EN14825_010','EN14825_011','EN14825_012','EN14825_013','EN14825_014','EN14825_015','EN14825_016','EN14825_017','EN14825_018','EN14825_019','EN14825_020','EN14825_022','EN14825_023','EN14825_024','EN14825_025','EN14825_026','EN14825_027','EN14825_028','EN14825_030','EN14825_031','EN14825_032','EN14825_033','EN14825_034','EN14825_035','EN14825_036','EN14825_037','EN14825_038','EN14825_039']
    general_info=['Manufacturer','Modelname','Date','Refrigerant','Mass of Refrigerant']
    with os.scandir('../input/csv_11_2022') as dir1:
        for file in dir1:
            j=0 #j: start index; i: end index
            df=pd.read_csv(file)
            try:
                df.loc[df['varName']=='title']
            except:
                continue
            for model in range(1,len(df.loc[df['varName']=='title'])+1):
                try:
                    i=(df.loc[df['varName']=='title'].index[model])
                except:
                    i=len(df)
                #df1 is dataframe of each model
                df1=(df.iloc[j:i])
                j=i
                for temperature in ['low','high']:
                    #df2 is dataframe of each climate and temperature
                    df2=df1.loc[(df1['climate']>=3) & (df1['climate']<=4)]
                    if temperature=='low':
                        df2.loc[df2['temperature']==4,'temperature']=6
                        df2=df2.loc[(df2['temperature']==6)]
                        temperatures.append('low')
                    else:
                        df2.loc[(df2['temperature']==5),'temperature']=7
                        df2=df2.loc[(df2['temperature']==7)]
                        temperatures.append('high')
                    for value, lst in zip(values,lists):
                        if value in general_info:
                            read_value=df.loc[df['varName']==value,'value'].values[0]
                        elif (value=='title') or (value=='application'):
                            read_value=df1.loc[df1['varName']==value,'value'].values[0]
                        else:
                            try:
                                read_value=df2.loc[df2['varName']==value,'value'].values[0]
                            except:
                                read_value=''
                        lst.append(read_value)
    df_all['manufacturers']=manufacturers
    df_all['models']=models
    df_all['titels']=titels
    df_all['dates']=dates
    df_all['types']=types
    df_all['refrigerants']=refrigerants
    df_all['mass_of_refrigerants']=mass_of_refrigerants
    df_all['spl_indoor']=spl_indoors
    df_all['spl_outdoor']=spl_outdoors
    df_all['eta']=eta
    df_all['p_rated']=p_rated
    df_all['scop']=scop
    df_all['t_biv']=t_biv
    df_all['tol']=tol
    df_all['p_th_minus7']=p_th_minus7
    df_all['cop_minus7']=cop_minus7
    df_all['p_th_2']=p_th_2
    df_all['cop_2']=cop_2
    df_all['p_th_7']=p_th_7
    df_all['cop_7']=cop_7
    df_all['p_th_12']=p_th_12
    df_all['cop_12']=cop_12
    df_all['p_th_tbiv']=p_th_tbiv
    df_all['cop_tbiv']=cop_tbiv
    df_all['p_th_tol']=p_th_tol
    df_all['cop_tol']=cop_tol
    df_all['rated_airflows']=rated_airflows
    df_all['wtols']=wtols
    df_all['poffs']=poffs
    df_all['ptos']=ptos
    df_all['psbs']=psbs
    df_all['pcks']=pcks
    df_all['supp_energy_types']=supp_energy_types
    df_all['p_sups']=p_sups
    df_all['p_design_cools']=p_design_cools
    df_all['seers']=seers
    df_all['pdcs_35']=pdcs_35
    df_all['eer_35']=eer_35
    df_all['pdcs_30']=pdcs_30
    df_all['eer_30']=eer_30
    df_all['pdcs_25']=pdcs_25
    df_all['eer_25']=eer_25
    df_all['pdcs_20']=pdcs_20
    df_all['eer_20']=eer_20
    df_all['temperatures']=temperatures
    df_all.to_csv(r'../output/database.csv', index=False)

def reduce_heating_data():
    # reduce the hplib_database_heating to a specific climate measurement series (average, warm, cold)
    # delete redundant entries
    # climate = average, warm or cold
    df=pd.read_csv('../output/database.csv')
    df=df.loc[df['eta'].isna()==0]
    df=df.drop_duplicates(subset=['eta', 'p_rated',
        'scop', 't_biv', 'tol', 'p_th_minus7', 'cop_minus7', 'p_th_2', 'cop_2',
        'p_th_7', 'cop_7', 'p_th_12', 'cop_12', 'p_th_tbiv', 'cop_tbiv',
        'p_th_tol', 'cop_tol', 'wtols', 'poffs', 'ptos',
        'psbs', 'pcks', 'supp_energy_types', 'p_sups', 'p_design_cools',
        'seers', 'pdcs_35', 'eer_35', 'pdcs_30', 'eer_30', 'pdcs_25', 'eer_25',
        'pdcs_20', 'eer_20', 'temperatures'])#types?
    df.sort_values(by=['manufacturers','models'], inplace=True,key=lambda col: col.str.lower())
    df=df.loc[df['temperatures']=='low'].merge(df.loc[df['temperatures']=='high'],on='titels')
    df=df[['manufacturers_x', 'models_x', 'titels', 'dates_x', 'types_x','refrigerants_x', 'mass_of_refrigerants_x', 'spl_indoor_x','spl_outdoor_x', 'eta_x', 'p_rated_x', 'scop_x', 't_biv_x', 'tol_x','p_th_minus7_x', 'cop_minus7_x', 'p_th_2_x', 'cop_2_x', 'p_th_7_x','cop_7_x', 'p_th_12_x', 'cop_12_x', 'p_th_tbiv_x', 'cop_tbiv_x','p_th_tol_x', 'cop_tol_x', 'rated_airflows_x', 'wtols_x', 'poffs_x','ptos_x', 'psbs_x', 'pcks_x', 'supp_energy_types_x', 'p_sups_x','p_design_cools_x', 'seers_x', 'pdcs_35_x', 'eer_35_x', 'pdcs_30_x','eer_30_x', 'pdcs_25_x', 'eer_25_x', 'pdcs_20_x', 'eer_20_x', 'spl_indoor_y','spl_outdoor_y', 'eta_y', 'p_rated_y', 'p_th_minus7_y', 'cop_minus7_y', 'p_th_2_y', 'cop_2_y', 'p_th_7_y','cop_7_y', 'p_th_12_y', 'cop_12_y', 'p_th_tbiv_y', 'cop_tbiv_y','p_th_tol_y', 'cop_tol_y', 'rated_airflows_y', 'p_sups_y','p_design_cools_y', 'seers_y', 'pdcs_35_y', 'eer_35_y', 'pdcs_30_y','eer_30_y', 'pdcs_25_y', 'eer_25_y', 'pdcs_20_y', 'eer_20_y']]
    df.rename(columns={'manufacturers_x': 'manufacturers','models_x': 'models','titels': 'titel','dates_x': 'dates','types_x': 'types','refrigerants_x': 'refrigerants','mass_of_refrigerants_x': 'mass_of_refrigerants', 'spl_indoor_x': 'spl_indoor_l','spl_outdoor_x': 'spl_outdoor_l', 'eta_x': 'eta_l', 'p_rated_x': 'p_rated_l', 'scop_x': 'scop_l', 't_biv_x': 't_biv', 'tol_x': 'tol','p_th_minus7_x': 'p_th_minus7_l', 'cop_minus7_x': 'cop_minus7_l', 'p_th_2_x': 'p_th_2_l', 'cop_2_x': 'cop_2_l', 'p_th_7_x': 'p_th_7_l','cop_7_x': 'cop_7_l', 'p_th_12_x': 'p_th_12_l', 'cop_12_x': 'cop_12_l', 'p_th_tbiv_x': 'p_th_tbiv_l', 'cop_tbiv_x': 'cop_tbiv_l','p_th_tol_x': 'p_th_tol_l', 'cop_tol_x': 'cop_tol_l', 'rated_airflows_x': 'rated_airflows_l', 'wtols_x': 'wtols', 'poffs_x': 'poffs','ptos_x': 'ptos', 'psbs_x': 'psbs', 'pcks_x': 'pcks', 'supp_energy_types_x': 'supp_energy_types', 'p_sups_x': 'p_sups_l','p_design_cools_x': 'p_design_cools_l', 'seers_x': 'seers_l', 'pdcs_35_x': 'pdcs_35_l', 'eer_35_x': 'eer_35_l','pdcs_30_x': 'pdcs_30_l','eer_30_x': 'eer_30_l', 'pdcs_25_x': 'pdcs_25_l', 'eer_25_x': 'eer_25_l', 'pdcs_20_x': 'pdcs_20_l','eer_20_x': 'eer_20_l', 'spl_indoor_y': 'spl_indoor_h','spl_outdoor_y': 'spl_outdoor_h', 'eta_y': 'eta_h', 'p_rated_y': 'p_rated_h', 'scop_y': 'scop_h', 'p_th_minus7_y': 'p_th_minus7_h', 'cop_minus7_y': 'cop_minus7_h', 'p_th_2_y': 'p_th_2_h', 'cop_2_y': 'cop_2_h', 'p_th_7_y': 'p_th_7_h','cop_7_y': 'cop_7_h', 'p_th_12_y': 'p_th_12_h', 'cop_12_y': 'cop_12_h', 'p_th_tbiv_y': 'p_th_tbiv_h', 'cop_tbiv_y': 'cop_tbiv_h','p_th_tol_y': 'p_th_tol_h', 'cop_tol_y': 'cop_tol_h', 'rated_airflows_y': 'rated_airflows_h', 'p_sups_y': 'p_sups_h','p_design_cools_y': 'p_design_cools_h', 'seers_y': 'seers_h', 'pdcs_35_y': 'pdcs_35_h', 'eer_35_y': 'eer_35_h', 'pdcs_30_y': 'pdcs_30_h','eer_30_y': 'eer_30_h', 'pdcs_25_y': 'pdcs_25_h', 'eer_25_y': 'eer_25_h', 'pdcs_20_y': 'pdcs_20_h', 'eer_20_y': 'eer_20_h'},inplace=True)
    df.to_csv('../output/database_reduced.csv',index=False)


def normalize_data():
    df=pd.read_csv('../output/database_reduced.csv')
    #change kW to W
    df['p_th_minus7_l']=df['p_th_minus7_l']*1000
    df['p_th_2_l']=df['p_th_2_l']*1000
    df['p_th_7_l']=df['p_th_7_l']*1000
    df['p_th_12_l']=df['p_th_12_l']*1000
    df['p_th_tbiv_l']=df['p_th_tbiv_l']*1000
    df['p_th_tol_l']=df['p_th_tol_l']*1000
    df['pdcs_35_l']=df['pdcs_35_l']*1000
    df['pdcs_30_l']=df['pdcs_30_l']*1000
    df['pdcs_25_l']=df['pdcs_25_l']*1000
    df['pdcs_20_l']=df['pdcs_20_l']*1000
    df['p_th_minus7_h']=df['p_th_minus7_h']*1000
    df['p_th_2_h']=df['p_th_2_h']*1000
    df['p_th_7_h']=df['p_th_7_h']*1000
    df['p_th_12_h']=df['p_th_12_h']*1000
    df['p_th_tbiv_h']=df['p_th_tbiv_h']*1000
    df['p_th_tol_h']=df['p_th_tol_h']*1000
    df['pdcs_35_h']=df['pdcs_35_h']*1000
    df['pdcs_30_h']=df['pdcs_30_h']*1000
    df['pdcs_25_h']=df['pdcs_25_h']*1000
    df['pdcs_20_h']=df['pdcs_20_h']*1000
    # add P_el
    df['p_el_minus7_l'] = df['p_th_minus7_l'] / df['cop_minus7_l']
    df['p_el_2_l'] = df['p_th_2_l'] / df['cop_2_l']
    df['p_el_7_l'] = df['p_th_7_l'] / df['cop_7_l']
    df['p_el_12_l'] = df['p_th_12_l'] / df['cop_12_l']
    df['p_el_tbiv_l'] = df['p_th_tbiv_l'] / df['cop_tbiv_l']
    df['p_el_tol_l'] = df['p_th_tol_l'] / df['cop_tol_l']
    df['p_el_35_l'] = df['pdcs_35_l'] / df['eer_35_l']
    df['p_el_30_l'] = df['pdcs_30_l'] / df['eer_30_l']
    df['p_el_25_l'] = df['pdcs_25_l'] / df['eer_25_l']
    df['p_el_20_l'] = df['pdcs_20_l'] / df['eer_20_l']
    df['p_el_minus7_h'] = df['p_th_minus7_h'] / df['cop_minus7_h']
    df['p_el_2_h'] = df['p_th_2_h'] / df['cop_2_h']
    df['p_el_7_h'] = df['p_th_7_h'] / df['cop_7_h']
    df['p_el_12_h'] = df['p_th_12_h'] / df['cop_12_h']
    df['p_el_tbiv_h'] = df['p_th_tbiv_h'] / df['cop_tbiv_h']
    df['p_el_tol_h'] = df['p_th_tol_h'] / df['cop_tol_h']
    df['p_el_35_h'] = df['pdcs_35_h'] / df['eer_35_h']
    df['p_el_30_h'] = df['pdcs_30_h'] / df['eer_30_h']
    df['p_el_25_h'] = df['pdcs_25_h'] / df['eer_25_h']
    df['p_el_20_h'] = df['pdcs_20_h'] / df['eer_20_h']
    df['p_el_minus7_l_n'] = df['p_el_minus7_l'] / df['p_el_minus7_h']
    df['p_el_2_l_n'] = df['p_el_2_l'] / df['p_el_minus7_h']
    df['p_el_7_l_n'] = df['p_el_7_l'] / df['p_el_minus7_h']
    df['p_el_12_l_n'] = df['p_el_12_l'] / df['p_el_minus7_h']
    df['p_el_tbiv_l_n'] = df['p_el_tbiv_l'] / df['p_el_minus7_h']
    df['p_el_tol_l_n'] = df['p_el_tol_l'] / df['p_el_minus7_h']
    df['p_el_35_l_n'] = df['p_el_35_l'] / df['p_el_35_l']
    df['p_el_30_l_n'] = df['p_el_30_l'] / df['p_el_35_l']
    df['p_el_25_l_n'] = df['p_el_25_l'] / df['p_el_35_l']
    df['p_el_20_l_n'] = df['p_el_20_l'] / df['p_el_35_l']
    df['p_el_minus7_h_n'] = df['p_el_minus7_h'] / df['p_el_minus7_h']
    df['p_el_2_h_n'] = df['p_el_2_h'] / df['p_el_minus7_h']
    df['p_el_7_h_n'] = df['p_el_7_h'] / df['p_el_minus7_h']
    df['p_el_12_h_n'] = df['p_el_12_h'] / df['p_el_minus7_h']
    df['p_el_tbiv_h_n'] = df['p_el_tbiv_h'] / df['p_el_minus7_h']
    df['p_el_tol_h_n'] = df['p_el_tol_h'] / df['p_el_minus7_h']
    df['p_el_35_h_n'] = df['p_el_35_h'] / df['p_el_35_l']
    df['p_el_30_h_n'] = df['p_el_30_h'] / df['p_el_35_l']
    df['p_el_25_h_n'] = df['p_el_25_h'] / df['p_el_35_l']
    df['p_el_20_h_n'] = df['p_el_20_h'] / df['p_el_35_l']
    df=df.loc[df['cop_minus7_l']!=1]
    df=df[['manufacturers', 'models', 'titel', 'dates', 'types', 'refrigerants','mass_of_refrigerants', 'spl_indoor_l', 'spl_outdoor_l', 'eta_l', 'p_rated_l', 'scop_l', 't_biv', 'tol', 'p_th_minus7_l', 'cop_minus7_l', 'p_el_minus7_l', 'p_th_2_l', 'cop_2_l', 'p_el_2_l', 'p_th_7_l', 'cop_7_l', 'p_el_7_l', 'p_th_12_l', 'cop_12_l', 'p_el_12_l',  'p_th_tbiv_l', 'cop_tbiv_l', 'p_el_tbiv_l', 'p_th_tol_l', 'cop_tol_l', 'p_el_tol_l', 'rated_airflows_l', 'wtols', 'poffs', 'ptos', 'psbs', 'pcks', 'supp_energy_types', 'p_sups_l', 'p_design_cools_l', 'seers_l', 'pdcs_35_l', 'eer_35_l', 'p_el_35_l', 'pdcs_30_l', 'eer_30_l', 'p_el_30_l', 'pdcs_25_l', 'eer_25_l', 'p_el_25_l', 'pdcs_20_l', 'eer_20_l', 'p_el_20_l', 'spl_indoor_h', 'spl_outdoor_h', 'eta_h', 'p_rated_h', 'p_th_minus7_h', 'cop_minus7_h', 'p_el_minus7_h', 'p_th_2_h', 'cop_2_h', 'p_el_2_h', 'p_th_7_h', 'cop_7_h', 'p_el_7_h', 'p_th_12_h', 'cop_12_h', 'p_el_12_h', 'p_th_tbiv_h', 'cop_tbiv_h', 'p_el_tbiv_h', 'p_th_tol_h', 'cop_tol_h', 'p_el_tol_h', 'rated_airflows_h', 'p_sups_h', 'p_design_cools_h', 'seers_h', 'pdcs_35_h', 'eer_35_h', 'p_el_35_h', 'pdcs_30_h', 'eer_30_h', 'p_el_30_h', 'pdcs_25_h', 'eer_25_h', 'p_el_25_h', 'pdcs_20_h', 'eer_20_h', 'p_el_20_h', 'p_el_minus7_l_n', 'p_el_2_l_n', 'p_el_7_l_n', 'p_el_12_l_n', 'p_el_tbiv_l_n', 'p_el_tol_l_n', 'p_el_35_l_n', 'p_el_30_l_n', 'p_el_25_l_n', 'p_el_20_l_n', 'p_el_minus7_h_n', 'p_el_2_h_n', 'p_el_7_h_n', 'p_el_12_h_n', 'p_el_tbiv_h_n', 'p_el_tol_h_n', 'p_el_35_h_n', 'p_el_30_h_n', 'p_el_25_h_n', 'p_el_20_h_n']]
    # add second (+18/+23 °C) point for cooling based on other heat pumps 
    df.loc[(df['eer_20_l'].isna()==0)&(df['p_el_35_h_n'].isna()),'eer_20_h'] = df.loc[(df['eer_20_l'].isna()==0)&(df['p_el_35_h_n'].isna()),'eer_20_l']*(df[df['p_el_35_h_n'].isna()==0]['eer_20_h']/df[df['p_el_35_h_n'].isna()==0]['eer_20_l']).unique().mean()
    df.loc[(df['eer_25_l'].isna()==0)&(df['p_el_35_h_n'].isna()),'eer_25_h'] = df.loc[(df['eer_25_l'].isna()==0)&(df['p_el_35_h_n'].isna()),'eer_25_l']*(df[df['p_el_35_h_n'].isna()==0]['eer_25_h']/df[df['p_el_35_h_n'].isna()==0]['eer_25_l']).unique().mean()
    df.loc[(df['eer_30_l'].isna()==0)&(df['p_el_35_h_n'].isna()),'eer_30_h'] = df.loc[(df['eer_30_l'].isna()==0)&(df['p_el_35_h_n'].isna()),'eer_30_l']*(df[df['p_el_35_h_n'].isna()==0]['eer_30_h']/df[df['p_el_35_h_n'].isna()==0]['eer_30_l']).unique().mean()
    df.loc[(df['eer_35_l'].isna()==0)&(df['p_el_35_h_n'].isna()),'eer_35_h'] = df.loc[(df['eer_35_l'].isna()==0)&(df['p_el_35_h_n'].isna()),'eer_35_l']*(df[df['p_el_35_h_n'].isna()==0]['eer_35_h']/df[df['p_el_35_h_n'].isna()==0]['eer_35_l']).unique().mean()

    df.loc[(df['p_el_20_l_n'].isna()==0)&(df['p_el_35_h_n'].isna()),'p_el_20_h_n'] = df[df['p_el_35_h_n'].isna()==0]['p_el_20_h_n'].unique().mean()
    df.loc[(df['p_el_25_l_n'].isna()==0)&(df['p_el_35_h_n'].isna()),'p_el_25_h_n'] = df[df['p_el_35_h_n'].isna()==0]['p_el_25_h_n'].unique().mean()
    df.loc[(df['p_el_30_l_n'].isna()==0)&(df['p_el_35_h_n'].isna()),'p_el_30_h_n'] = df[df['p_el_35_h_n'].isna()==0]['p_el_30_h_n'].unique().mean()
    df.loc[(df['p_el_35_l_n'].isna()==0)&(df['p_el_35_h_n'].isna()),'p_el_35_h_n'] = df[df['p_el_35_h_n'].isna()==0]['p_el_35_h_n'].unique().mean()
    df.to_csv(r'../output/database_reduced_normalized.csv', encoding='utf-8', index=False)


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
    unique_values = pd.unique(df['p3_P_el_h [-]']).tolist()
    for values in unique_values:
        modelnames = df.loc[df['p3_P_el_h [-]'] == values, ['Model']]
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
    