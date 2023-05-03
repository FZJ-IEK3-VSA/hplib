import os
import pandas as pd
import numpy as np
import scipy
import hplib as hpl
import pickle
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import shutil


# get path to the current file
THIS_FOLDER_PATH = os.path.dirname(os.path.abspath(__file__))

# get path to the input folder
INPUT_FOLDER_PATH = os.path.dirname(os.path.abspath(__file__)) + '/../input/' 

# get path to the output folder
OUTPUT_FOLDER_PATH = os.path.dirname(os.path.abspath(__file__)) + '/../output/'

# Functions
def import_keymark_data(
        target_folder='csv',
        manufacturer_url='https://www.heatpumpkeymark.com/?type=109126',
        base_url='https://www.heatpumpkeymark.com/',
        i=0
    ):
    """
    Downloads the raw .csv keymark files from the keymark website.

    Parameters
    ----------
    target_folder : str
        Name of the folder where the raw csv files are stored.
    manufacturer_url : str
        URL where the manufacturers are listed on the keymark website.
    base_url : str
        Base URL of the keymark website.
    i : int
        Number of the manufacturer to start with.
    """
    already_downloaded = []
    no_csv_file_available = []


    #open main page of EHPA
    manufacturers_info = BeautifulSoup(requests.get(manufacturer_url).content, 'html.parser')
    
    #look for all manufacturers and progress from defined i
    number_of_manufacturers=len(manufacturers_info.find_all('td'))

    for manufacturer_info in manufacturers_info.find_all('td')[i:]:
        i+=1 

        # manufacturer name
        manufacturer=manufacturer_info.text

        # TODO read manufacturer origin country

        # open manufacturer page
        manufacturer_models= BeautifulSoup(requests.get(base_url + manufacturer_info.a.get('href')).content, 'html.parser')

        print('Progress: ',i, ' / ', number_of_manufacturers,' In case of error: restart function with ', i-1, ' as input of function')       

        # every model is one row in the table - tr and skip header
        for model in manufacturer_models.find_all('tr')[1:]:
            # get the first column
            model_url = model.find_all('a')[0]

            filename=manufacturer+model_url.text.replace('/','_')
            filename=filename.replace(' ','_')

            # download only non-existing files
            if not os.path.isfile(
                INPUT_FOLDER_PATH + target_folder 
                + '/' + filename + '.csv'
                ):
                
                # open model info page
                model_info = BeautifulSoup(requests.get(base_url + model_url.get('href')).content, 'html.parser')

                # retrieve supplementary values
                for info_col in model_info.find_all(class_='info-coll'):
                    if (info_col.find(class_='info-label').span.text)==('Refrigerant'):
                        ref = (info_col.find(class_='info-data').text.replace(' ','').replace('\n','').replace('\r',''))
                    if (info_col.find(class_='info-label').span.text)==('Mass of Refrigerant'):
                        mass_of_ref = (info_col.find(class_='info-data').text.replace('\n',''))
                    if (info_col.find(class_='info-label').span.text)==('Certification Date'):
                        date = (info_col.find(class_='info-data').text.replace(' ','').replace('\n','').replace('\r',''))
                    if (info_col.find(class_='info-label').span.text)==('Heat Pump Type'):
                        type = (info_col.find(class_='info-data').text.replace('\n','')[13:-9])
                    if (info_col.find(class_='info-label').span.text)==('Driving energy'):
                        energy = (info_col.find(class_='info-data').text.replace('\n','')[13:-9])

                # move to download page
                download_page_url = model_info.find('a',string="Export model CSV")
                if download_page_url:
                    download_page = BeautifulSoup(requests.get(base_url+download_page_url.get('href')).content,'html.parser')
                    csv_download_url = download_page.find('a',string="Download")
                    csv_content = requests.get(base_url + csv_download_url.get('href')).content
                    with open(INPUT_FOLDER_PATH +target_folder + '/' +filename+'.csv', 'wb') as file:
                        file.write(csv_content)

                    # add supplementary values to csv
                    with open(INPUT_FOLDER_PATH +target_folder + '/' +filename+'.csv', 'a') as f:
                        f.write('"","Refrigerant","'+str(ref)+'","0","0","0","0"\r\n')
                        f.write('"","Mass of Refrigerant","'+str(mass_of_ref)+'","0","0","0","0"\r\n')
                        f.write('"","Date","'+str(date)+'","0","0","0","0"\r\n')
                        f.write('"","Manufacturer","'+manufacturer+'","0","0","0","0"\r\n')
                        f.write('"","Modelname","'+model_url.text+'","0","0","0","0"\r\n')
                        f.write('"","Type","'+type+'","0","0","0","0"\r\n')
                        f.write('"","Energy","'+energy+'","0","0","0","0"\r\n')
                else:
                    no_csv_file_available.append(filename)

            else:
                already_downloaded.append(filename)

    list_to_file(no_csv_file_available, INPUT_FOLDER_PATH +target_folder + '/__no_csv_file_available.txt')
    list_to_file(already_downloaded, INPUT_FOLDER_PATH +target_folder + '/__already_downloaded.txt')



def list_to_file(list, file_path):
    """
    Writes a list to a file.

    Parameters
    ----------
    list : list
        List to be written to file.
    file_path : str
        Path to the file.
    """
    with open(file_path, 'w') as f:
        for line in list:
            f.write(f"{line}\n")


def combine_raw_csv(foldername, target_filename = "database.csv"):
    df_all=pd.DataFrame()
    manufacturers, models, titels, dates, types, refrigerants, mass_of_refrigerants, supply_energy, spl_indoors, spl_outdoors, eta, p_rated, scop, t_biv, tol, p_th_minus7, cop_minus7, p_th_2, cop_2, p_th_7, cop_7, p_th_12, cop_12, p_th_tbiv, cop_tbiv, p_th_tol, cop_tol, rated_airflows, wtols, poffs, ptos, psbs, pcks, supp_energy_types, p_sups, p_design_cools, seers, pdcs_35, eer_35, pdcs_30, eer_30, pdcs_25, eer_25, pdcs_20, eer_20, temperatures= ([] for i in range(46))
    lists=[manufacturers, models, titels, dates, types, refrigerants, mass_of_refrigerants, supply_energy, spl_indoors, spl_outdoors, eta, p_rated, scop, t_biv, tol, p_th_minus7, cop_minus7, p_th_2, cop_2, p_th_7, cop_7, p_th_12, cop_12, p_th_tbiv, cop_tbiv, p_th_tol, cop_tol, rated_airflows, wtols, poffs, ptos, psbs, pcks, supp_energy_types, p_sups, p_design_cools, seers, pdcs_35, eer_35, pdcs_30, eer_30, pdcs_25, eer_25, pdcs_20, eer_20, temperatures]
    values=['Manufacturer','Modelname','title','Date','application','Refrigerant','Mass of Refrigerant','Energy','EN12102_1_001','EN12102_1_002','EN14825_001','EN14825_002','EN14825_003','EN14825_004','EN14825_005','EN14825_008','EN14825_009','EN14825_010','EN14825_011','EN14825_012','EN14825_013','EN14825_014','EN14825_015','EN14825_016','EN14825_017','EN14825_018','EN14825_019','EN14825_020','EN14825_022','EN14825_023','EN14825_024','EN14825_025','EN14825_026','EN14825_027','EN14825_028','EN14825_030','EN14825_031','EN14825_032','EN14825_033','EN14825_034','EN14825_035','EN14825_036','EN14825_037','EN14825_038','EN14825_039']
    general_info=['Manufacturer','Modelname','Date','Refrigerant','Mass of Refrigerant', 'Energy']
    with os.scandir(THIS_FOLDER_PATH + '/../input/'+ foldername) as dir1:
        # loop over every file in the folder
        for file in dir1:
            j=0 #j: start index; i: end index

            df=pd.read_csv(file)

            # loop over every model in the file - it always starts with a title
            for model in range(1,len(df.loc[df['varName']=='title'])+1):
                try:
                    i=(df.loc[df['varName']=='title'].index[model])
                except KeyError:
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
    df_all['supply_energy']=supply_energy
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
    df_all.to_csv(r'../output/' + target_filename, index=False)



