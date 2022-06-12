import datetime
import libs.plot
import libs.vars
import xarray
xarray.set_options(keep_attrs=True);


def calendar_division_mean(data, time, division='month'):
    '''
    Function: calendar_division_mean()
        Filter data by specified month/season and calculate
        calculate monthly/seasonal mean values for each grid cell

    Inputs:
    - data (xarray): data to slice and process
    - time (string): month or season to average over
        allowed month values:
            ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN',
             'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC']
        allowed season values:
            ['DJF', 'MAM', 'JJA', 'SON']
    - division (string): type of time division
        allowed values: 'month', 'season'
        default: 'month'

    Outputs:
    - (xarray): processed data
    '''
    division_key = f'time.{division}'

    # Convert from %b to integer
    if division == 'month':
        time = datetime.datetime.strptime(time, '%b').month

    return data.copy()\
        .where(data.time[division_key] == time)\
        .mean(dim=('time'), skipna=True)


def climatology_monthly(data, date_start, date_end, relative=False):
    baseline = data.sel(time=slice(date_start, date_end))
    period = 'time.month'
    climatology = baseline.groupby(period).mean('time')

    if relative:
        return 100 * ((data.groupby(period) / climatology) - 1)

    return (data.groupby(period) - climatology)


'''
def climatology_seasonal(arr, date_start, date_end, season):
    baseline = arr[0].sel(time=slice(date_start, date_end))
    period = 'time.season'
    climatology = baseline.where(baseline.time[period] == season).mean('time')

    return [x.where(x.time[period] == season) - climatology for x in arr]
'''


def correlation_spatial_clim(
    ensemble_a,
    ensemble_b,
    climatology_period=slice('1980-01-01', '2011-01-01'),
    seasons=['DJF', 'MAM', 'JJA', 'SON']
):
    var_a_name = ensemble_a[0]['data'].name
    var_b_name = ensemble_b[0]['data'].name

    for s in seasons:
        ensemble_data = []

        for i, item in enumerate(ensemble_a):
            baseline_a = item['data']\
                .sel(time=climatology_period)\
                .where(item['data'].time['time.season'] == s)\
                .mean('time')

            item_a = item['data']\
                .where(item['data'].time['time.season'] == s) - baseline_a

            baseline_b = ensemble_b[i]['data']\
                .sel(time=climatology_period)\
                .where(ensemble_b[i]['data'].time['time.season'] == s)\
                .mean('time')

            item_b = ensemble_b[i]['data']\
                .where(ensemble_b[i]['data'].time['time.season'] == s) - baseline_b

            ensemble_data.append({
                'data': xarray.corr(item_a, item_b, dim='time'),
                'label': item['source_id']
            })


        libs.plot.nstereo(
            ensemble_data,
            title=f'{s} {var_a_name}/{var_b_name} correlation (climatology 1980-2010)',
            colorbar_label='Correlation',
            colormesh_kwargs={
                'cmap': 'RdBu_r',
                'extend': 'neither',
                'levels': 21,
                'vmin': -1,
                'vmax': 1,
                'x': 'longitude',
                'y': 'latitude'
            },
            shape=(1, len(ensemble_data))
        )


def ensemble_mean(ensemble):
    '''
    Function: ensemble_mean()

    Inputs:
    - ensemble (array): array with items formatted as
        { 'data': (xarray), 'label: (string) }

    Outputs:
    - (dict): the calculated mean in format
        { 'color': '#000', 'data': (xarray), 'label': 'Ensemble mean' }
    '''
    data = ensemble[0]['data'].copy()
    for item in ensemble[1:]:
        data += item['data']

    data /= len(ensemble)

    return {
        'color': '#000',
        'data': data,
        'label': 'Ensemble mean'
    }


def generate_slices(
    ensemble,
    item_plot_kwargs={},
    slices=libs.vars.default_time_slices()
):
    '''
    Function: generate_slices()

    Inputs:
    - ensemble (array): array with items formatted as
        {
            'color': (string),
            'data': (xarray),
            'label': (string),
            'plot_kwargs': (dict)
        }
    - slices (array): array of slices in format
        {
            'slice': { 'time': slice('2015-01-01', '2036-01-01') },
            'label': '2015-2035'
        }
        where 'slice' can be passed as kwargs into: ds.sel(**slice)
        default: libs.vars.default_time_slices()

    Outputs:
    - (array): array of slices with processed ensemble members, e.g.
        [{
            'label': '2015-2035',
            'ensemble': [
                 { 'color': (string), 'data': (xarray), 'label': (string) }, ...
            ]
        }, ...]
    '''
    slices_ensemble = []

    for s in slices:
        ensemble_processed = [{
            'color': item['color'],
            'plot_kwargs': item_plot_kwargs,
            'data': item['data'].sel(**s['slice']),
            'label': item['label']
        } for item in ensemble]

        slices_ensemble.append({
            'ensemble': ensemble_processed,
            'label': s['label']
        })

    return slices_ensemble


def monthly_weighted(data, weight, method='sum', dim=None):
    '''
    Function: monthly_weighted()
        Calculate area weighted sum or mean, grouped by month and averaged
        over time. It is recommended to first the slice data before calling
        this function.

    Inputs:
    - data (xarray): array of ensemble members
    - weight (xarray): array to weight data against (e.g. areacella)
    - method (string): whether to calculate mean or sum
        allowed values: 'sum', 'mean'
        default: 'sum'
    - dim (tuple): custom dimensions to sum over
        e.g. ('i', 'j') for ocean, ('lat', 'lon') for atmos
        default: None (all weighted dimensions summed)

    Outputs:
    - (xarray) processed data
    '''
    if method not in ['sum', 'mean']:
        print(f'Error: `method` should be either `sum` or `mean`, got {method}')
        return data

    data = data.copy()
    data_weighted = data.weighted(weight)
    dim = dim if dim != None else data_weighted.weights.dims

    return getattr(data_weighted, method)(dim=dim, skipna=True)\
        .fillna(0)\
        .groupby('time.month')\
        .mean('time')


def smoothed_mean(data, time=60):
    '''
    Function: smoothed_mean()
        Smooth data over rolling window

    Inputs:
    - data (xarray): data to smooth
    - time (int): length of rolling window, in months
        default: 60 (i.e. 5 years)

    Outputs:
    - (xarray): smoothed data
    '''
    return data.rolling(time=time, center=True).mean(dim=('month'))
