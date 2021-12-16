# import config
from config import CONFIG

# import packages
import json, os
import requests

# import deepcopy
from copy import deepcopy

# import numpy and pandas
import numpy as np
import pandas as pd

# datetime
from datetime import datetime as dt


class Acquisition():
    """Class that handles data acquisition and retrieval."""

    ## Some common exceptions
    noSuchTableException = Exception('No such data table exists. Please see the ./data directory for allowed table names and either use one of the existing names or add this table to the list together with the api rquired to fetch it.')
    noSuchInfoException = Exception('No such information exists for this table. Please see the ./data directory for allowed information keys and either use one of the existing keys or add this new key to the list together with the required value.')
    cannotGetTableException = Exception('We cannot retrieve the data from this table, either because the api request failed or because you have requested not to get the data in the first place (check attributes of the methods you used).')
    cannotReachAPIEndpoint = lambda status: Exception('We pinged the API endpoint and cannot get through, because the status-code is: {code}.'.format(code=status))


    @classmethod
    def _setInfoFromTableName(cls, whichData, key="update", value=str(dt.now())):
        CONFIG.write(whichData=whichData, key=key, value=value)


    @classmethod
    def _getInfoFromTableName(cls, whichData, info="filename"):
        """method to obtain information about the data table

        Args:
            whichData (str): name of the data table.
            info (str, optional): key of the value that we want to retrieve. Defaults to "filename".

        Raises:
            cls.noSuchTableException: The table doesnt exist.
            cls.noSuchInfoException: The key doesnt exist.

        Returns:
            str or int: the value of the requested information.
        """
        if whichData not in CONFIG.DataSources:
            raise cls.noSuchTableException
        if info=="filename":
            if info not in CONFIG.DataSources[whichData]:
                raise cls.noSuchInfoException
            filename = CONFIG.DataSources[whichData][info]
            return deepcopy(os.path.join(CONFIG.DataDirectory, filename))
        elif info=="api":
            if info not in CONFIG.DataSources[whichData]:
                raise cls.noSuchInfoException
            return deepcopy(CONFIG.DataSources[whichData][info])
        else:
            if info not in CONFIG.DataSources[whichData]:
                raise cls.noSuchInfoException
            return deepcopy(CONFIG.DataSources[whichData][info])


    @classmethod
    def readDataLocally(cls, whichData="cg_asset_platforms", downloadIfMissing=True, forceUpdate=False, **kwargs):
        """Read data from a given table or fetch it, if its not there.

        Args:
            whichData (str, optional): selected data table. Defaults to "cg_asset_platforms".
            downloadIfMissing (bool, optional): [if data table cant be found, should it be fetched? Defaults to True.
            forceUpdate (bool, optional): update data irrespective of its current status. Defaults to False.

        Raises:
            cls.cannotGetTableException: cannot get table

        Returns:
            dict or list: return data from jsonized data-table. 
        """

        completeFilePath = cls._getInfoFromTableName(whichData=whichData, info="filename")
        isFileFlag = os.path.isfile(completeFilePath)
        
        # check whether csv-file exists. If not:
        if not isFileFlag:
            if downloadIfMissing:
                status = cls.updateDataLocally(whichData=whichData, **kwargs)
            if not downloadIfMissing or status!=200:
                raise cls.cannotGetTableException


        returnData = cls.fetchDataLocally(whichData=whichData, **kwargs)

        # only update when forceUpdate flag is put or new data is requested
        if "from" in kwargs and "to" in kwargs:
            minBiggerFrom = int(returnData.time.min() / 1000) > int(kwargs["from"])
            maxSmallerTo = int(returnData.time.max() / 1000) < int(kwargs["to"])
            newDataRequested = minBiggerFrom or maxSmallerTo
        else:
            newDataRequested = False

        if forceUpdate or newDataRequested:
            status = cls.updateDataLocally(whichData=whichData, **kwargs)
            if status!=200:
                raise cls.cannotGetTableException
            
            returnData = cls.fetchDataLocally(whichData=whichData, **kwargs)

        return returnData


    @classmethod
    def timeIntervalOfData(cls, whichData, form='datetime'):
        returnData = cls.fetchDataLocally(whichData=whichData)
        minTimestamp = returnData.time.min()
        maxTimestamp = returnData.time.max()
        if form=='timestamp':
            return int(minTimestamp), int(maxTimestamp)
        elif form=='datetime':
            return dt.fromtimestamp(minTimestamp / 1000), dt.fromtimestamp(maxTimestamp / 1000)
        else:
            raise Exception('Please provide a valid form. Either form="timestamp" or form="datetime"')
        

    @classmethod
    def readDataFromURL(cls, whichData, **kwargs):

        dataAPI = cls._getInfoFromTableName(whichData=whichData, info="api")
        defaultParams = cls._getInfoFromTableName(whichData=whichData, info="default_params")
        apiRawParams = cls._getInfoFromTableName(whichData=whichData, info="api_raw_params")
        dataStructure = cls._getInfoFromTableName(whichData=whichData, info="data_structure")
        dataApiFormatted = dataAPI.format(**apiRawParams)
        defaultParams.update(kwargs)
        req = requests.get(dataApiFormatted, params=defaultParams)
        if req.status_code==200:

            df = pd.DataFrame(data={
                key: get_data(data=req.json(),specs=val)
                for key, val in dataStructure.items()
            })
        else:
            df = pd.DataFrame()
    
        # drop duplicates
        if 'time' in df:
            df.drop_duplicates(subset='time', inplace=True)
        else:
            df.drop_duplicates(inplace=True)

        return df, req.status_code



    @classmethod
    def fetchDataLocally(cls, whichData, **kwargs):
        completeFilePath = cls._getInfoFromTableName(whichData=whichData, info="filename")
        isFileFlag = os.path.isfile(completeFilePath)
        
        # check whether csv-file exists. If not:
        if not isFileFlag:
            return pd.DataFrame()

        if not kwargs:
            return pd.read_csv(completeFilePath, sep=',', index_col=0)
        
        df = pd.read_csv(completeFilePath, sep=',', index_col=0)
        if "from" in kwargs and "to" in kwargs:

            return df[(df.time<=(kwargs["to"] * 1000)) & (df.time>=(kwargs["from"] * 1000))].copy()
        
        return df



    @classmethod
    def updateDataLocally(cls, whichData="cg_asset_platforms", **kwargs):
        """Updates data by writing into the respective data table (check data_sources.json for reference).

        Args:
            whichData (str, optional): name of the data table. Defaults to "cg_asset_platforms".

        Returns:
            int: status code for the request
        """

        ## TODO!! Use readDataFromURL method here.
        completeFilePath = cls._getInfoFromTableName(whichData=whichData, info="filename")
        dataAPI = cls._getInfoFromTableName(whichData=whichData, info="api")
        defaultParams = cls._getInfoFromTableName(whichData=whichData, info="default_params")
        apiRawParams = cls._getInfoFromTableName(whichData=whichData, info="api_raw_params")
        dataStructure = cls._getInfoFromTableName(whichData=whichData, info="data_structure")
        dataApiFormatted = dataAPI.format(**apiRawParams)
        defaultParams.update(kwargs)
        req = requests.get(dataApiFormatted, params=defaultParams)
        if req.status_code==200:

            df_new = pd.DataFrame(data={
                key: get_data(data=req.json(),specs=val)
                for key, val in dataStructure.items()
            })


            # fetch locally
            isFileFlag = os.path.isfile(completeFilePath)
            # check whether csv-file exists. If not:
            if isFileFlag:
                df = cls.fetchDataLocally(whichData=whichData)
                df_new = df.merge(df_new, on=list(df.columns), how="outer").copy()

            # drop duplicates
            if 'time' in df_new:
                df_new.drop_duplicates(subset='time', inplace=True)
            else:
                df_new.drop_duplicates(inplace=True)
   
            df_new.to_csv(completeFilePath, sep=',')
            cls._setInfoFromTableName(whichData=whichData, key="update", value=str(dt.now()))

        return req.status_code


    @classmethod
    def _ping(cls):
        req = requests.get('https://api.coingecko.com/api/v3/ping')
        if req.status_code != 200:
            raise cls.cannotReachAPIEndpoint(req.status_code)
        return req.status_code
        


def get_data(data, specs):
    """Recursive function to extract the desired time series from the data using the specs.

    Args:
        data ([type]): [description]
        specs ([type]): [description]

    Raises:
        Exception: [description]
        e: [description]

    Returns:
        [type]: [description]
    """
    if len(specs)==0:
        return data

    spec = specs.pop(0)
    type_of_operation = spec[0]
    try:
        if type_of_operation=="method":
            method_name = spec[1]
            args = spec[2]
            kwargs = spec[3]
            data = getattr(data, method_name)(*args, **kwargs)
        elif type_of_operation=="attribute":
            attribute_name = spec[1]            
            data = getattr(data, attribute_name)
        elif type_of_operation=="function":
            function_name = spec[1]
            args = spec[2]
            kwargs = spec[3]
            data = globals()[function_name](*args, **kwargs)
        elif type_of_operation=="module":
            module_name = spec[1]
            submodule_names = spec[2]
            args = spec[3]
            kwargs = spec[4]
            obj = globals()[module_name]
            for submodule in submodule_names:
                obj = getattr(obj, submodule)
            data = obj(data, *args, **kwargs)
        else:
            raise Exception('Neither method, nor function nor module! Please select!')
            
    except Exception as e:
        raise e

    return get_data(data=data, specs=specs)