VARIABLE_MAPPING = {
    "EN12102_1_001": "spl_indoor",
    "EN12102_1_002": "spl_outdoor",
    "EN14825_001": 	"eta",
    "EN14825_002": 	"p_rated",
    "EN14825_003": 	"scop",
    "EN14825_004": 	"t_biv",
    "EN14825_005": 	"tol",
    "EN14825_008": 	"p_th_minus7",
    "EN14825_009": 	"cop_minus7",
    "EN14825_010": 	"p_th_2",
    "EN14825_011": 	"cop_2",
    "EN14825_012": 	"p_th_7",
    "EN14825_013": 	"cop_7",
    "EN14825_014": 	"p_th_12",
    "EN14825_015": 	"cop_12",
    "EN14825_016": 	"p_th_tbiv",
    "EN14825_017": 	"cop_tbiv",
    "EN14825_018": 	"p_th_tol",
    "EN14825_019": 	"cop_tol",
    "EN14825_020": 	"rated_airflows",
    "EN14825_022": 	"wtols",
    "EN14825_023": 	"poffs",
    "EN14825_024": 	"ptos",
    "EN14825_025": 	"psbs",
    "EN14825_026": 	"pcks",
    "EN14825_027": 	"supp_energy_types",
    "EN14825_028": 	"p_sups",
    "EN14825_029": 	"P_he",
    "EN14825_030": 	"p_design_cools",
    "EN14825_031": 	"seers",
    "EN14825_032": 	"pdcs_35",
    "EN14825_033": 	"eer_35",
    "EN14825_034": 	"pdcs_30",
    "EN14825_035": 	"eer_30",
    "EN14825_036": 	"pdcs_25",
    "EN14825_037": 	"eer_25",
    "EN14825_038": 	"pdcs_20",
    "EN14825_039": 	"eer_20",
    "EN14825_041":  "E_cooling",
}

MANUALLY_ADDED_VARIABLES = [
    "Date", "Manufacturer", "Modelname", "Type", "Energy",
    "Refrigerant", "Mass of Refrigerant"
]

def merge_raw_csv(
        foldername, 
        filename_performance = "performance_data.csv",
        filename_meta = "meta_data.csv",
        filetype = "csv"
    ):
    """
    Merge all .csv files in a folder into two .csv files.
    One for the performance data depending on the operation 
    conditions and one for the meta data about the heatpump
    model itself.

    Parameters
    ----------
    foldername : str
        Name of the folder in which the .csv files are located.
    filename_performance : str
        Name of the output file for the performance data.
    filename_meta : str
        Name of the output file for the meta data.
    filetype: str
        Type of the output file. Either .csv or .json.
    """

    operation_data = {}
    meta_data = {}

    no_data = []
    
    with os.scandir(INPUT_FOLDER_PATH + foldername) as dir1:
        # loop over every file in the folder
        for file in dir1:
            j=0 #j: start index; i: end index

            if file.name.endswith(".csv"):
                df = pd.read_csv(file)
            
                # skip empty .csv files 
                if 'varName' not in df.columns:
                    no_data.append(file.name)
                else:
                    # first, extract the general information
                    df_raw = df[~df['varName'].isin(MANUALLY_ADDED_VARIABLES)]

                    # manual values from web page
                    general_info = df[df['varName'].isin(MANUALLY_ADDED_VARIABLES)].set_index('varName')['value'].to_dict()
                    
                    # inside a .csv can be multiple models
                    for model_index in df_raw["modelID"].unique():
                        
                        # dataframe of each model
                        # if the index is NaN, the model is not defined and
                        # the csv containts a single model
                        if not pd.isnull(model_index):
                            model_data = df_raw[df_raw["modelID"] == model_index]
                        else:
                            model_data = df_raw[df_raw["modelID"].isnull()]

                        # retrieve operation independent meta data
                        csv_info = model_data[model_data['info'] == 1].set_index('varName')['value'].to_dict()

                        # define an index for every model
                        id = general_info['Manufacturer'] + ' ' + csv_info['title']

                        # merge general info and operation independent meta data
                        meta_data[id] = csv_info
                        meta_data[id].update(general_info)

                        # retrieve operation dependent data
                        model_operation = model_data[model_data['info'] == 2]
                        model_operation.drop(columns=['modelID', 'indoorUnittype',
                                                    'hpType','info'],
                                            inplace=True)

                        # filter out the chosen values
                        model_operation = model_operation[model_operation['varName'].isin(VARIABLE_MAPPING.keys())]

                        # first remove duplicates
                        model_operation = model_operation.drop_duplicates(['varName', 'temperature', 'climate'])

                        # TODO identify where duplicates occured and why

                        # set operation conditions as index
                        model_operation.set_index(['varName','temperature', 'climate'], 
                                                inplace=True)
                        

                        # set values as columns
                        model_operation = model_operation['value'].unstack(level=0)

                        # rename columns
                        model_operation.rename(columns=VARIABLE_MAPPING, inplace=True)

                        # and add to the operation data
                        operation_data[id] = model_operation

    # makes a dataframe from the dictionary
    df_operation = pd.concat(operation_data, names=['id', 'temperature', 'climate'])

    # makes a dataframe from the dictionary
    df_meta = pd.DataFrame.from_dict(meta_data, orient='index')


    if filetype == "json":
        # and saves it to a .json
        df_operation.T.to_json(OUTPUT_FOLDER_PATH + filename_performance)

        # and saves it to a .json
        df_meta.T.to_json(OUTPUT_FOLDER_PATH + filename_meta)
    elif filetype == "csv":
        # and saves it to a .csv
        df_operation.to_csv(OUTPUT_FOLDER_PATH + filename_performance, sep=';')

        # and saves it to a .csv
        df_meta.to_csv(OUTPUT_FOLDER_PATH + filename_meta, sep=';')
    else:
        raise ValueError("filetype must be either csv or json")

    list_to_file(no_data, INPUT_FOLDER_PATH + foldername + '/__empty_csv_files.txt')
    
    return df_operation, df_meta

def read_performance_data(filename):
    """
    Read the performance data from a .csv file with the
    heatpump id, the temperature and the climate as index.

    Parameters
    ----------
    filename : str
        Name of the .csv file.

    Returns
    -------
    df : pandas.DataFrame
        The performance data.
    """
    df = pd.read_csv(OUTPUT_FOLDER_PATH +filename, index_col=[0,1,2], sep=';')
    df.index.names = ['id', 'temperature', 'climate']
    return df

def read_meta_data(filename):
    """
    Read the meta data (type etc.) from a .csv file with the
    heatpump id as index.

    Parameters
    ----------
    filename : str
        Name of the .csv file.

    Returns
    -------
    df : pandas.DataFrame
        The meta data.
    """
    df = pd.read_csv(OUTPUT_FOLDER_PATH +filename, index_col=[0], sep=';')
    df.index.names = ['id']
    return df

