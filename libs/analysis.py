import libs.vars


def calendar_division_mean(data, time, division='month'):
    '''
    Function: calendar_division_mean()
        Filter data by specified month/season and calculate
        calculate monthly/seasonal mean values for each grid cell

    Inputs:
    - data (xarray): data to slice and process
    - time (int|string): month or season to average over
        month value should be an integer, i.e. JAN = 1, ..., DEC = 12
        season value should be in ['DJF', 'MAM', 'JJA', 'SON']
    - division (string): type of time division
        allowed values: 'month', 'season'
        default: 'month'

    Outputs:
    - (xarray): processed data
    '''
    division_key = f'time.{division}'

    return data.copy()\
        .where(data.time[division_key] == time)\
        .mean(dim=('time'), skipna=True)


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
    slices=libs.vars.default_time_slices()
):
    '''
    Function: ensemble_mean()

    Inputs:
    - ensemble (array): array with items formatted as
        { 'data': (xarray), 'label: (string) }
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
                 { 'data': (xarray), 'label: (string) }, ...
            ]
        }, ...]
    '''
    slices_ensemble = []

    for s in slices:
        ensemble_processed = [{
            'color': item['color'],
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
