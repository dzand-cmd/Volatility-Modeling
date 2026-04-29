import numpy as np
import pandas as pd
from arch import arch_model

def rolling_volatility(returns, window=21):
    """
    returns: pandas Series
    window: rolling window (e.g., 21 for ~1 month)
    """
    return returns.rolling(window).std()

def ewma_volatility(returns, lam=0.94):
    """
    lam: decay factor (0.94 is standard for daily data)
    """
    returns = np.array(returns)
    var = np.zeros(len(returns))
    
    # initialize
    var[0] = np.var(returns)
    
    for t in range(1, len(returns)):
        var[t] = lam * var[t-1] + (1 - lam) * returns[t-1]**2
    
    return np.sqrt(var)

def garch11_volatility(returns, omega=0.000001, alpha=0.05, beta=0.9):
    returns = np.array(returns)
    var = np.zeros(len(returns))
    
    var[0] = np.var(returns)
    
    for t in range(1, len(returns)):
        var[t] = omega + alpha * returns[t-1]**2 + beta * var[t-1]
    
    return np.sqrt(var)

# simulate returns (replace with real data)
np.random.seed(0)
returns = pd.Series(np.random.normal(0, 0.02, 1000))

# compute volatilities
roll_vol = rolling_volatility(returns)
ewma_vol = ewma_volatility(returns)
garch_vol = garch11_volatility(returns)

print(roll_vol.tail())
print(ewma_vol[-5:])
print(garch_vol[-5:])