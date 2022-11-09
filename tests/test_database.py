import pytest
import os

import hplib.hplib_database as db


def test_import_heating_data():
    """Tests if the heating relevant data can be retrieved"""
    
    TEST_NAME = "test_database.csv"
    
    test_path = os.path.join(db.OUTPUT_FOLDERS, TEST_NAME)

    try:
        db.import_heating_data(database_name=TEST_NAME)

        with open(test_path) as f:
            lines = sum(1 for line in f)

        assert lines > 6000

    finally:
        os.remove(test_path)

    



def test_import_cooling_data():
    """Tests if the cooling relevant data can be gathered"""

    db.import_cooling_data()