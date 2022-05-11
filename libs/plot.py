# -*- coding: utf-8 -*-

import cartopy.crs as ccrs
import cftime
import matplotlib
import matplotlib.pyplot as plt
import numpy as np


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
    for i, item in enumerate(data):
        item['data'].plot(ax=ax, label=item['label']) #, color=color)

    ax.grid()
    ax.set_xlim(1, 12)
    yrange != None and ax.set_ylim(*yrange)
    
    months = np.arange(1, 13)
    month_ticks = ['J', 'F', 'M', 'A', 'M', 'J', 'J', 'A', 'S', 'O', 'N', 'D']
    ax.set_xticks(months, month_ticks)
    ax.legend(loc='best') 
    ax.set(xlabel='Month', ylabel=ylabel)
    ax.set_title('')


def nstereo(
    arr, 
    title, 
    colorbar_label, 
    colormesh_kwargs
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
            'vmax': 1
        }
        See:
        - https://xarray.pydata.org/en/stable/generated/xarray.plot.pcolormesh.html
        - https://matplotlib.org/stable/gallery/color/colormap_reference.html
        
    
    Outputs: None
    '''

    fig, axs = plt.subplots(
        1, 
        len(arr), 
        figsize=(15, 6),
        subplot_kw={ 
            'projection': ccrs.Stereographic(central_latitude=90.0)
        }
    )
    fig.suptitle(title)
    transform = ccrs.PlateCarree()
    
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
            levels=21,
            shading='flat',
            transform=transform,
            **colormesh_kwargs
        )
        ax.set_title(arr[i]['label'])
        subfigs.append(subfig)
    
    fig.colorbar(
        subfigs[0],
        ax=axs.ravel().tolist(),
        label=colorbar_label,
        location='bottom',
        pad=0.05,
        shrink=0.5
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