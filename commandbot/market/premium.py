import requests
import json


# https://stackoverflow.com/questions/15389768/standard-deviation-of-a-list
def mean(data):
    """Return the sample arithmetic mean of data."""
    n = len(data)
    if n < 1:
        raise ValueError('mean requires at least one data point')
    return sum(data)/n # in Python 2 use sum(data)/float(n)

def _ss(data):
    """Return sum of square deviations of sequence data."""
    c = mean(data)
    ss = sum((x-c)**2 for x in data)
    return ss

def stddev(data, ddof=0):
    """Calculates the population standard deviation
    by default; specify ddof=1 to compute the sample
    standard deviation."""
    n = len(data)
    if n < 2:
        raise ValueError('variance requires at least two data points')
    ss = _ss(data)
    pvar = ss/(n-ddof)
    return pvar**0.5


def get():
    market = 'Premium'
    url = 'http://coinpremiums.jaeholee.org/json'

    try:
        result = ""
        premiums_response = requests.get(url).json()

        for exchange, exchange_currencies in premiums_response['premium'].items():
            result += '{} >> '.format(exchange.title())
            premiums = []

            for currency_name, currency in exchange_currencies.items():
                premium = currency['raw'] - 1
                result += '[{}] {:.2%} '.format(currency_name.upper(), premium)
                premiums.append(premium)

            p_stddev = stddev(premiums)
            p_mean = mean(premiums)

            adjusted_premiums = [p for p in premiums if abs(p_mean - p) <= p_stddev * 2]
            result += '[평균(adj)] {:.2%} \n'.format(mean(adjusted_premiums))
    except Exception as e:
        result = '[{market}] error! : {msg}'.format(market=market, msg=e.__repr__())

    return result
