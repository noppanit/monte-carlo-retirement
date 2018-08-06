import os
import pandas as pd

try:
    import urllib2  # python2
except:
    import urllib.request as urllib2  # python3

csv_file = os.getcwd() + '/data/shiller.csv'

if not os.path.exists(csv_file):
    xls_url = 'http://www.econ.yale.edu/~shiller/data/chapt26.xlsx'
    url = urllib2.urlopen(xls_url)

    xls = pd.ExcelFile(url)
    df = xls.parse('Data', skiprows=[0, 1, 3, 4, 5, 6, 7],
                   skip_footer=5, index_col=0)

    df.to_csv(csv_file)

else:
    df = pd.read_csv(csv_file, index_col=0)

cpi = df['CPI']  # Consumer Price Index
gs10 = df['RLONG'] / 100.  # convert from percent to fraction, Long Government Bond Yield

stock_price = df['P']  # S&P Composite Price Index
stock_div = df['D']  # Divided accuring to index


## Computing annualized changes

def annualized_changes(x):
    return x.diff() / x


# Inflation rate
inflation = annualized_changes(cpi)

# Stock market rate of return
stock_increase = stock_price.diff() + stock_div
stock_returns = stock_increase / stock_price

interest_rates = gs10

dates = cpi.index
