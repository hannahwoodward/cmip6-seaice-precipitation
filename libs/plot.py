# -*- coding: utf-8 -*-

import cartopy.crs as ccrs
import cftime
import datetime
import libs.helpers as helpers
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import xarray


def monthly_spatial(
    arr,
    colormesh_kwargs,
    units,
    months=['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC'],
    title=''
):
    '''
    Function: monthly_spatial()
        Calculate monthly means for time slices and plot on a north stereographic
        projection (60-90N)

    Inputs:
    - arr (array): array of data to plot
        format: [{ 'data': (xarray), 'label': (string) }]
    - colormesh_kwargs (dict): kwargs to pass to pcolormesh
        e.g.
        {
            'cmap': 'PuBu',
            'extend': 'max', # ['min', 'both']
            'vmin': 0,
            'vmax': 1,
            'x': 'longitude',
            'y': 'latitude'
        }
        See:
        - https://xarray.pydata.org/en/stable/generated/xarray.plot.pcolormesh.html
        - https://matplotlib.org/stable/gallery/color/colormap_reference.html
    - units (string): units to add to title and colorbar label
    - months (array): array of months (in abbreviated format '%b') to plot
        default: ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN',
                  'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC']
    - title (string): title of plot, will be formatted with m, label, units
        e.g. '{m} SSP585 {label} 60-90°N ({units})'
        default: ''

    Outputs: None
    '''
    for m in months:
        m_index = datetime.datetime.strptime(m, '%b').month

        for item in arr:
            data_mod = helpers.monthly_means_spatial(item['data'].copy(), m_index)
            label = item['label']

            nstereo(
                data_mod,
                title=title.format(m=m, label=label.lower(), units=units),
                colorbar_label=f'{label} ({units})',
                colormesh_kwargs=colormesh_kwargs
            )


def monthly_variability(
    data,
    title,
    ylabel,
    yrange=None
):
    '''
    Function: monthly_variability()
        Plot an array of data with monthly averages on a single figure
    
    Inputs:
    - data (array): array of time series data to plot
        format: [{ 'data': (xarray), 'label': (string) }]
    - title (string): title of plot
    - ylabel (string): y-axis label
    - yrange (array): y-axis range
        format: [min, max]
        default: None
    
    Outputs: None
    
    TODO:
    - color
    '''
    fig, ax = plt.subplots(figsize=(21, 6))
    fig.suptitle(title)
    yrange != None and ax.set_ylim(*yrange)
    monthly_variability_subplot(data, ax, '', ylabel)
    ax.legend(loc='best')


def monthly_variability_regional(
    data,
    title,
    ylabel,
    mask_type='latlon',
    process=lambda x: x,
    ylim=None
):
    '''
    Function: monthly_variability_regional()
        Mask data to nsidc regions and plot monthly variability

    Inputs:
    - data (xarray): data to process and plot
    - title (string): axis title
    - ylabel (string): y-axis label
    - process (function): process data before plotting
        default: lambda x: x
    - ylim (array): y-axis range
        e.g. [0, 5]
        default: None

    Outputs: None

    TODO:
    - color
    - automate ylim
    - legend below subplots?
    '''
    regions = helpers.nsidc_regions()
    path_nsidc_mask = '_data/_cache/NSIDC_Regions_Masks_LatLon_nearest_s2d.nc'
    if mask_type == 'ocean':
        path_nsidc_mask = '_data/_cache/NSIDC_Regions_Masks_Ocean_nearest_s2d.nc'

    nsidc_mask = xarray.open_mfdataset(paths=path_nsidc_mask, combine='by_coords').mask

    if mask_type == 'latlon':
        nsidc_mask = nsidc_mask.roll(x=96, roll_coords=True)

    fig, axs = plt.subplots(3, 3, figsize=(15, 15))
    axs = axs.flatten()
    fig.suptitle(title)

    for i, region in enumerate(regions[1:]):
        data_masked = data.copy().where(np.isin(nsidc_mask.values, region['values']))
        data_masked = process(data_masked)
        ax = axs[i]
        monthly_variability_subplot(data_masked, ax, region['label'], ylabel)
        i == 0 and ax.legend(loc='best')

    fig.tight_layout()
    ylim != None and plt.setp(axs, ylim=ylim)


def monthly_variability_subplot(data, ax, title, ylabel):
    '''
    Function: monthly_variability_subplot()
        Plot an array of data on a given axis with
        monthly averages on a single figure

    Inputs:
    - data (array): array of time series data to plot
        format: [{ 'data': (xarray), 'label': (string) }]
    - ax (matplotlib.pyplot.axis): axis on which to plot
    - title (string): axis title
    - ylabel (string): y-axis label

    Outputs: None

    TODO:
    - color
    '''
    for i, item in enumerate(data):
        item['data'].plot(ax=ax, label=item['label']) #, color=color)

    ax.grid()
    ax.set_xlim(1, 12)
    months = np.arange(1, 13)
    month_ticks = ['J', 'F', 'M', 'A', 'M', 'J', 'J', 'A', 'S', 'O', 'N', 'D']
    ax.set_xticks(months, month_ticks)
    ax.set(xlabel='Month', ylabel=ylabel)
    ax.set_title(title)


