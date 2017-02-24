import urllib2
from owslib.waterml.wml11 import WaterML_1_1 as wml11


def get_wml_values(url):
    response = urllib2.urlopen(url)
    data = response.read()
    series = wml11(data).response
    var = series.get_series_by_variable(var_name='Flow Forecast')
    vals = var[0].values[0]
    date_vals = vals.get_date_values()
    data = [[a, float(b)] for a, b in date_vals]

    return data