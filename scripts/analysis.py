import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from hurst import compute_Hc, random_walk

def revertingRate(x, delta=60, with_sigma=False):
    """mean reverting rate for processes centered around 0. 

    Args:
        x (numpy.ndarray): one dimensional numpy array of time series data
        delta (int, optional): timestep in minutes. Defaults to 60.
        with_sigma (bool, optional): include the volatility as an output parametera. Defaults to False.

    Returns:
        float or tuple: either a float with the reverting rate or a tuple of reverting rate and volatility.
    """
    xn = x[0:(len(x)-1)]
    xm = x[1:(len(x))]
    xnre = xn.reshape((-1,1))
    model = LinearRegression().fit(xnre,xm)
    m = model.coef_[0]
    logm = np.log(m)
    kappa = - logm / delta
    if with_sigma:
        diff = xm - model.predict(X=xnre)
        sigma = np.sqrt(diff.var() * ( - 2 * logm / (delta * (1-m**2))))
        return kappa, sigma
    return kappa

def stablecoinRevertingRate(x, delta=60, with_sigma=False):
    """mean reverting rate of a process centered around 1 (stable coin case).

    Args:
        x ([type]): [description]
        delta (int, optional): [description]. Defaults to 60.
        with_sigma (bool, optional): [description]. Defaults to False.

    Returns:
        [type]: [description]
    """
    return revertingRate(x=x-1, delta=delta, with_sigma=with_sigma)


def hurstExponent(x):
    H, _, _ = compute_Hc(x, kind='random_walk', simplified=True)
    return H