def nstereo(
    arr,
    title,
    colorbar_label, 
    colormesh_kwargs,
    shape=None
):
    '''
    Function: nstereo()
        Create a set of subplots on a north stereographic projection (60-90N)
    
    Inputs:
    - arr (array): array of data to plot
        format: [{ 'data': (xarray), 'label': (string) }]
    - title (string): title of plot
    - colorbar_label (string): colorbar label
    - colormesh_kwargs (dict): kwargs to pass to pcolormesh
        e.g. 
        {
            'cmap': 'PuBu',
            'extend': 'max', # ['min', 'both']
            'vmin': 0,
            'vmax': 1,
            'x': 'longitude',
            'y': 'latitude'
        }
        See:
        - https://xarray.pydata.org/en/stable/generated/xarray.plot.pcolormesh.html
        - https://matplotlib.org/stable/gallery/color/colormap_reference.html
        
    
    Outputs: None
    '''
    if shape == None:
        shape = (1, len(arr))

    fig, axs = plt.subplots(
        *shape,
        figsize=(15, 6 * shape[0]),
        subplot_kw={ 
            'projection': ccrs.Stereographic(central_latitude=90.0)
        }
    )
    fig.suptitle(title)
    transform = ccrs.PlateCarree()
    axs = axs.flatten() if len(arr) > 1 else [axs]
    
    subfigs = []
    for i, ax in enumerate(axs):
        ax.coastlines(resolution='110m', linewidth=0.5)
        ax.set_extent([-180, 180, 60, 90], transform)
        gl = ax.gridlines()
        gl.ylocator = matplotlib.ticker.LinearLocator(4)

        # Crop to circle
        theta = np.linspace(0, 2 * np.pi, 100)
        center, radius = [0.5, 0.5], 0.5
        verts = np.vstack([np.sin(theta), np.cos(theta)]).T
        circle = matplotlib.path.Path(verts * radius + center)
        ax.set_boundary(circle, transform=ax.transAxes)

        subfig = arr[i]['data'].plot.pcolormesh(
            add_colorbar=False,
            ax=ax,
            transform=transform,
            **colormesh_kwargs
        )
        ax.set_title(arr[i]['label'])
        subfigs.append(subfig)
    
    colorbar_ax = axs.ravel().tolist() if len(arr) > 1 else axs
    fig.colorbar(
        subfigs[0],
        ax=colorbar_ax,
        label=colorbar_label,
        location='bottom',
        pad=0.05,
        shrink=0.5
    )


def seasonal_spatial(
    arr,
    colormesh_kwargs,
    units,
    seasons=['DJF', 'MAM', 'JJA', 'SON'],
    title=''
):
    '''
    Function: seasonal_spatial()
        Calculate seasonal means for time slices and plot on a north stereographic
        projection (60-90N)

    Inputs:
    - arr (array): array of data to plot
        format: [{ 'data': (xarray), 'label': (string) }]
    - colormesh_kwargs (dict): kwargs to pass to pcolormesh
        e.g.
        {
            'cmap': 'PuBu',
            'extend': 'max', # ['min', 'both']
            'vmin': 0,
            'vmax': 1,
            'x': 'longitude',
            'y': 'latitude'
        }
        See:
        - https://xarray.pydata.org/en/stable/generated/xarray.plot.pcolormesh.html
        - https://matplotlib.org/stable/gallery/color/colormap_reference.html
    - units (string): units to add to title and colorbar label
    - seasons (array): array of seasons to plot
        default: ['DJF', 'MAM', 'JJA', 'SON']
    - title (string): title of plot, will be formatted with s, label, units
        e.g. '{s} SSP585 {label} 60-90°N ({units})'
        default: ''

    Outputs: None
    '''
    for s in seasons:
        for item in arr:
            data_mod = helpers.seasonal_means_spatial(item['data'].copy(), s)
            label = item['label']

            nstereo(
                data_mod,
                title=title.format(s=s, label=label.lower(), units=units),
                colorbar_label=f'{label} ({units})',
                colormesh_kwargs=colormesh_kwargs
            )


def time_series(
    data, 
    title, 
    xattr,
    ylabel,
    process=lambda x: x,
    years=np.arange(1980, 2101, 20),
    yrange=None, 
):
    '''
    Function: time_series()
        Plot an array of time series on a single figure
    
    Inputs:
    - data (array): array of time series data to plot
        format: [{ 'data': (xarray), 'label': (string) }]
    - title (string): title of plot
    - xattr (string): time attribute name, e.g. 'time', 'year'
    - ylabel (string): y-axis label
    - process (function): process data before plotting
        default: lambda x: x
    - years (array): list of years to show on x-axis ticks
        default: np.arange(1980, 2101, 20)
    - yrange (array): y-axis range
        format: [min, max]
        default: None
    
    Outputs: None
    
    TODO:
    - color
    '''
    fig, ax = plt.subplots(figsize=(21, 6))
    fig.suptitle(title)
    xmin = None
    xmax = None
    for i, item in enumerate(data):
        label = item['label']
        data_mod = process(item['data'].copy())
        data_mod.plot(ax=ax, label=label) #, color=color)
        data_x_min = np.nanmin(data_mod[xattr])
        data_x_max = np.nanmax(data_mod[xattr])
        xmin = np.nanmin([xmin, data_x_min]) if xmin != None else data_x_min
        xmax = np.nanmax([xmax, data_x_max]) if xmax != None else data_x_max

    ax.legend(loc='best')
    ax.set(xlabel='Year', ylabel=ylabel),
    ax.set_title('')
    ax.grid()
    ax.set_xlim(xmin, xmax)
    yrange != None and ax.set_ylim(*yrange)

    year_ticks = years
    if xattr == 'time':
        year_ticks = [cftime.Datetime360Day(y, 1, 1, 0, 0, 0) for y in years]
    ax.set_xticks(year_ticks, years)