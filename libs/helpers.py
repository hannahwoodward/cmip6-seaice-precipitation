# -*- coding: utf-8 -*-
import numpy as np
import xarray


def default_slices(data):
    '''
    Function: default_slices()
        Create an array of data slices for analysis

    Inputs:
    - data (xarray): data to slice

    Outputs:
    - (array): slices
        format: [
            { 'data': data.sel(time=slice('2015-01-01', '2036-01-01')), 'label': '2015-2035' },
            { 'data': data.sel(time=slice('2040-01-01', '2061-01-01')), 'label': '2040-2060' },
            { 'data': data.sel(time=slice('2080-01-01', '2101-01-01')), 'label': '2080-2100' }
        ]

    TODO:
    - change first to 1980-2010
    '''

    return [
        { 'data': data.sel(time=slice('2015-01-01', '2036-01-01')), 'label': '2015-2035' },
        { 'data': data.sel(time=slice('2040-01-01', '2061-01-01')), 'label': '2040-2060' },
        { 'data': data.sel(time=slice('2080-01-01', '2101-01-01')), 'label': '2080-2100' }
    ]


def ensemble_mean(arr):
    data = arr[0]['data'].copy()
    for item in arr[1:]:
        data += item['data']

    data /= len(arr)

    return {
        'data': data,
        'label': 'Ensemble mean'
    }


def monthly_means_spatial(data, month):
    '''
    Function: monthly_means_spatial()
        Create an array of sliced data which has each been sliced to a
        year range and a monthly average taken

    Inputs:
    - data (xarray): data to slice and process
    - month (string): month to average over

    Outputs:
    - (array): slices
        format: [
            { 'data': (data), 'label': '2015-2035' },
            { 'data': (data), 'label': '2040-2060' },
            { 'data': (data), 'label': '2080-2100' }
        ]

    TODO:
    - change first to 1980-2010
    '''
    slices = default_slices(data)

    for i, item in enumerate(slices):
        slices[i]['data'] = item['data']\
            .where(item['data'].time['time.month'] == month)\
            .mean(dim=('time'), skipna=True)

    return slices


def monthly_means_time(data, weight, dim=None, fillna=False):
    '''
    Function: monthly_means_time()
        Create an array of sliced data which has each been sliced to a
        year range, averaged spatially over specified dims and a monthly
        mean taken
    
    Inputs:
    - data (xarray): data to slice and process
    - weight (xarray): array to weight data against (e.g. areacella)
    - dim (tuple): custom dimensions to average over
        e.g. ('i', 'j') for ocean, ('lat', 'lon') for atmos
        default: None (all weighted dimensions averaged)
    - fillna (bool): whether to fill any NaN values in the final
        time series with zero
    
    Outputs:
    - (array): slices
        format: [
            { 'data': (xarray), 'label': '2015-2035' },
            { 'data': (xarray), 'label': '2040-2060' },
            { 'data': (xarray), 'label': '2080-2100' }
        ]
    
    TODO:
    - change first to 1980-2010
    '''
    slices = default_slices(data)
    
    for i, item in enumerate(slices):
        data = item['data']
        data_weighted = data.weighted(weight)
        data_dim = dim if dim != None else data_weighted.weights.dims

        slices[i]['data'] = data_weighted\
            .mean(dim=data_dim, skipna=True)\
            .groupby('time.month')\
            .mean('time')
        
        if fillna:
            slices[i]['data'] = slices[i]['data'].fillna(0)

    return slices


def monthly_sums_time(data, weight, dim=None):
    '''
    Function: monthly_sums_time()
        Create an array of sliced data which has each been sliced to a
        year range, applied area weighting and summed over spatial dims

    Inputs:
    - data (xarray): data to slice and process
    - weight (xarray): array to weight data against (e.g. areacella)
    - dim (tuple): custom dimensions to sum over
        e.g. ('i', 'j') for ocean, ('lat', 'lon') for atmos
        default: None (all weighted dimensions summed)

    Outputs:
    - (array): slices
        format: [
            { 'data': (xarray), 'label': '2015-2035' },
            { 'data': (xarray), 'label': '2040-2060' },
            { 'data': (xarray), 'label': '2080-2100' }
        ]

    TODO:
    - change first to 1980-2010
    '''
    slices = default_slices(data)

    for i, item in enumerate(slices):
        data = item['data']
        data_weighted = data.weighted(weight)
        data_dim = dim if dim != None else data_weighted.weights.dims

        slices[i]['data'] = data_weighted\
            .sum(dim=data_dim, skipna=True)\
            .groupby('time.month')\
            .mean('time')

    return slices


def seasonal_means_spatial(data, season):
    '''
    Function: seasonal_means_spatial()
        Create an array of sliced data which has each been sliced to a
        year range and a seasonal average taken

    Inputs:
    - data (xarray): data to slice and process
    - season (string): season to average over [DJF, MAM, JJA, SON]

    Outputs:
    - (array): slices
        format: [
            { 'data': (data), 'label': '2015-2035' },
            { 'data': (data), 'label': '2040-2060' },
            { 'data': (data), 'label': '2080-2100' }
        ]

    TODO:
    - change first to 1980-2010
    '''
    slices = default_slices(data)

    for i, item in enumerate(slices):
        slices[i]['data'] = item['data']\
            .where(item['data'].time['time.season'] == season)\
            .mean(dim=('time'), skipna=True)

    return slices


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
