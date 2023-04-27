import pytest
import os

import hplib.hplib_database as db
import hplib.hplib as hpl

def test_import_keymark_data():
    """Tests if the heating relevant data can be retrieved
    from the csv files and saved in a single database/csv
    file."""
    
    db.import_keymark_data()


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