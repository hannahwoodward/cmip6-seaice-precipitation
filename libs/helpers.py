# -*- coding: utf-8 -*-
import numpy as np
import os
import regionmask
import urllib
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


def get_data(
    experiment_id, 
    component, 
    var,
    variant_id,
    verbose=False,
    add_historical=False
):
    '''
    Function: get_data()
        Load a UKESM1 output variable from a local path with xarray.
        Format:
            '_data/cmip6/UKESM1/{var}_{component}_UKESM1-0-LL_{e_id}_{variant_id}_gn_{y}.nc'
    
    Inputs:
    - experiment_id (string): model experiment
        e.g. 'historical', 'ssp585'
    - component (string): model components
        e.g. 'Amon'
    - var (string): variable
        e.g. 'pr'
    - variant_id (string): model realisation
        e.g. 'r2i1p1f2'
    - verbose (bool): whether to output loading/errors
        default: False
    - add_historical (bool): whether to prepend historical runs to data
        default: False
    
    Outputs:
    - (xarray): loaded data
    
    TODO:
    - custom model [e.g. UKESM1-0-LL]
    - custom path?
    - remote download?
    '''
    
    # Ensure `_data` dir exists
    os.makedirs('_data', exist_ok=True)
    os.makedirs('_data/cmip6', exist_ok=True)
    
    # Set year ranges 
    years = ['201501-204912', '205001-210012']
    experiment_ids = [experiment_id, experiment_id]
    if experiment_id == 'historical':
        years = ['185001-194912', '195001-201412']
    elif add_historical:
        years[:0] = ['185001-194912', '195001-201412']
        experiment_ids[:0] = ['historical', 'historical']

    # Gather relevant files
    files = []
    for i, y in enumerate(years):
        e_id = experiment_ids[i]
        
        filename = f'{var}_{component}_UKESM1-0-LL_{e_id}_{variant_id}_gn_{y}.nc'
        local_file = f'_data/cmip6/UKESM1/{filename}'
        
        verbose and print(f'Loading {filename}')
        if not os.path.exists(local_file):
            verbose and print(f'-> Error 404. Exiting.')            
            #filepath = f'{base_url}/{ssp}/{component}/{var}/gn/{v}/{filename}'
            #urllib.request.urlretrieve(filepath, local_file)
            return None

        files.append(local_file)

    # Merge into single xarray & return
    return xarray.open_mfdataset(paths=files, combine='by_coords')


def monthly_means_time(data):
    '''
    Function: monthly_means_time()
        Create an array of sliced data which has each been sliced to a
        year range, averaged spatially (lat,lon) and monthly averages taken
    
    Inputs:
    - data (xarray): data to slice and process
    
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
        data = item['data']
        
        slices[i]['data'] = weighted(data)\
            .mean(dim=('lat', 'lon'), skipna=True)\
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


def weighted(data, region=None):
    '''
    Function: weighted()
        Create weighted data to lat-lon, 
        e.g. for taking spatial sum or mean
    
    Inputs:
    - data (xarray): data to slice and process
    - region (string): mask to regionmask region
        default: None
    
    Outputs:
    - (xarray): weighted data
    '''
    # Copy metadata from first time-step
    w = data[0, :, :] 
    w = np.cos(np.deg2rad(data.lat))
    w.name = 'weights'

    # TODO: multiple regions
    if region:
        mask = regionmask.defined_regions.ar6.all.mask(data[0, :, :])
        w = w.where(mask == region, 0) 

    return data.weighted(w)