def reduce_heating_data():
    # reduce the hplib_database_heating to a specific climate measurement series (average, warm, cold)
    # delete redundant entries
    # climate = average, warm or cold
    df=pd.read_csv('../output/database.csv')
    df=df.loc[df['eta'].isna()==0]
    #df=df.drop_duplicates(subset=['p_rated', 't_biv', 'tol', 'p_th_minus7', 'cop_minus7', 'p_th_2', 'cop_2',
    #    'p_th_7', 'cop_7', 'p_th_12', 'cop_12', 'p_th_tbiv', 'cop_tbiv',
    #    'p_th_tol', 'cop_tol', 'wtols', 'poffs', 'ptos',
    #    'psbs', 'pcks', 'supp_energy_types', 'p_sups', 'p_design_cools',
    #    'pdcs_35', 'eer_35', 'pdcs_30', 'eer_30', 'pdcs_25', 'eer_25',
    #    'pdcs_20', 'eer_20', 'temperatures'])#types?
    df.sort_values(by=['manufacturers','models'], inplace=True,key=lambda col: col.str.lower())
    df=df.loc[df['temperatures']=='low'].merge(df.loc[df['temperatures']=='high'],on='titels')
    df=df[['manufacturers_x', 'models_x', 'titels', 'dates_x', 'types_x','refrigerants_x', 'mass_of_refrigerants_x', 'spl_indoor_x','spl_outdoor_x', 'eta_x', 'p_rated_x', 'scop_x', 't_biv_x', 'tol_x','p_th_minus7_x', 'cop_minus7_x', 'p_th_2_x', 'cop_2_x', 'p_th_7_x','cop_7_x', 'p_th_12_x', 'cop_12_x', 'p_th_tbiv_x', 'cop_tbiv_x','p_th_tol_x', 'cop_tol_x', 'rated_airflows_x', 'wtols_x', 'poffs_x','ptos_x', 'psbs_x', 'pcks_x', 'supp_energy_types_x', 'p_sups_x','p_design_cools_x', 'seers_x', 'pdcs_35_x', 'eer_35_x', 'pdcs_30_x','eer_30_x', 'pdcs_25_x', 'eer_25_x', 'pdcs_20_x', 'eer_20_x', 'spl_indoor_y','spl_outdoor_y', 'eta_y', 'p_rated_y', 'p_th_minus7_y', 'cop_minus7_y', 'p_th_2_y', 'cop_2_y', 'p_th_7_y','cop_7_y', 'p_th_12_y', 'cop_12_y', 'p_th_tbiv_y', 'cop_tbiv_y','p_th_tol_y', 'cop_tol_y', 'rated_airflows_y', 'p_sups_y','p_design_cools_y', 'seers_y', 'pdcs_35_y', 'eer_35_y', 'pdcs_30_y','eer_30_y', 'pdcs_25_y', 'eer_25_y', 'pdcs_20_y', 'eer_20_y']]
    df.rename(columns={'manufacturers_x': 'manufacturers','models_x': 'models','titels': 'titel','dates_x': 'dates','types_x': 'types','refrigerants_x': 'refrigerants','mass_of_refrigerants_x': 'mass_of_refrigerants', 'spl_indoor_x': 'spl_indoor_l','spl_outdoor_x': 'spl_outdoor_l', 'eta_x': 'eta_l', 'p_rated_x': 'p_rated_l', 'scop_x': 'scop_l', 't_biv_x': 't_biv', 'tol_x': 'tol','p_th_minus7_x': 'p_th_minus7_l', 'cop_minus7_x': 'cop_minus7_l', 'p_th_2_x': 'p_th_2_l', 'cop_2_x': 'cop_2_l', 'p_th_7_x': 'p_th_7_l','cop_7_x': 'cop_7_l', 'p_th_12_x': 'p_th_12_l', 'cop_12_x': 'cop_12_l', 'p_th_tbiv_x': 'p_th_tbiv_l', 'cop_tbiv_x': 'cop_tbiv_l','p_th_tol_x': 'p_th_tol_l', 'cop_tol_x': 'cop_tol_l', 'rated_airflows_x': 'rated_airflows_l', 'wtols_x': 'wtols', 'poffs_x': 'poffs','ptos_x': 'ptos', 'psbs_x': 'psbs', 'pcks_x': 'pcks', 'supp_energy_types_x': 'supp_energy_types', 'p_sups_x': 'p_sups_l','p_design_cools_x': 'p_design_cools_l', 'seers_x': 'seers_l', 'pdcs_35_x': 'pdcs_35_l', 'eer_35_x': 'eer_35_l','pdcs_30_x': 'pdcs_30_l','eer_30_x': 'eer_30_l', 'pdcs_25_x': 'pdcs_25_l', 'eer_25_x': 'eer_25_l', 'pdcs_20_x': 'pdcs_20_l','eer_20_x': 'eer_20_l', 'spl_indoor_y': 'spl_indoor_h','spl_outdoor_y': 'spl_outdoor_h', 'eta_y': 'eta_h', 'p_rated_y': 'p_rated_h', 'scop_y': 'scop_h', 'p_th_minus7_y': 'p_th_minus7_h', 'cop_minus7_y': 'cop_minus7_h', 'p_th_2_y': 'p_th_2_h', 'cop_2_y': 'cop_2_h', 'p_th_7_y': 'p_th_7_h','cop_7_y': 'cop_7_h', 'p_th_12_y': 'p_th_12_h', 'cop_12_y': 'cop_12_h', 'p_th_tbiv_y': 'p_th_tbiv_h', 'cop_tbiv_y': 'cop_tbiv_h','p_th_tol_y': 'p_th_tol_h', 'cop_tol_y': 'cop_tol_h', 'rated_airflows_y': 'rated_airflows_h', 'p_sups_y': 'p_sups_h','p_design_cools_y': 'p_design_cools_h', 'seers_y': 'seers_h', 'pdcs_35_y': 'pdcs_35_h', 'eer_35_y': 'eer_35_h', 'pdcs_30_y': 'pdcs_30_h','eer_30_y': 'eer_30_h', 'pdcs_25_y': 'pdcs_25_h', 'eer_25_y': 'eer_25_h', 'pdcs_20_y': 'pdcs_20_h', 'eer_20_y': 'eer_20_h'},inplace=True)
    df.to_csv('../output/database_reduced.csv',index=False)


