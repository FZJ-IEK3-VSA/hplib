import pytest
import os

import hplib.hplib_database as db
import hplib.hplib as hpl

# @pytest.mark.skip(reason="Takes too long to download")
def test_import_keymark_data():
    """Tests if the heating relevant data can be retrieved
    from the csv files and saved in a single database/csv
    file."""
    
    db.import_keymark_data()


def test_merge_to_database():
    """Tests if the relevant data can be retrieved
    from the csv files and saved in a single database/csv
    file."""
    
    df_operation, df_meta = db.merge_raw_csv(foldername='csv',)

    # filter temperature 55°C (5) and climate average (3)
    df = df_operation.loc[(slice(None), 5, 3), :]

    assert len(df) > 1000
    assert len(df) < 6000

    assert df['scop'].astype(float).mean() > 3.1
    assert df['scop'].astype(float).mean() < 3.5
    

def test_read_performance_data():
    """
    """
    df = db.read_performance_data("performance_data.csv",)

    # filter temperature 55°C (5) and climate average (3)
    df = df.loc[(slice(None), 5, 3), :]


    assert len(df) > 1000
    assert len(df) < 6000

    assert df['scop'].astype(float).mean() > 3.1
    assert df['scop'].astype(float).mean() < 3.5


def test_load_database():
    """Tests if the database can be loaded."""
    
    database = hpl.load_database()




def test_load_single_performance_data():
    """
    Tests if the performance data from a single heat pump
    can be loaded 
    """
    model = 'i-SHWAK V4 06'
    parameters = hpl.get_parameters(model).squeeze(axis=0).to_dict()

    assert parameters['Rated Power medium T [kW]'] == 4

    
    assert "Model"  in parameters
    assert "Rated Power low T [kW]" in parameters