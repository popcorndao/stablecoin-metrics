import os
from datetime import datetime
import json

class CONFIG():
    """Configuration class for the scripts"""
    
    ConfigPath = os.path.dirname(os.path.realpath(__file__))
    DataDirectory = os.path.join(ConfigPath, '..', 'data')
    with open(os.path.join(DataDirectory, "data_sources.json"), "r") as file:
        DataSources = json.load(file); 

    
    @classmethod
    def write(cls, whichData, key, value):
        cls.DataSources[whichData][key] = value
        with open(os.path.join(cls.DataDirectory, "data_sources.json"), "w") as file:
            json.dump(cls.DataSources, file, indent=2)
    