def normalize_data():
    df=pd.read_csv('../output/database_reduced.csv')
    #change kW to W
    df['p_th_minus7_l']=(df['p_th_minus7_l']*1000).astype(int)
    df['p_th_2_l']=(df['p_th_2_l']*1000).astype(int)
    df['p_th_7_l']=(df['p_th_7_l']*1000).astype(int)
    df['p_th_12_l']=(df['p_th_12_l']*1000).astype(int)
    df['p_th_tbiv_l']=(df['p_th_tbiv_l']*1000).astype(int)
    df['p_th_tol_l']=(df['p_th_tol_l']*1000).astype(int)
    df['p_th_minus7_h']=(df['p_th_minus7_h']*1000).astype(int)
    df['p_th_2_h']=(df['p_th_2_h']*1000).astype(int)
    df['p_th_7_h']=(df['p_th_7_h']*1000).astype(int)
    df['p_th_12_h']=(df['p_th_12_h']*1000).astype(int)
    df['p_th_tbiv_h']=(df['p_th_tbiv_h']*1000).astype(int)
    df['p_th_tol_h']=(df['p_th_tol_h']*1000).astype(int)
    df['pdcs_35_l']=(df['pdcs_35_l']*1000)
    df['pdcs_30_l']=(df['pdcs_30_l']*1000)
    df['pdcs_25_l']=(df['pdcs_25_l']*1000)
    df['pdcs_20_l']=(df['pdcs_20_l']*1000)
    df['pdcs_35_h']=(df['pdcs_35_h']*1000)
    df['pdcs_30_h']=(df['pdcs_30_h']*1000)
    df['pdcs_25_h']=(df['pdcs_25_h']*1000)
    df['pdcs_20_h']=(df['pdcs_20_h']*1000)
    # add P_el
    df['p_el_minus7_l'] = (round(df['p_th_minus7_l'] / df['cop_minus7_l'])).astype(int)
    df['p_el_2_l'] = (round(df['p_th_2_l'] / df['cop_2_l'])).astype(int)
    df['p_el_7_l'] = (round(df['p_th_7_l'] / df['cop_7_l'])).astype(int)
    df['p_el_12_l'] = (round(df['p_th_12_l'] / df['cop_12_l'])).astype(int)
    df['p_el_tbiv_l'] = (round(df['p_th_tbiv_l'] / df['cop_tbiv_l'])).astype(int)
    df['p_el_tol_l'] = (round(df['p_th_tol_l'] / df['cop_tol_l'])).astype(int)
    df['p_el_minus7_h'] = (round(df['p_th_minus7_h'] / df['cop_minus7_h'])).astype(int)
    df['p_el_2_h'] = (round(df['p_th_2_h'] / df['cop_2_h'])).astype(int)
    df['p_el_7_h'] = (round(df['p_th_7_h'] / df['cop_7_h'])).astype(int)
    df['p_el_12_h'] = (round(df['p_th_12_h'] / df['cop_12_h'])).astype(int)
    df['p_el_tbiv_h'] = (round(df['p_th_tbiv_h'] / df['cop_tbiv_h'])).astype(int)
    df['p_el_tol_h'] = (round(df['p_th_tol_h'] / df['cop_tol_h'])).astype(int)
    df['p_el_35_l'] = (round(df['pdcs_35_l'] / df['eer_35_l']))
    df['p_el_30_l'] = (round(df['pdcs_30_l'] / df['eer_30_l']))
    df['p_el_25_l'] = (round(df['pdcs_25_l'] / df['eer_25_l']))
    df['p_el_20_l'] = (round(df['pdcs_20_l'] / df['eer_20_l']))
    df['p_el_35_h'] = (round(df['pdcs_35_h'] / df['eer_35_h']))
    df['p_el_30_h'] = (round(df['pdcs_30_h'] / df['eer_30_h']))
    df['p_el_25_h'] = (round(df['pdcs_25_h'] / df['eer_25_h']))
    df['p_el_20_h'] = (round(df['pdcs_20_h'] / df['eer_20_h']))
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
    """Overall there are not so many unique Keymark heat pumps for cooling in comparison to heating.

    With our fit method it is not possible to fit only over one outflow temperature. For that reason we added another
    set point at 18°C output temperature based on the heat pumps we had with this condition in Keymark. For that purpose, we identified multiplication factors for eletrical power and eer between 7°C and 18°C secondary output temperature. The mean value of that are used to calculate the electrical power and EER at 18°C for other heat pumps:
    P_el at 18°C = P_el at 7°C * multiplication factor 
    EER at 18°C = EER at 7°C * multiplication factor"""

    df.loc[(df['eer_20_l'].isna()==0)&(df['p_el_35_h_n'].isna()),'eer_20_h'] = df.loc[(df['eer_20_l'].isna()==0)&(df['p_el_35_h_n'].isna()),'eer_20_l']*(df[df['p_el_35_h_n'].isna()==0]['eer_20_h']/df[df['p_el_35_h_n'].isna()==0]['eer_20_l']).unique().mean()
    df.loc[(df['eer_25_l'].isna()==0)&(df['p_el_35_h_n'].isna()),'eer_25_h'] = df.loc[(df['eer_25_l'].isna()==0)&(df['p_el_35_h_n'].isna()),'eer_25_l']*(df[df['p_el_35_h_n'].isna()==0]['eer_25_h']/df[df['p_el_35_h_n'].isna()==0]['eer_25_l']).unique().mean()
    df.loc[(df['eer_30_l'].isna()==0)&(df['p_el_35_h_n'].isna()),'eer_30_h'] = df.loc[(df['eer_30_l'].isna()==0)&(df['p_el_35_h_n'].isna()),'eer_30_l']*(df[df['p_el_35_h_n'].isna()==0]['eer_30_h']/df[df['p_el_35_h_n'].isna()==0]['eer_30_l']).unique().mean()
    df.loc[(df['eer_35_l'].isna()==0)&(df['p_el_35_h_n'].isna()),'eer_35_h'] = df.loc[(df['eer_35_l'].isna()==0)&(df['p_el_35_h_n'].isna()),'eer_35_l']*(df[df['p_el_35_h_n'].isna()==0]['eer_35_h']/df[df['p_el_35_h_n'].isna()==0]['eer_35_l']).unique().mean()

    df.loc[(df['p_el_20_l_n'].isna()==0)&(df['p_el_35_h_n'].isna()),'p_el_20_h_n'] = df[df['p_el_35_h_n'].isna()==0]['p_el_20_h_n'].unique().mean()
    df.loc[(df['p_el_25_l_n'].isna()==0)&(df['p_el_35_h_n'].isna()),'p_el_25_h_n'] = df[df['p_el_35_h_n'].isna()==0]['p_el_25_h_n'].unique().mean()
    df.loc[(df['p_el_30_l_n'].isna()==0)&(df['p_el_35_h_n'].isna()),'p_el_30_h_n'] = df[df['p_el_35_h_n'].isna()==0]['p_el_30_h_n'].unique().mean()
    df.loc[(df['p_el_35_l_n'].isna()==0)&(df['p_el_35_h_n'].isna()),'p_el_35_h_n'] = df[df['p_el_35_h_n'].isna()==0]['p_el_35_h_n'].unique().mean()
    df.to_csv(r'../output/database_reduced_normalized.csv', encoding='utf-8', index=False)


def identify_subtypes():
    # Identify Subtype like On-Off or Regulated by comparing the thermal Power output at different temperature levels:
    # -7/34 |  2/30  |  7/27  |  12/24
    # assumptions for On-Off Heatpump: if temperature difference is bigger, thermal Power output is smaller
    # assumptions for Regulated: everythin else
    df=pd.read_csv(r'../output/database_reduced_normalized.csv')
    df['Subtype'] = np.where((df['p_th_minus7_l'] <= df['p_th_2_l']) & (df['p_th_2_l'] <= df['p_th_7_l'])& (df['p_th_7_l'] <= df['p_th_12_l']), 'On-Off', 'Regulated')

    filt1 = (df['types'] == 'Outdoor Air/Water') & (df['Subtype'] == 'Regulated')
    df.loc[filt1, 'Group'] = 1
    filt1 = (df['types'] == 'Exhaust Air/Water') & (df['Subtype'] == 'Regulated')
    df.loc[filt1, 'Group'] = 7
    filt1 = (df['types'] == 'Brine/Water') & (df['Subtype'] == 'Regulated')
    df.loc[filt1, 'Group'] = 2
    filt1 = (df['types'] == 'Brine/Water and Water/Water') & (df['Subtype'] == 'Regulated')
    df.loc[filt1, 'Group'] = 2
    filt1 = (df['types'] == 'Water/Water') & (df['Subtype'] == 'Regulated')
    df.loc[filt1, 'Group'] = 3

    filt1 = (df['types'] == 'Outdoor Air/Water') & (df['Subtype'] == 'On-Off')
    df.loc[filt1, 'Group'] = 4
    filt1 = (df['types'] == 'Exhaust Air/Water') & (df['Subtype'] == 'On-Off')
    df.loc[filt1, 'Group'] = 7
    filt1 = (df['types'] == 'Brine/Water') & (df['Subtype'] == 'On-Off')
    df.loc[filt1, 'Group'] = 5
    filt1 = (df['types'] == 'Brine/Water and Water/Water') & (df['Subtype'] == 'On-Off')
    df.loc[filt1, 'Group'] = 5
    filt1 = (df['types'] == 'Water/Water') & (df['Subtype'] == 'On-Off')
    df.loc[filt1, 'Group'] = 6
    df = df.loc[df['Group'] != 7]
    df.to_csv(r'../output/database_reduced_normalized_subtypes.csv', encoding='utf-8', index=False)


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


def interpolate_t_out(t_in):
    # Function to interpolate Temperature out at T_biv and TOL
    t_amb=[12,7,2,-7]
    t_out_low=[24,27,30,34]
    t_out_high=[30,36,42,52]
    if t_in>=7:
        i=0
    elif t_in<=2:
        i=2
    else:
        i=1
    t_out_l=t_out_low[i+1]-(t_out_low[i+1]-t_out_low[i])*(t_in-t_amb[i+1])/(t_amb[i]-t_amb[i+1])
    t_out_h=t_out_high[i+1]-(t_out_high[i+1]-t_out_high[i])*(t_in-t_amb[i+1])/(t_amb[i]-t_amb[i+1])
    return round(t_out_l,2), round(t_out_h,2)


