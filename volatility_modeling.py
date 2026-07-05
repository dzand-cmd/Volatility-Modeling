import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.interpolate import griddata
from scipy.stats import norm
import yfinance as yf
from mpl_toolkits.mplot3d import Axes3D

def rolling_volatility(returns, window=21):
    return returns.rolling(window).std() * np.sqrt(252)

def ewma_volatility(returns, lam=0.94):
    returns = np.array(returns)
    var = np.zeros(len(returns))
    var[0] = np.var(returns)

    for t in range(1, len(returns)):
        var[t] = lam * var[t-1] + (1 - lam) * returns[t-1]**2

    return np.sqrt(var * 252)

def garch11_volatility(returns, omega=1e-6, alpha=0.05, beta=0.9):
    returns = np.array(returns)
    var = np.zeros(len(returns))
    var[0] = np.var(returns)

    for t in range(1, len(returns)):
        var[t] = omega + alpha * returns[t-1]**2 + beta * var[t-1]

    return np.sqrt(var * 252)

def implied_vol_bisection(price, S, K, T, r, option_type="call"):
    def bs_price(vol):
        d1 = (np.log(S/K) + (r + 0.5*vol**2)*T) / (vol*np.sqrt(T))
        d2 = d1 - vol*np.sqrt(T)

        if option_type == "call":
            return S*norm.cdf(d1) - K*np.exp(-r*T)*norm.cdf(d2)
        else:
            return K*np.exp(-r*T)*norm.cdf(-d2) - S*norm.cdf(-d1)

    low, high = 1e-6, 5.0

    for _ in range(50):
        mid = (low + high) / 2
        if bs_price(mid) > price:
            high = mid
        else:
            low = mid

    return (low + high) / 2

def get_iv_surface(ticker="AAPL"):
    asset = yf.Ticker(ticker)
    S = asset.history(period="1d")["Close"].iloc[-1]

    surfaces = []

    for expiry in asset.options[:3]: 
        opt_chain = asset.option_chain(expiry)
        calls = opt_chain.calls

        T = (pd.to_datetime(expiry) - pd.Timestamp.today()).days / 365

        for i, row in calls.iterrows():
            if row["bid"] > 0 and row["ask"] > 0:
                mid_price = (row["bid"] + row["ask"]) / 2
                iv = implied_vol_bisection(mid_price, S, row["strike"], T, 0.02, "call")
                surfaces.append([row["strike"], T, iv])

    return pd.DataFrame(surfaces, columns=["strike", "T", "iv"])

def plot_iv_surface(df):
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    ax.scatter(df["strike"], df["T"], df["iv"])

    ax.set_xlabel("Strike")
    ax.set_ylabel("Time to Maturity")
    ax.set_zlabel("Implied Vol")

    plt.title("Implied Volatility Surface")
    plt.show()

def local_vol_surface(df):
    df = df.sort_values(["T", "strike"])
    df["dIV_dK"] = df.groupby("T")["iv"].diff()
    df["d2IV_dK2"] = df.groupby("T")["iv"].diff().diff()
    df["local_vol"] = np.sqrt(df["iv"]**2 + df["d2IV_dK2"].fillna(0))

    return df

def heston_simulation(S0, v0, kappa, theta, xi, rho, T, steps=252, paths=1000):
    dt = T / steps
    S = np.zeros((paths, steps))
    v = np.zeros((paths, steps))
    S[:, 0] = S0
    v[:, 0] = v0

    for t in range(1, steps):
        Z1 = np.random.normal(size=paths)
        Z2 = rho * Z1 + np.sqrt(1 - rho**2) * np.random.normal(size=paths)

        v[:, t] = np.abs(v[:, t-1] + kappa * (theta - v[:, t-1]) * dt + xi * np.sqrt(v[:, t-1] * dt) * Z2)

        S[:, t] = S[:, t-1] * np.exp(-0.5 * v[:, t-1] * dt + np.sqrt(v[:, t-1] * dt) * Z1)

    return S, v

def build_vol_surface(df):
    strikes = df["strike"].values
    maturities = df["T"].values
    ivs = df["iv"].values

    K_grid = np.linspace(min(strikes), max(strikes), 50)
    T_grid = np.linspace(min(maturities), max(maturities), 50)

    K_mesh, T_mesh = np.meshgrid(K_grid, T_grid)

    IV_mesh = griddata(
        (strikes, maturities),
        ivs,
        (K_mesh, T_mesh),
        method="cubic"
    )

    return K_mesh, T_mesh, IV_mesh

def plot_vol_surface(K_mesh, T_mesh, IV_mesh):
    fig = plt.figure()
    ax = fig.add_subplot(111, projection="3d")

    ax.plot_surface(K_mesh, T_mesh, IV_mesh, cmap="viridis")

    ax.set_xlabel("Strike")
    ax.set_ylabel("Maturity (T)")
    ax.set_zlabel("Implied Volatility")

    plt.title("Implied Volatility Surface")
    plt.show()



if __name__ == "__main__":
    np.random.seed(0)
    returns = pd.Series(np.random.normal(0, 0.02, 1000))

    print("Rolling Vol:", rolling_volatility(returns).tail())
    print("EWMA Vol:", ewma_volatility(returns)[-5:])
    print("GARCH Vol:", garch11_volatility(returns)[-5:])

    df = get_iv_surface("AAPL")
    print(df.head())
    plot_iv_surface(df)

    S, v = heston_simulation(
        S0=100,
        v0=0.04,
        kappa=2.0,
        theta=0.04,
        xi=0.3,
        rho=-0.7,
        T=1
    )

    K_mesh, T_mesh, IV_mesh = build_vol_surface(df)

    plot_vol_surface(K_mesh, T_mesh, IV_mesh)

    print("Heston simulation done")