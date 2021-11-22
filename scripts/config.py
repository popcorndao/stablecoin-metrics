import os
from datetime import datetime
import json

class CONFIG():
    """Configuration class for the scripts"""
    
    ConfigPath = os.path.dirname(os.path.realpath(__file__))
    DataDirectory = os.path.join(ConfigPath, '..', 'data')
    with open(os.path.join(DataDirectory, "data_sources.json"), "r") as file:
        DataSources = json.load(file); 
    