def calculate_fitting_parameters():
   # Calculate function parameters from normalized values
    p1_P_el = []
    p2_P_el = []
    p3_P_el = []
    p4_P_el = []
    p1_COP = []
    p2_COP = []
    p3_COP = []
    p4_COP = []
    p1_P_el_c=[]
    p2_P_el_c=[]
    p3_P_el_c=[]
    p4_P_el_c=[]
    p1_EER=[]
    p2_EER=[]
    p3_EER=[]
    p4_EER=[]
    df = pd.read_csv(r'../output/database_reduced_normalized_subtypes.csv')
    for model in df['titel']:
        group=df.loc[df['titel']==(model),'Group'].values[0]
        #Create Model DF with all important information for fitting heating parameters
        df_model=pd.DataFrame()
        df_model['T_amb']=[-7,-7,2,2,7,7,12,12]
        df_model['T_out']=[34,52,30,42,27,36,24,30]
        df_model['P_el']=[(df.loc[df['titel']==(model),'p_el_minus7_l_n'].values[0]),
                            (df.loc[df['titel']==(model),'p_el_minus7_h_n'].values[0]),
                            (df.loc[df['titel']==(model),'p_el_2_l_n'].values[0]),
                            (df.loc[df['titel']==(model),'p_el_2_h_n'].values[0]),
                            (df.loc[df['titel']==(model),'p_el_7_l_n'].values[0]),
                            (df.loc[df['titel']==(model),'p_el_7_h_n'].values[0]),
                            (df.loc[df['titel']==(model),'p_el_12_l_n'].values[0]),
                            (df.loc[df['titel']==(model),'p_el_12_h_n'].values[0]),
                            ]
        df_model['COP']=[(df.loc[df['titel']==(model),'cop_minus7_l'].values[0]),
                            (df.loc[df['titel']==(model),'cop_minus7_h'].values[0]),
                            (df.loc[df['titel']==(model),'cop_2_l'].values[0]),
                            (df.loc[df['titel']==(model),'cop_2_h'].values[0]),
                            (df.loc[df['titel']==(model),'cop_7_l'].values[0]),
                            (df.loc[df['titel']==(model),'cop_7_h'].values[0]),
                            (df.loc[df['titel']==(model),'cop_12_l'].values[0]),
                            (df.loc[df['titel']==(model),'cop_12_h'].values[0]),
                            ]
        if group==1 or group==4: #Air/Water 
            df_model['T_in']=[-7,-7,2,2,7,7,12,12]
        elif group==2 or group==5: #Brine/Water
            df_model['T_in']=[0,0,0,0,0,0,0,0]
            df_model1=df_model.copy()
            df_model1['T_in'] = df_model1['T_in'] + 1
            df_model1['T_out'] = df_model1['T_out'] + 1
            df_model = pd.concat([df_model, df_model1])
        else: # Water/Water
            df_model['T_in']=[10,10,10,10,10,10,10,10]
            df_model1=df_model.copy()
            df_model1['T_in'] = df_model1['T_in'] + 1
            df_model1['T_out'] = df_model1['T_out'] + 1
            df_model = pd.concat([df_model, df_model1])
        """
        t_biv=df.loc[df['titel']==(model),'t_biv'].values[0]
        tol=df.loc[df['titel']==(model),'tol'].values[0]
        tol_low,tol_high=interpolate_t_out(tol)
        t_biv_low,t_biv_high=interpolate_t_out(t_biv)
        df_model['T_amb']=[tol,tol,t_biv,t_biv,-7,-7,2,2,7,7,12,12]
        df_model['T_out']=[tol_low,tol_high,t_biv_low,t_biv_high,34,52,30,42,27,36,24,30]
        df_model['P_el']=[(df.loc[df['titel']==(model),'p_el_tol_l_n'].values[0]),
                            (df.loc[df['titel']==(model),'p_el_tol_h_n'].values[0]),  
                            (df.loc[df['titel']==(model),'p_el_tbiv_l_n'].values[0]),  
                            (df.loc[df['titel']==(model),'p_el_tbiv_h_n'].values[0]),  
                            (df.loc[df['titel']==(model),'p_el_minus7_l_n'].values[0]),
                            (df.loc[df['titel']==(model),'p_el_minus7_h_n'].values[0]),
                            (df.loc[df['titel']==(model),'p_el_2_l_n'].values[0]),
                            (df.loc[df['titel']==(model),'p_el_2_h_n'].values[0]),
                            (df.loc[df['titel']==(model),'p_el_7_l_n'].values[0]),
                            (df.loc[df['titel']==(model),'p_el_7_h_n'].values[0]),
                            (df.loc[df['titel']==(model),'p_el_12_l_n'].values[0]),
                            (df.loc[df['titel']==(model),'p_el_12_h_n'].values[0]),
                            ]
        df_model['COP']=[(df.loc[df['titel']==(model),'cop_tol_l'].values[0]),
                            (df.loc[df['titel']==(model),'cop_tol_h'].values[0]),
                            (df.loc[df['titel']==(model),'cop_tbiv_l'].values[0]),
                            (df.loc[df['titel']==(model),'cop_tbiv_h'].values[0]),
                            (df.loc[df['titel']==(model),'cop_minus7_l'].values[0]),
                            (df.loc[df['titel']==(model),'cop_minus7_h'].values[0]),
                            (df.loc[df['titel']==(model),'cop_2_l'].values[0]),
                            (df.loc[df['titel']==(model),'cop_2_h'].values[0]),
                            (df.loc[df['titel']==(model),'cop_7_l'].values[0]),
                            (df.loc[df['titel']==(model),'cop_7_h'].values[0]),
                            (df.loc[df['titel']==(model),'cop_12_l'].values[0]),
                            (df.loc[df['titel']==(model),'cop_12_h'].values[0]),
                            ]
        if group==1 or group==4: #Air/Water 
            df_model['T_in']=[tol,tol,t_biv,t_biv,-7,-7,2,2,7,7,12,12]
        elif group==2 or group==5: #Brine/Water
            df_model['T_in']=[0,0,0,0,0,0,0,0,0,0,0,0]
            df_model1=df_model.copy()
            df_model1['T_in'] = df_model1['T_in'] + 1
            df_model1['T_out'] = df_model1['T_out'] + 1
            df_model = pd.concat([df_model, df_model1])
        else: # Water/Water
            df_model['T_in']=[10,10,10,10,10,10,10,10,10,10,10,10]
            df_model1=df_model.copy()
            df_model1['T_in'] = df_model1['T_in'] + 1
            df_model1['T_out'] = df_model1['T_out'] + 1
            df_model = pd.concat([df_model, df_model1])
        df_model.drop_duplicates(inplace=True) #if multiple data at the same point"""
        #Calculate heating parameters
        if group == 1 or group == 2 or group == 3:
            COP_para_key = fit_simple(df_model['T_in'], df_model['T_out'], df_model['T_amb'], df_model['COP'])
            df_model=df_model.loc[((df_model['T_amb'] != 12) & (df_model['T_amb'] != 7))]
            P_el_n_para_key=fit_simple(df_model['T_in'], df_model['T_out'], df_model['T_amb'], df_model['P_el'])
        elif group == 4 or group == 5 or group == 6:
            P_el_n_para_key=fit_simple(df_model['T_in'], df_model['T_out'], df_model['T_amb'], df_model['P_el'])
            COP_para_key = fit_simple(df_model['T_in'], df_model['T_out'], df_model['T_amb'], df_model['COP'])
        
        #Calculate cooling parameters
        if df.loc[df['titel']==(model),'seers_l'].isna().values[0]==0:
            df_model=pd.DataFrame()
            df_model['T_in']=[20,20,25,25,30,30,35,35]
            df_model['T_amb']=[20,20,25,25,30,30,35,35]
            df_model['T_out']=[7,18,7,18,7,18,7,18]
            df_model['P_el']=[(df.loc[df['titel']==(model),'p_el_20_l_n'].values[0]),  
                                (df.loc[df['titel']==(model),'p_el_20_h_n'].values[0]), 
                                (df.loc[df['titel']==(model),'p_el_25_l_n'].values[0]),
                                (df.loc[df['titel']==(model),'p_el_25_h_n'].values[0]),  
                                (df.loc[df['titel']==(model),'p_el_30_l_n'].values[0]),  
                                (df.loc[df['titel']==(model),'p_el_30_h_n'].values[0]),  
                                (df.loc[df['titel']==(model),'p_el_35_l_n'].values[0]),
                                (df.loc[df['titel']==(model),'p_el_35_h_n'].values[0]),
                                ]
            df_model['EER']=[(df.loc[df['titel']==(model),'eer_20_l'].values[0]),
                                (df.loc[df['titel']==(model),'eer_20_h'].values[0]),
                                (df.loc[df['titel']==(model),'eer_25_l'].values[0]),
                                (df.loc[df['titel']==(model),'eer_25_h'].values[0]),
                                (df.loc[df['titel']==(model),'eer_30_l'].values[0]),
                                (df.loc[df['titel']==(model),'eer_30_h'].values[0]),
                                (df.loc[df['titel']==(model),'eer_35_l'].values[0]),
                                (df.loc[df['titel']==(model),'eer_35_h'].values[0]),
                                ]
            EER_para_key = fit_simple(df_model['T_in'], df_model['T_out'], df_model['T_amb'], df_model['EER'])
            df_model=df_model.loc[df_model['T_in']>20]
            P_el_n_para_key_c = fit_simple(df_model['T_in'], df_model['T_out'], df_model['T_amb'], df_model['P_el'])
            
            if group!=1: #TODO: Cooling for Brine/Water and Water/Water
                P_el_n_para_key_c = [np.nan,np.nan,np.nan,np.nan]
                EER_para_key = [np.nan,np.nan,np.nan,np.nan]
        else:
            P_el_n_para_key_c = [np.nan,np.nan,np.nan,np.nan]
            EER_para_key = [np.nan,np.nan,np.nan,np.nan]
        #add to lists
        p1_P_el.append(P_el_n_para_key[0])
        p2_P_el.append(P_el_n_para_key[1])
        p3_P_el.append(P_el_n_para_key[2])
        p4_P_el.append(P_el_n_para_key[3])
        p1_COP.append(COP_para_key[0])
        p2_COP.append(COP_para_key[1])
        p3_COP.append(COP_para_key[2])
        p4_COP.append(COP_para_key[3])
        p1_P_el_c.append(P_el_n_para_key_c[0])
        p2_P_el_c.append(P_el_n_para_key_c[1])
        p3_P_el_c.append(P_el_n_para_key_c[2])
        p4_P_el_c.append(P_el_n_para_key_c[3])
        p1_EER.append(EER_para_key[0])
        p2_EER.append(EER_para_key[1])
        p3_EER.append(EER_para_key[2])
        p4_EER.append(EER_para_key[3])
    #Add parameters to df
    df['p1_P_el_h [1/°C]'] = p1_P_el
    df['p2_P_el_h [1/°C]'] = p2_P_el
    df['p3_P_el_h [-]'] = p3_P_el
    df['p4_P_el_h [1/°C]'] = p4_P_el
    df['p1_COP [-]'] = p1_COP
    df['p2_COP [-]'] = p2_COP
    df['p3_COP [-]'] = p3_COP
    df['p4_COP [-]'] = p4_COP
    #Add cooling parameters to df
    df['p1_P_el_c [1/°C]'] = p1_P_el_c
    df['p2_P_el_c [1/°C]'] = p2_P_el_c
    df['p3_P_el_c [-]'] = p3_P_el_c
    df['p4_P_el_c [1/°C]'] = p4_P_el_c
    df['p1_EER [-]'] = p1_EER
    df['p2_EER [-]'] = p2_EER
    df['p3_EER [-]'] = p3_EER
    df['p4_EER [-]'] = p4_EER
    df.to_csv(r'../output/database_reduced_normalized_subtypes_parameters.csv', encoding='utf-8', index=False)
    df.rename(columns={'manufacturers': 'Manufacturer' ,
                        'models': 'Model' ,
                        'titel': 'Titel' ,
                        'dates': 'Date' ,
                        'types': 'Type',
                        'refrigerants': 'Refrigerant' ,
                        'mass_of_refrigerants': 'Mass of Refrigerant [kg]' ,
                        'spl_indoor_l': 'SPL indoor low Power [dBA]' ,
                        'spl_outdoor_l': 'SPL outdoor low Power [dBA]' ,
                        'eta_l': 'eta low T [%]' ,
                        'p_rated_l': 'Rated Power low T [kW]' ,
                        'scop_l': 'SCOP' ,
                        't_biv': 'Bivalence temperature [°C]' ,
                        'tol': 'Tolerance temperature [°C]' ,
                        'wtols': 'Max. water heating temperature [°C]' ,
                        'poffs': 'Poff [W]' ,
                        'ptos': 'PTOS [W]' ,
                        'psbs': 'PSB [W]',
                        'pcks': 'PCKS [W]' ,
                        'seers_l': 'SEER low T' ,
                        'spl_indoor_h': 'SPL indoor high Power [dBA]' ,
                        'spl_outdoor_h': 'SPL outdoor high Power [dBA]' ,
                        'eta_h': 'eta medium T [%]' ,
                        'p_rated_h': 'Rated Power medium T [kW]' ,
                        'p_th_minus7_h': 'P_th_h_ref [W]' ,
                        'cop_minus7_h': 'COP_ref' ,
                        'p_el_minus7_h': 'P_el_h_ref [W]' ,
                        'p_design_cools_h': 'P_design_h_T [kW]' ,
                        'seers_h': 'SEER medium T' ,
                        'pdcs_35_l': 'P_th_c_ref [W]' ,
                        'eer_35_l': 'EER_c_ref' ,
                        'p_el_35_l': 'P_el_c_ref [W]' ,
                        'Subtype': 'Subtype' ,
                        'Group': 'Group' ,
                        }, inplace=True)
    df=df[['Manufacturer' ,'Model' ,'Titel' ,'Date' ,'Type','Subtype' ,'Group' ,'Rated Power low T [kW]' ,'Rated Power medium T [kW]' ,'Refrigerant' ,'Mass of Refrigerant [kg]' ,'SPL indoor low Power [dBA]' ,'SPL outdoor low Power [dBA]' ,'SPL indoor high Power [dBA]' ,'SPL outdoor high Power [dBA]' ,'Bivalence temperature [°C]' ,'Tolerance temperature [°C]' ,'Max. water heating temperature [°C]' ,'Poff [W]' ,'PTOS [W]' ,'PSB [W]','PCKS [W]' ,'eta low T [%]' ,'eta medium T [%]' ,'SCOP' ,'SEER low T' ,'SEER medium T' ,'P_th_h_ref [W]' ,'P_th_c_ref [W]' ,'P_el_h_ref [W]' ,'P_el_c_ref [W]' ,'COP_ref' ,'EER_c_ref' ,'p1_P_el_h [1/°C]', 'p2_P_el_h [1/°C]', 'p3_P_el_h [-]','p4_P_el_h [1/°C]', 'p1_COP [-]', 'p2_COP [-]', 'p3_COP [-]','p4_COP [-]','p1_P_el_c [1/°C]','p2_P_el_c [1/°C]', 'p3_P_el_c [-]', 'p4_P_el_c [1/°C]', 'p1_EER [-]','p2_EER [-]', 'p3_EER [-]', 'p4_EER [-]']]
    df.to_csv(r'hplib_database.csv', encoding='utf-8', index=False)


