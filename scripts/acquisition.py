# import config
from .config import CONFIG

# import packages
import json, os
import requests


class Acquisition():

    noSuchTableException = Exception('No such data table exists. Please see the ./data directory for allowed table names and either use one of the existing names or add this table to the list together with the api rquired to fetch it.')
    noSuchInfoException = Exception('No such information exists for this table. Please see the ./data directory for allowed information keys and either use one of the existing keys or add this new key to the list together with the required value.')
    cannotGetTableException = Exception('We cannot retrieve the data from this table, either because the api request failed or because you have requested not to get the data in the first place (check attributes of the methods you used).')


    @classmethod
    def _getInfoFromTableName(cls, whichData, info="filename"):
        if whichData not in CONFIG.DataSources:
            raise cls.noSuchTableException
        if info=="filename":
            if info not in CONFIG.DataSources[whichData]:
                raise cls.noSuchInfoException
            filename = CONFIG.DataSources[whichData][info]
            return os.path.join(CONFIG.DataDirectory, filename)
        elif info=="api":
            if info not in CONFIG.DataSources[whichData]:
                raise cls.noSuchInfoException
            return CONFIG.DataSources[whichData][info]
        else:
            if info not in CONFIG.DataSources[whichData]:
                raise cls.noSuchInfoException
            return CONFIG.DataSources[whichData][info]

    @classmethod
    def readDataLocally(cls, whichData="cg_asset_platforms", downloadIfMissing=True, forceUpdate=False):
        completeFilePath = cls._getInfoFromTableName(whichData=whichData, info="filename")
        isFileFlag = os.path.isfile(completeFilePath)
        if not isFileFlag:
            if downloadIfMissing:
                status = cls.updateDataLocally(whichData=whichData)
            if not downloadIfMissing or status!=200:
                raise cls.cannotGetTableException

        else:
            if forceUpdate:
                status = cls.updateDataLocally(whichData=whichData)
                if status!=200:
                    raise cls.cannotGetTableException
            
        
        with open(completeFilePath, "r") as file:
            returnData = json.load(file)

        return returnData

    @classmethod
    def updateDataLocally(cls, whichData="cg_asset_platforms"):
        completeFilePath = cls._getInfoFromTableName(whichData=whichData, info="filename")
        dataAPI = cls._getInfoFromTableName(whichData=whichData, info="api")
        req = requests.get(dataAPI)
        if req.status_code==200:
            with open(completeFilePath, "w") as file:
                json.dump(req.json(), file, indent=2)
        return req.status_code

