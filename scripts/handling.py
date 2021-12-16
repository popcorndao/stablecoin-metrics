from acquisition import Acquisition as Akw
from analysis import hurstExponent, revertingRate, stablecoinRevertingRate, stablecoinRevertingRateWithError
from datetime import datetime as dt, timedelta as td, timezone

import pandas as pd
import numpy as np


def addReversionAndVolatility(df,
                     granularity='days',
                     withVolatility=True,
                     discount_factor=0.,
                     windowSize=200,
                     minDataPoints=120,
                     sampleError=0.0001):
    
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

    granularitySeries = df["time"].apply(lambda x: int(x // factor))
    isIncrementable = (granularitySeries.diff(periods=1).abs()==1) | (granularitySeries.diff(periods=-1).abs()==1) 
    # availableDataPoints = isIncrementable.sum() - 1
    granularDf = df[isIncrementable].copy()
    granularDf["granular"] = granularDf["time"] // factor
    minTime = int(df.time.min() // factor)
    maxTime = int(df.time.max() // factor)

    rates = np.nan * np.zeros(granularDf.shape[0])
    rate_errors = np.nan * np.zeros(granularDf.shape[0])

    if withVolatility:
        sigmas = np.nan * np.zeros(granularDf.shape[0])
        sigma_errors = np.nan * np.zeros(granularDf.shape[0])


    for i, t in enumerate(range(minTime + windowSize, maxTime + 1)):
        
        filteredGranularDf = granularDf[(granularDf.granular >= (t - windowSize)) & (granularDf.granular <= t)]
        if filteredGranularDf.shape[0] < minDataPoints:
            rates[windowSize + i] = np.nan
            sigmas[windowSize + i] = np.nan
        else:
            # TODO! Replace discount_factor with weights (adjusted to the case that data is missing)
            result = stablecoinRevertingRateWithError(x=filteredGranularDf.price.values,
                                                delta=delta,
                                                with_sigma=True,
                                                discount_factor=discount_factor,
                                                sample_error=sampleError)
            rates[windowSize + i] = result["kappa"]
            rate_errors[windowSize + i] = result["kappa_error"]
            if withVolatility:
                sigmas[windowSize + i] = result["sigma"]
                sigma_errors[windowSize + i] = result["sigma_error"]
        
    granularDf["reversion"] = rates
    granularDf["reversion_error"] = rate_errors
    if withVolatility:
        granularDf["volatility"] = sigmas
        granularDf["volatility_error"] = sigma_errors

    return granularDf

    

   
def acquireDataFrame(whichData,
                    timestamp_from=0,
                    datetime_from=dt.now(),
                    timestamp_till=0,
                    datetime_till=dt.now(),
                    granularity='all',
                    includeOffPeg=False,
                    downloadIfMissing=True,
                    forceUpdate=False,
                    requestDataFromURL=False):
                
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
    
    return data