def validation_re_mape():
    # Simulate every set point for every heat pump and save csv file
    mape_pth=[]
    mape_pel=[]
    mape_cop=[]
    mape_pdc=[]
    mape_pel_c=[]
    mape_eer=[]
    df=pd.read_csv('../output/database_reduced_normalized_subtypes_parameters.csv')
    df_re=pd.DataFrame()
    i=0
    while i<len(df):
        model=df.iloc[i:]['titel'].values[0]
        para=hpl.get_parameters(model)
        heatpump = hpl.HeatPump(para)
        group=df.iloc[i:]['Group'].values[0]
        df_model=pd.DataFrame()
        df_model['T_amb']=[-7,-7,2,2,7,7,12,12]
        df_model['T_out']=[34,52,30,42,27,36,24,30]
        if group==1 or group==4: #Air/Water 
            df_model['T_in']=[-7,-7,2,2,7,7,12,12]
        elif group==2 or group==5: #Brine/Water
            df_model['T_in']=[0,0,0,0,0,0,0,0]
        else: # Water/Water
            df_model['T_in']=[10,10,10,10,10,10,10,10]
        res=heatpump.simulate(t_in_primary=df_model['T_in'].values,t_in_secondary=df_model['T_out'].values-5,t_amb=df_model['T_amb'].values)
        res=pd.DataFrame(res)
        res['P_th_real']=[(df.loc[df['titel']==(model),'p_th_minus7_l'].values[0]),
                        (df.loc[df['titel']==(model),'p_th_minus7_h'].values[0]),
                        (df.loc[df['titel']==(model),'p_th_2_l'].values[0]),
                        (df.loc[df['titel']==(model),'p_th_2_h'].values[0]),
                        (df.loc[df['titel']==(model),'p_th_7_l'].values[0]),
                        (df.loc[df['titel']==(model),'p_th_7_h'].values[0]),
                        (df.loc[df['titel']==(model),'p_th_12_l'].values[0]),
                        (df.loc[df['titel']==(model),'p_th_12_h'].values[0]),
                                    ]
        res['P_el_real']=[(df.loc[df['titel']==(model),'p_el_minus7_l'].values[0]),
                        (df.loc[df['titel']==(model),'p_el_minus7_h'].values[0]),
                        (df.loc[df['titel']==(model),'p_el_2_l'].values[0]),
                        (df.loc[df['titel']==(model),'p_el_2_h'].values[0]),
                        (df.loc[df['titel']==(model),'p_el_7_l'].values[0]),
                        (df.loc[df['titel']==(model),'p_el_7_h'].values[0]),
                        (df.loc[df['titel']==(model),'p_el_12_l'].values[0]),
                        (df.loc[df['titel']==(model),'p_el_12_h'].values[0]),
                                    ]
        res['COP_real']=[(df.loc[df['titel']==(model),'cop_minus7_l'].values[0]),
                        (df.loc[df['titel']==(model),'cop_minus7_h'].values[0]),
                        (df.loc[df['titel']==(model),'cop_2_l'].values[0]),
                        (df.loc[df['titel']==(model),'cop_2_h'].values[0]),
                        (df.loc[df['titel']==(model),'cop_7_l'].values[0]),
                        (df.loc[df['titel']==(model),'cop_7_h'].values[0]),
                        (df.loc[df['titel']==(model),'cop_12_l'].values[0]),
                        (df.loc[df['titel']==(model),'cop_12_h'].values[0]),
                                    ]
        """tol=df.iloc[i-1:]['tol'].values[0]
        t_biv=df.iloc[i-1:]['t_biv'].values[0]
        tol_low,tol_high=interpolate_t_out(tol)
        t_biv_low,t_biv_high=interpolate_t_out(t_biv)
        df_model=pd.DataFrame()
        df_model['T_amb']=[tol,tol,t_biv,t_biv,-7,-7,2,2,7,7,12,12]
        df_model['T_out']=[tol_low,tol_high,t_biv_low,t_biv_high,34,52,30,42,27,36,24,30]
        if group==1 or group==4: #Air/Water 
            df_model['T_in']=[tol,tol,t_biv,t_biv,-7,-7,2,2,7,7,12,12]
        elif group==2 or group==5: #Brine/Water
            df_model['T_in']=[0,0,0,0,0,0,0,0,0,0,0,0]
        else: # Water/Water
            df_model['T_in']=[10,10,10,10,10,10,10,10,10,10,10,10]
        res=heatpump.simulate(t_in_primary=df_model['T_in'].values,t_in_secondary=df_model['T_out'].values-5,t_amb=df_model['T_in'].values)
        res=pd.DataFrame(res)
        res['P_th_real']=[(df.loc[df['titel']==(model),'p_th_tol_l'].values[0]),
                        (df.loc[df['titel']==(model),'p_th_tol_h'].values[0]),  
                        (df.loc[df['titel']==(model),'p_th_tbiv_l'].values[0]),  
                        (df.loc[df['titel']==(model),'p_th_tbiv_h'].values[0]),
                        (df.loc[df['titel']==(model),'p_th_minus7_l'].values[0]),
                        (df.loc[df['titel']==(model),'p_th_minus7_h'].values[0]),
                        (df.loc[df['titel']==(model),'p_th_2_l'].values[0]),
                        (df.loc[df['titel']==(model),'p_th_2_h'].values[0]),
                        (df.loc[df['titel']==(model),'p_th_7_l'].values[0]),
                        (df.loc[df['titel']==(model),'p_th_7_h'].values[0]),
                        (df.loc[df['titel']==(model),'p_th_12_l'].values[0]),
                        (df.loc[df['titel']==(model),'p_th_12_h'].values[0]),
                                    ]
        res['P_el_real']=[(df.loc[df['titel']==(model),'p_el_tol_l'].values[0]),
                        (df.loc[df['titel']==(model),'p_el_tol_h'].values[0]),  
                        (df.loc[df['titel']==(model),'p_el_tbiv_l'].values[0]),  
                        (df.loc[df['titel']==(model),'p_el_tbiv_h'].values[0]),
                        (df.loc[df['titel']==(model),'p_el_minus7_l'].values[0]),
                        (df.loc[df['titel']==(model),'p_el_minus7_h'].values[0]),
                        (df.loc[df['titel']==(model),'p_el_2_l'].values[0]),
                        (df.loc[df['titel']==(model),'p_el_2_h'].values[0]),
                        (df.loc[df['titel']==(model),'p_el_7_l'].values[0]),
                        (df.loc[df['titel']==(model),'p_el_7_h'].values[0]),
                        (df.loc[df['titel']==(model),'p_el_12_l'].values[0]),
                        (df.loc[df['titel']==(model),'p_el_12_h'].values[0]),
                                    ]
        res['COP_real']=[(df.loc[df['titel']==(model),'cop_tol_l'].values[0]),
                        (df.loc[df['titel']==(model),'cop_tol_h'].values[0]),
                        (df.loc[df['titel']==(model),'cop_tbiv_l'].values[0]),
                        (df.loc[df['titel']==(model),'cop_tbiv_h'].values[0]),
                        (df.loc[df['titel']==(model),'cop_minus7_l'].values[0]),
                        (df.loc[df['titel']==(model),'cop_minus7_h'].values[0]),
                        (df.loc[df['titel']==(model),'cop_2_l'].values[0]),
                        (df.loc[df['titel']==(model),'cop_2_h'].values[0]),
                        (df.loc[df['titel']==(model),'cop_7_l'].values[0]),
                        (df.loc[df['titel']==(model),'cop_7_h'].values[0]),
                        (df.loc[df['titel']==(model),'cop_12_l'].values[0]),
                        (df.loc[df['titel']==(model),'cop_12_h'].values[0]),
                                    ]"""
        res['RE_P_th']=(res['P_th']/res['P_th_real']-1)*100
        res['RE_P_el']=(res['P_el']/res['P_el_real']-1)*100
        res['RE_COP']=(res['COP']/res['COP_real']-1)*100
        mape_pth.append((((res['P_th_real']-res['P_th']).abs())/res['P_th_real']*100).mean())
        mape_pel.append((((res['P_el_real']-res['P_el']).abs())/res['P_el_real']*100).mean())
        mape_cop.append((((res['COP_real']-res['COP']).abs())/res['COP_real']*100).mean())
        if (df.loc[df['titel']==(model),'seers_l'].isna().values[0]==0) & (group==1):
            df_model=pd.DataFrame()
            df_model['T_in']=[20,20,25,25,30,30,35,35]
            df_model['T_amb']=[20,20,25,25,30,30,35,35]
            df_model['T_out']=[7,18,7,18,7,18,7,18]
            res_c=heatpump.simulate(t_in_primary=df_model['T_in'].values,t_in_secondary=df_model['T_out'].values+5,t_amb=df_model['T_in'].values,mode=2)
            res_c=pd.DataFrame(res_c)
            res_c['Pdc_real']=[(df.loc[df['titel']==(model),'pdcs_20_l'].values[0]),  
                                (df.loc[df['titel']==(model),'pdcs_20_h'].values[0]), 
                                (df.loc[df['titel']==(model),'pdcs_25_l'].values[0]),
                                (df.loc[df['titel']==(model),'pdcs_25_h'].values[0]),  
                                (df.loc[df['titel']==(model),'pdcs_30_l'].values[0]),  
                                (df.loc[df['titel']==(model),'pdcs_30_h'].values[0]),  
                                (df.loc[df['titel']==(model),'pdcs_35_l'].values[0]),
                                (df.loc[df['titel']==(model),'pdcs_35_h'].values[0]),
                                ]
            res_c['Pel_c_real']=[(df.loc[df['titel']==(model),'p_el_20_l'].values[0]),  
                                (df.loc[df['titel']==(model),'p_el_20_h'].values[0]), 
                                (df.loc[df['titel']==(model),'p_el_25_l'].values[0]),
                                (df.loc[df['titel']==(model),'p_el_25_h'].values[0]),  
                                (df.loc[df['titel']==(model),'p_el_30_l'].values[0]),  
                                (df.loc[df['titel']==(model),'p_el_30_h'].values[0]),  
                                (df.loc[df['titel']==(model),'p_el_35_l'].values[0]),
                                (df.loc[df['titel']==(model),'p_el_35_h'].values[0]),
                                ]
            res_c['EER_real']=[(df.loc[df['titel']==(model),'eer_20_l'].values[0]),
                                (df.loc[df['titel']==(model),'eer_20_h'].values[0]),
                                (df.loc[df['titel']==(model),'eer_25_l'].values[0]),
                                (df.loc[df['titel']==(model),'eer_25_h'].values[0]),
                                (df.loc[df['titel']==(model),'eer_30_l'].values[0]),
                                (df.loc[df['titel']==(model),'eer_30_h'].values[0]),
                                (df.loc[df['titel']==(model),'eer_35_l'].values[0]),
                                (df.loc[df['titel']==(model),'eer_35_h'].values[0]),
                                ]
            res_c['RE_Pdc']=(res_c['P_th']*-1/res_c['Pdc_real']-1)*100
            res_c['RE_Pel_c']=(res_c['P_el']/res_c['Pel_c_real']-1)*100
            res_c['RE_EER']=(res_c['EER']/res_c['EER_real']-1)*100
            res=pd.concat([res,res_c])
            mape_pdc.append((((res['Pdc_real']+res['P_th']).abs())/res['Pdc_real']*100).mean())
            mape_pel_c.append((((res['Pel_c_real']-res['P_el']).abs())/res['Pel_c_real']*100).mean())
            mape_eer.append((((res['EER_real']-res['EER']).abs())/res['EER_real']*100).mean())
        else:
            mape_pdc.append(np.nan)
            mape_pel_c.append(np.nan)
            mape_eer.append(np.nan)
        res['titel']=model
        res['Group']=group
        df_re=pd.concat([df_re,res])
        i+=1
    df_re.to_csv('../output/relative_error.csv', encoding='utf-8', index=False)
    df=pd.read_csv('hplib_database.csv')
    df = df.loc[df['Model'] != 'Generic']
    df['MAPE P_th']=mape_pth
    df['MAPE P_el']=mape_pel
    df['MAPE COP']=mape_cop
    df['MAPE Pdc']=mape_pdc
    df['MAPE P_el_c']=mape_pel_c
    df['MAPE EER']=mape_eer
    df.to_csv(r'hplib_database.csv', encoding='utf-8', index=False)


