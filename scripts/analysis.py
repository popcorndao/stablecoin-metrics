import numpy as np
import pandas as pd
from copy import deepcopy
from sklearn.linear_model import LinearRegression
from hurst import compute_Hc, random_walk

def discount(n, start=1, factor=0.5, normalize=False):
    """iterator for exponentially discounted weights

    Args:
        n (int): number of entries
        start (int, optional): initial number. Defaults to 1.
        factor (float, optional): discounting factor. Defaults to 0.5.
        normalize (bool, optional): whether weights should be normalized. Defaults to False.

    Raises:
        Exception: Discount iterator requires the factor to be between 0 and 1

    Yields:
        float: discounted number
    """
    
    if factor<0 or factor>1:
        raise Exception('Discount iterator requires the factor to be between 0 and 1')
    if normalize:
        start =  (1 - factor) / (1 - factor ** (n))
    i = 0
    while i < n:
        yield start
        start *= factor
        i += 1


def perturbator(x, epsilon):
    if len(x)<1:
        raise Exception('x is too short. Needs to be at least of length 1')
    for i in range(len(x)):
        y = deepcopy(x)
        y[i] += epsilon
        yield y 



def revertingRate(x, delta=24.0, with_sigma=False, discount_factor=0.):
    """mean reverting rate for processes centered around 0. 

    Args:
        x (numpy.ndarray): one dimensional numpy array of time series data
        delta (int, optional): sampling interval in hours. Defaults to 24.
        with_sigma (bool, optional): include the volatility as an output parametera. Defaults to False.
        discount_factor (float, optional): the exponential weighing factor for the regression. Must be zero or positive. Zero mean no weights. Defaults to 0.

    Returns:
        dict: either a float with the reverting rate or a tuple of reverting rate and volatility.
    """
    xn = x[0:(len(x)-1)]
    xm = x[1:(len(x))]
    xnre = xn.reshape((-1,1))
    if discount_factor>0:
        weights = list(discount(n=len(xm),factor=discount_factor, normalize=True))
        weights.reverse()
        model = LinearRegression().fit(X=xnre, y=xm, sample_weight=weights)
    else:
        model = LinearRegression().fit(X=xnre, y=xm)
    m = model.coef_[0]
    if m<=0:
        logm = np.nan
        kappa = np.nan
    else:
        logm = np.log(m)
        kappa = - logm / delta
    if with_sigma:
        diff = xm - model.predict(X=xnre)
        sigma = np.sqrt(diff.var() * ( - 2 * logm / (delta * (1-m**2))))
        return {"kappa": kappa, "sigma": sigma}
    return {"kappa": kappa, "sigma": None}


def stablecoinRevertingRate(x, delta=24.0, with_sigma=False, discount_factor=0):
    """mean reverting rate of a process centered around 1 (stable coin case).

    Args:
        x (numpy.ndarray): time series of the stable coin price with respect to its peg asset (should be pegged to 1)
        delta (int, optional): sampling interval in hours. Defaults to 24.
        with_sigma (bool, optional): return the volatility, too. Defaults to False.

    Returns:
        float or tuple: either a float with the reverting rate or a tuple of reverting rate and volatility.
    """
    return revertingRate(x=x-1, delta=delta, with_sigma=with_sigma, discount_factor=discount_factor)


def revertingRateWithError(x, delta=24., discount_factor=0., with_sigma=True, sample_error=0.001):
    kwargs = dict(delta=delta,
                  discount_factor=discount_factor,
                  with_sigma=with_sigma)
    kappa_devs = np.zeros(len(x))
    sigma_devs = np.zeros(len(x))
    null_res = revertingRate(x=x, **kwargs)
    for i, x_pert in enumerate(perturbator(x, epsilon=sample_error)):
        res = revertingRate(x=x_pert, **kwargs)
        kappa_devs[i] = (res["kappa"] - null_res["kappa"])
        if with_sigma:
            sigma_devs[i] = (res["sigma"] - null_res["sigma"])

    # updating the error contributions
    null_res.update({"kappa_error": np.sqrt(kappa_devs ** 2).sum()})
    if with_sigma:
        null_res.update({"sigma_error": np.sqrt(sigma_devs ** 2).sum()})

    return null_res


def stablecoinRevertingRateWithError(x, delta=24.0, with_sigma=False, discount_factor=0, sample_error=0.001):
    """mean reverting rate of a process centered around 1 (stable coin case).

    Args:
        x (numpy.ndarray): time series of the stable coin price with respect to its peg asset (should be pegged to 1)
        delta (int, optional): sampling interval in hours. Defaults to 24.
        with_sigma (bool, optional): return the volatility, too. Defaults to False.

    Returns:
        float or tuple: either a float with the reverting rate or a tuple of reverting rate and volatility.
    """
    return revertingRateWithError(x - 1, delta=delta, discount_factor=discount_factor, with_sigma=with_sigma, sample_error=sample_error)



def hurstExponent(x, with_error=True):
    """Hurst Exponent of the time series

    Args:
        x (numpy.ndarray): one dimensional numpy array of time series

    Returns:
        float: Hurst exponent between 0 and 1, where 0.5 is a random walk.
    """
    H1, _, _ = compute_Hc(x, kind='random_walk', simplified=True)
    if with_error:
        H2, _, _ = compute_Hc(x[1:], kind='random_walk', simplified=True)
        H3, _, _ = compute_Hc(x[:-1], kind='random_walk', simplified=True)
        H4, _, _ = compute_Hc(x[2:], kind='random_walk', simplified=True)
        H5, _, _ = compute_Hc(x[:-2], kind='random_walk', simplified=True)
        Hs = np.array([H1,H2,H3,H4,H5])
        return {"mean": np.nanmean(Hs), "sigma": np.nanmean(Hs)}
    else:
        return {"mean": H1}