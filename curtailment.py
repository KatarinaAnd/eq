from datetime import date, timedelta, datetime, time
from energyquantified import EnergyQuantified
from energyquantified.time import Frequency
eq = EnergyQuantified(api_key='e96733e2-ad4cd72f-a28593e6-06615ee4')
import pandas as pd
import matplotlib.pyplot as plt 
import numpy as np
from matplotlib import rc
import seaborn as sns
sns.set()




# fetch potential available renewable power

def pa_power(area, type_of_renewable, startdate, enddate):

    if type_of_renewable.lower() == 'solar' or type_of_renewable.lower() == 'pv':
        renewable = 'Solar Photovoltaic Production MWh/h 15min Forecast'
    else:
        renewable = 'Wind Power Production MWh/h 15min Forecast'
    

    pa_get = eq.instances.relative(
        '{} {}'.format(area, renewable),
        begin = startdate,
        end = enddate,
        tag = 'ec-ens',
        days_ahead = 1, # The day-ahead forecast (0 or higher allowed)
        time_of_day = time(0, 0),
        frequency = Frequency.PT1H
    )

    pa_power = pa_get.to_pandas_dataframe(name = '{} {} potential'.format(area, type_of_renewable))
    pa_power.index.name = 'date'
    pa_power.index = pa_power.index.tz_localize(None)
    pa_power = pa_power[~pa_power.index.duplicated()]

    return pa_power





# fetch actual renewable power

def actual_power(area, type_of_renewable, startdate, enddate):

    if area in ['NO1', 'NO2', 'NO3', 'NO4', 'SE1', 'SE2', 'SE3', 'SE3', 'SE4', 'FI', 'DK1', 'DK2', 'EE', 'LT', 'PL']:
        if type_of_renewable.lower() == 'solar' or type_of_renewable.lower() == 'pv':
            renewable = 'Solar Photovoltaic Production MWh/h H Actual'
        else:
            renewable = 'Wind Power Production MWh/h H Actual'
    elif area in ['FR', 'GB']:
        if type_of_renewable.lower() == 'solar' or type_of_renewable.lower() == 'pv':
            renewable = 'Solar Photovoltaic Production MWh/h 30min Actual'
        else:
            renewable = 'Wind Power Production MWh/h 30min Actual'
    else:
        
        if type_of_renewable.lower() == 'solar' or type_of_renewable.lower() == 'pv':
            renewable = 'Solar Photovoltaic Production MWh/h 15min Actual'

        else:
            renewable = 'Wind Power Production MWh/h 15min Actual'
    actual_get = eq.timeseries.load(
    '{} {}'.format(area,renewable),
    begin = startdate,
    end = enddate,
    frequency = Frequency.PT1H
    )

    actual_power = actual_get.to_pandas_dataframe(name = '{} {} actual'.format(area, type_of_renewable))
    actual_power.index.name = 'date'
    actual_power.index = actual_power.index.tz_localize(None)
    actual_power = actual_power[~actual_power.index.duplicated()]

    return actual_power





# fetch prices

def area_prices(area, startdate, enddate):

    curvenames = {
        'NO1': 'NO1 Price Spot EUR/MWh NordPool 15min Actual',
        'NO2': 'NO2 Price Spot EUR/MWh NordPool 15min Actual',
        'NO3': 'NO3 Price Spot EUR/MWh NordPool 15min Actual',
        'NO4': 'NO4 Price Spot EUR/MWh NordPool 15min Actual',
        'SE1': 'SE1 Price Spot EUR/MWh NordPool 15min Actual',
        'SE2': 'SE2 Price Spot EUR/MWh NordPool 15min Actual',
        'SE3': 'SE3 Price Spot EUR/MWh NordPool 15min Actual',
        'SE4': 'SE4 Price Spot EUR/MWh NordPool 15min Actual',
        'FI': 'FI Price Spot EUR/MWh NordPool 15min Actual',
        'DK1': 'DK1 Price Spot EUR/MWh NordPool 15min Actual',
        'DK2': 'DK2 Price Spot EUR/MWh NordPool 15min Actual',
        'EE': 'EE Price Spot EUR/MWh NordPool 15min Actual',
        'LV': 'LV Price Spot EUR/MWh NordPool 15min Actual',
        'LT': 'LT Price Spot EUR/MWh NordPool 15min Actual',       
        'DE': 'DE Price Spot EUR/MWh EPEX 15min Actual',
        'NL': 'NL Price Spot EUR/MWh EPEX 15min Actual',
        'PL': 'PL Price Spot EUR/MWh POLPX 15min Actual',
        'FR': 'FR Price Spot EUR/MWh EPEX 15min Actual',
        'GB': 'GB Price Spot EUR/MWh N2EX H Actual',
        'ES': 'ES Price Spot EUR/MWh OMIE 15min Actual',
        'IT': 'IT Price Spot EUR/MWh GME 15min Actual'
    }


    get_prices = eq.timeseries.load(
        '{}'.format(curvenames[area]),
        begin = startdate,
        end = enddate,
        frequency = Frequency.PT1H
    )


    prices = get_prices.to_pandas_dataframe(name='{} prices'.format(area))
    prices.index.name = 'date'
    prices.index = prices.index.tz_localize(None)
    prices = prices[~prices.index.duplicated()]

    return prices






