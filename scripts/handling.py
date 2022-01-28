from acquisition import Acquisition as Akw
from analysis import hurstExponent, revertingRate, stablecoinRevertingRate, stablecoinRevertingRateWithError
from datetime import datetime as dt, timedelta as td, timezone

import string
import random
import pandas as pd
import numpy as np
import hashlib



def addReversionAndVolatility(df,
                     granularity='days',
                     withVolatility=True,
                     discount_factor=0.,
                     windowSize=200,
                     minDataPoints=120,
                     sampleError=0.0001,
                     rsuffix=None,
                     verbose=True):
    
    ## only those which have an entry one granular unit before or after that entry
    if granularity=='hours':
        factor = 3600 * 1000
        delta = 1.0
    
    elif granularity=='5minutes':
        factor = 5 * 60 * 1000
        delta = 1./12
    
    elif granularity=='days':
        factor = 24 * 3600 * 1000
        delta = 24.

    else:
        factor = 1000
        delta = 1./3600

    if rsuffix is None:
        try:
            rsuffix = df._name
        except:
            rsuffix = ''.join(random.choices(string.ascii_uppercase, k = 3))

    granularitySeries = df["time"].apply(lambda x: int(x // factor))
    isIncrementable = (granularitySeries.diff(periods=1).abs()==1) | (granularitySeries.diff(periods=-1).abs()==1) 
    # availableDataPoints = isIncrementable.sum() - 1
    granularDf = df[isIncrementable].copy()
    granularDf["granular"] = granularDf["time"] // factor
    minTime = int(df.time.min() // factor)
    maxTime = int(df.time.max() // factor)

    # rates = np.nan * np.zeros(granularDf.shape[0])
    # rate_errors = np.nan * np.zeros(granularDf.shape[0])
    granularDeductWindowDf = granularDf[granularDf["granular"] >= granularDf["granular"].min() + windowSize]["granular"]
    if granularDeductWindowDf.empty:
        # print("No data to plot in this dataframe!")
        raise Exception("No data to plot in this dataframe! Choose another window width")
    
    data = {
        "rate": dict(),
        "rate_error": dict(),
    }
    
    if withVolatility:
        data.update({
            "sigma": dict(),
            "sigma_error": dict()
        })

    for i, t in enumerate(range(minTime + windowSize, maxTime + 1)):
        
        filteredGranularDf = granularDf[(granularDf.granular >= (t - windowSize)) & (granularDf.granular <= t)]
        
        if filteredGranularDf.shape[0] >= minDataPoints:
            # TODO: maybe only use the time t, where the last data has been recorded.
            if discount_factor>0:
                weights = (1 - discount_factor) ** (t - filteredGranularDf.granular.values[1:])
            else:
                weights = None

            result = stablecoinRevertingRateWithError(x=filteredGranularDf.price.values,
                                                delta=delta,
                                                with_sigma=True,
                                                weights=weights,
                                                sample_error=sampleError)
            data["rate"][t] = result["kappa"]
            data["rate_error"][t] = result["kappa_error"]

            if withVolatility:
                data["sigma"][t] = result["sigma"]
                data["sigma_error"][t] = result["sigma_error"]

    analysisDf = pd.DataFrame(data)
    analysisDf.rename({k: k + '_' + rsuffix for k in data}, axis=1, inplace=True)
    granularDf = granularDf.join(pd.DataFrame(data), how="left", rsuffix=rsuffix)

    try:
        granularDf._name = df._name
    except Exception as e:
        print(e)
        
    return granularDf


def addAverages(df, columns="price", com=5, inplace=True):

    if inplace:
        if isinstance(columns, str):
            df[columns + "_ewm"] = df[columns].ewm(com=com).mean()
        elif isinstance(columns, list):
            for col in columns:
                df[col + "_ewm"] = df[col].ewm(com=com).mean()
        
        return None

    else:
        df_new = df.copy()
        try:
            df_new._name = df._name
        except Exception as e:
            print(e)
        
        if isinstance(columns, str):
            df_new[columns + "_ewm"] = df[columns].ewm(com=com).mean()
        elif isinstance(columns, list):
            for col in columns:
                df_new[col + "_ewm"] = df[col].ewm(com=com).mean()
        
        return df_new



def getDataObject(whichData, 
                  requestDataFromURL=False):
    if requestDataFromURL:
        data, _ = Akw.readDataFromURL(whichData=whichData)
    else:
        data = Akw.readDataLocally(whichData=whichData)
    return data

   
def getDataFrame(whichData,
                    timestamp_from=0,
                    datetime_from=dt.now(),
                    timestamp_till=0,
                    datetime_till=dt.now(),
                    granularity='all',
                    includeOffPeg=False,
                    downloadIfMissing=True,
                    forceUpdate=False,
                    requestDataFromURL=False):
                
    # check whether filetype is csv
    if "json"==Akw._getInfoFromTableName(whichData=whichData, info="format"):
        raise Exception("Cannot get DataFrame for this table, try getDataObject()")

    if timestamp_till==0 and isinstance(datetime_from, dt) and isinstance(datetime_till, dt):
        timestamp_from = round(datetime_from.replace(tzinfo=timezone.utc).timestamp())
        timestamp_till = round(datetime_till.replace(tzinfo=timezone.utc).timestamp())


    if requestDataFromURL:
        # TODO: include status check
        data, _ = Akw.readDataFromURL(whichData=whichData,
                            **{"from":timestamp_from, "to":timestamp_till})
    else:
        data = Akw.readDataLocally(whichData=whichData,
                            downloadIfMissing=downloadIfMissing,
                            forceUpdate=forceUpdate,
                            **{"from":timestamp_from, "to":timestamp_till})

    data.sort_values(by='time', ascending=True, inplace=True)

    data["date"] = data.time.apply(lambda x: dt.fromtimestamp(x / 1000)) 

    if granularity=='hours':
        factor = 3600 * 1000
        data["hour"] = data["time"] // factor
        data = data.groupby("hour").first().copy()
    
    elif granularity=='5minutes':
        factor = 5 * 60 * 1000
        data["5minute"] = data["time"] // factor
        data = data.groupby("5minute").first().copy()
    

    elif granularity=='days':
        factor = 24 * 3600 * 1000
        data["day"] = data["time"] // factor
        data = data.groupby("day").first().copy()

    if includeOffPeg:
        data["off_peg"] = data.price.apply(lambda x: abs(x-1))
    
    # data.__hash__ = hashlib.sha1(str(data).encode("utf-8")).hexdigest()
    data._name = whichData
    return data