def add_generic():
    percent=[0,0.2,0.8,1]
    df = pd.read_csv('hplib_database.csv', delimiter=',')
    df = df.loc[df['Model'] != 'Generic']
    #df=df.drop_duplicates(subset=['p1_P_el_h [1/°C]', 'p2_P_el_h [1/°C]', 'p3_P_el_h [-]', 'p4_P_el_h [1/°C]', 'p1_COP [-]', 'p2_COP [-]', 'p3_COP [-]', 'p4_COP [-]', 'p1_P_el_c [1/°C]', 'p2_P_el_c [1/°C]', 'p3_P_el_c [-]', 'p4_P_el_c [1/°C]', 'p1_EER [-]', 'p2_EER [-]', 'p3_EER [-]', 'p4_EER [-]'])
    df.index=range(len(df))
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
        i=len((df.loc[(df['MAPE P_el']>0) &(df['MAPE P_el']<=25) & (df['Group']==group)]))
        if i>50:
            for j in percent:
                if j<1:
                    if j==0:
                        titel='Generic_top'
                    if j==0.2:
                        titel='Generic_average'
                    if j==0.8:
                        titel='Generic_bottom'
                    df_generic=(df.loc[(df['MAPE P_el']>0) & (df['MAPE P_el']<=25) & (df['Group']==group)]).sort_values(['SCOP'],ascending=False)[int(j*i):int(i*percent[percent.index(j)+1])]
                    para=df_generic[['p1_P_el_h [1/°C]', 'p2_P_el_h [1/°C]', 'p3_P_el_h [-]', 'p4_P_el_h [1/°C]', 'p1_COP [-]', 'p2_COP [-]', 'p3_COP [-]', 'p4_COP [-]', 'p1_P_el_c [1/°C]', 'p2_P_el_c [1/°C]', 'p3_P_el_c [-]', 'p4_P_el_c [1/°C]', 'p1_EER [-]', 'p2_EER [-]', 'p3_EER [-]', 'p4_EER [-]' ]].mean(0).to_list()
                    df.loc[len(df.index)]=['Generic', 'Generic', titel, '', Type, modus, group,'', '', '','', '','', '', '', '', '', '','', '', '', '', '','', '', '', '','', '', '', '','', '']+ para +[0,0,0,0,0,0]
        else:
            df_generic=(df.loc[(df['MAPE P_el']>0) & (df['MAPE P_el']<=25) & (df['Group']==group)]).sort_values(['SCOP'],ascending=False)
            para=df_generic[['p1_P_el_h [1/°C]', 'p2_P_el_h [1/°C]', 'p3_P_el_h [-]', 'p4_P_el_h [1/°C]', 'p1_COP [-]', 'p2_COP [-]', 'p3_COP [-]', 'p4_COP [-]', 'p1_P_el_c [1/°C]', 'p2_P_el_c [1/°C]', 'p3_P_el_c [-]', 'p4_P_el_c [1/°C]', 'p1_EER [-]', 'p2_EER [-]', 'p3_EER [-]', 'p4_EER [-]' ]].mean(0).to_list()
            df.loc[len(df.index)]=['Generic', 'Generic', 'Generic_average', '', Type, modus, group,'', '', '','', '','', '', '', '', '', '','', '', '', '', '','', '', '', '','', '', '', '','', '']+ para +[0,0,0,0,0,0]
    df.to_csv('hplib_database.csv', encoding='utf-8', index=False)



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
    