def create_df(area, startdate, enddate):

    wind_actual = actual_power(area, 'wind', startdate, enddate)
    solar_actual = actual_power(area, 'solar', startdate, enddate)
    wind_pa = pa_power(area, 'wind', startdate, enddate)
    solar_pa = pa_power(area, 'solar', startdate, enddate)
    prices = area_prices(area, startdate, enddate)


    df = pd.concat([wind_actual, wind_pa, solar_actual, solar_pa, prices], axis = 1)
    df = df.rename(columns = {('{} wind actual'.format(area), '', ''):'{} wind actual'.format(area),
                              ('{} wind potential'.format(area), '', ''):'{} wind potential'.format(area),
                              ('{} solar actual'.format(area), '', ''):'{} solar actual'.format(area),
                              ('{} solar potential'.format(area), '', ''):'{} solar potential'.format(area),
                              ('{} prices'.format(area), '', ''):'{} prices'.format(area)})
    df.index.name = None


    df['{} WiSo potential'.format(area)] = df['{} wind potential'.format(area)] + df['{} solar potential'.format(area)]
    df['{} WiSo actual'.format(area)] = df['{} wind actual'.format(area)] + df['{} solar actual'.format(area)]


    delta_df = pd.DataFrame({'{} delta WiSo'.format(area): df['{} WiSo potential'.format(area)] - df['{} WiSo actual'.format(area)],
                             '{} delta wind'.format(area): df['{} wind potential'.format(area)] - df['{} wind actual'.format(area)],
                             '{} delta solar'.format(area): df['{} solar potential'.format(area)] - df['{} solar actual'.format(area)],
                             '{} prices'.format(area): df['{} prices'.format(area)]})
    

    
    delta_df = delta_df.sort_values('{} prices'.format(area))
    delta_df = delta_df.set_index('{} prices'.format(area))


    return df, delta_df




# plottefunksjon

def plot_shit(area, startdate, enddate):

    delta_df = create_df(area, startdate, enddate)[1]
    delta_df_f = delta_df.loc[delta_df.index <= 0] # removes all timestamps prices are above zero


    fig1, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(20, 5))
    fig1.suptitle('{} from {} to {}'.format(area, startdate, enddate))

    ax1.scatter(delta_df.index, delta_df['{} delta WiSo'.format(area)], s = 7, color = 'seagreen', alpha = 0.5)
    ax1.set_xlabel('price (€/MWh)')
    ax1.set_ylabel(r'$\Delta$ WiSo (MW)')
    ax1.xaxis.set_inverted(True)
    
    ax2.scatter(delta_df.index, delta_df['{} delta wind'.format(area)],  s = 7, color = 'steelblue', alpha = 0.5)
    ax2.set_xlabel('price (€/MWh)')
    ax2.set_ylabel(r'$\Delta$ wind (MW)')
    ax2.xaxis.set_inverted(True)

    ax3.scatter(delta_df.index, delta_df['{} delta solar'.format(area)], s = 7, color = 'goldenrod', alpha = 0.5)
    ax3.set_xlabel('price (€/MWh)')
    ax3.set_ylabel(r'$\Delta$ solar (MW)')
    ax3.xaxis.set_inverted(True)
    
    fig1.savefig('curtailment/{}.png'.format(area))


    fig2, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize = (20, 5))
    fig2.suptitle('Prices above zero, {} from {} to {}'.format(area, startdate, enddate))

    ax1.scatter(delta_df_f.index, delta_df_f['{} delta WiSo'.format(area)], s = 7, color = 'seagreen', alpha = 0.5)
    ax1.set_xlabel('price (€/MWh)')
    ax1.set_ylabel(r'$\Delta$ WiSo (MW)')
    ax1.xaxis.set_inverted(True)
    
    ax2.scatter(delta_df_f.index, delta_df_f['{} delta wind'.format(area)], s = 7, color = 'steelblue', alpha = 0.5)
    ax2.set_xlabel('price (€/MWh)')
    ax2.set_ylabel(r'$\Delta$ wind (MW)')
    ax2.xaxis.set_inverted(True)

    ax3.scatter(delta_df_f.index, delta_df_f['{} delta solar'.format(area)], s = 7, color = 'goldenrod', alpha = 0.5)
    ax3.set_xlabel('price (€/MWh)')
    ax3.set_ylabel(r'$\Delta$ solar (MW)')
    ax3.xaxis.set_inverted(True)

    fig2.savefig('curtailment/{}_filtered.png'.format(area))




    
list_of_areas = ['NO1', 'NO2', 'NO3', 'NO4', 'SE1', 'SE2', 'SE3', 'SE3', 'SE4', 'FI', 'DK1', 'DK2', 'EE', 'LT', 'DE', 'PL', 'FR', 'GB', 'ES', 'IT']

startdate = datetime(2024, 1, 1)
enddate = datetime(2024, 12, 31)
    
for i in list_of_areas:
    area = i
    plot_shit(area, startdate, enddate)
