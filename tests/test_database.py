import pytest
import os

import hplib.hplib_database as db


def test_import_keymark_data():
    """Tests if the heating relevant data can be retrieved"""
    
    db.import_keymark_data()

