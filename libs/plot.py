# -*- coding: utf-8 -*-

import cartopy.crs as ccrs
import cftime
import datetime
import libs.analysis
import libs.vars
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import xarray


def calendar_division_spatial(
    time_slices,
    colormesh_kwargs,
    time,
    units,
    col_var='ensemble',
    division='month',
    text='',
    title=''
):
    '''
    Function: calendar_division_spatial()
        Calculate monthly means for time slices and plot on a north stereographic
        projection (60-90°N)

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
    - time (string): month or season to average over
        allowed month values (in abbreviated format '%b'):
            ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN',
             'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC']
        allowed season values:
            ['DJF', 'MAM', 'JJA', 'SON']
    - division (string): type of time division
        allowed values: 'month', 'season'
        default: 'month'
    - col_var (string): controls plot layout, i.e. default value of 'ensemble' means
        that time_slices will vary by row, ensemble member will vary by column
        allowed values: 'time_slices', 'ensemble'
        default: 'ensemble'
    - text (string): variable text to be formatted in the plot title and colorbar
    - title (string): title of plot, will be formatted with time, label, units
        e.g. '{label} {time} ssp585 {text} 60-90°N ({units})'
        where label is either ensemble member or time slice depending on col_var/layout
        default: ''

    Outputs: None
    '''
    rows = time_slices
    if col_var == 'time_slices':
        rows = []
        for i, item in enumerate(time_slices[0]['ensemble']):
            row = [{
                'data': s['ensemble'][i]['data'],
                'label': s['label']
            } for s in time_slices]

            rows.append({
                'time_slices': row,
                'label': item['label']
            })

    for r in rows:
        label = r['label']
        cols = [{
            'data': libs.analysis.calendar_division_mean(item['data'], time, division),
            'label': item['label']
        } for item in r[col_var]]

        nstereo(
            cols,
            colorbar_label=f'{text} ({units})',
            colormesh_kwargs=colormesh_kwargs,
            title=title.format(label=label, text=text, time=time, units=units)
        )


def monthly_variability(
    arr,
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
    '''
    fig, ax = plt.subplots(figsize=(15, 7))
    fig.suptitle(title)
    yrange != None and ax.set_ylim(*yrange)
    monthly_variability_subplot(arr, ax, '', ylabel)
    place_legend(fig, ax, len(arr))
    fig.show()


def monthly_variability_regional(
    ensemble,
    title,
    ylabel,
    mask_type='latlon',
    calc_ensemble_mean=False,
    process=lambda x: x,
    yrange=None
):
    '''
    Function: monthly_variability_regional()
        Mask ensemble data to nsidc regions and plot monthly variability

    Inputs:
    - arr (xarray): array of data in format
        [{ 'label': (string), 'data': (xarray) }, ...]
    - title (string): axis title
    - ylabel (string): y-axis label
    - mask_type (string): whether to load mask on ocean or latlon grid
        allowed values: 'latlon', 'ocean'
        default: 'latlon'
    - calc_ensemble_mean (bool): whether to calculate ensemble mean
        default: False
    - process (function): process data before plotting, input is
        arr item['data'] which has been already masked to region
        default: lambda x: x
    - yrange (array): y-axis range e.g. [0, 5]
        default: None

    Outputs: None

    TODO:
    - color
    - automate ylim
    - legend below subplots?
    '''
    # Get all individual regions
    regions = [r for r in libs.vars.nsidc_regions() if len(r['values']) == 1]
    path_nsidc_mask = '_data/_cache/NSIDC_Regions_Masks_LatLon_nearest_s2d.nc'
    if mask_type == 'ocean':
        path_nsidc_mask = '_data/_cache/NSIDC_Regions_Masks_Ocean_nearest_s2d.nc'

    nsidc_mask = xarray.open_mfdataset(paths=path_nsidc_mask, combine='by_coords').mask

    if mask_type == 'latlon':
        nsidc_mask = nsidc_mask.roll(x=96, roll_coords=True)

    fig, axs = plt.subplots(3, 3, figsize=(15, 15))
    axs = axs.flatten()
    fig.suptitle(title)

    for i, region in enumerate(regions):
        ensemble_masked = [{
            'color': item['color'],
            'data': process(
                item['data'].where(np.isin(nsidc_mask.values, region['values']))
            ),
            'label': item['label']
        } for item in ensemble]

        if calc_ensemble_mean:
            ensemble_masked.append(libs.analysis.ensemble_mean(ensemble_masked))

        ax = axs[i]
        monthly_variability_subplot(ensemble_masked, ax, region['label'], ylabel)

    yrange != None and plt.setp(axs, ylim=yrange)
    place_legend(fig, axs[0], len(ensemble))
    fig.show()


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
    '''
    for i, item in enumerate(data):
        color = item['color'] if 'color' in item else None
        plot_kwargs = item['plot_kwargs'] if 'plot_kwargs' in item else {}
        item['data'].plot(ax=ax, label=item['label'], color=color, **plot_kwargs)

    ax.grid()
    ax.set_xlim(1, 12)
    months = np.arange(1, 13)
    month_ticks = ['J', 'F', 'M', 'A', 'M', 'J', 'J', 'A', 'S', 'O', 'N', 'D']
    ax.set_xticks(months) #, month_ticks)
    ax.set_xticklabels(month_ticks)
    ax.set(xlabel='Month', ylabel=ylabel)
    ax.set_title(title)


def nstereo(
    arr,
    title,
    colormesh_kwargs,
    colorbar_label='',
    shape=None,
    show_colorbar=True
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
        figsize=(5 * shape[1], 6 * shape[0]),
        subplot_kw={
            'projection': ccrs.Stereographic(central_latitude=90.0)
        }
    )
    fig.suptitle(title)
    transform = ccrs.PlateCarree()
    axs = axs.flatten() if len(arr) > 1 else [axs]

    subfigs = []
    for i, ax in enumerate(axs):
        if i >= len(arr):
            continue

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

    if show_colorbar:
        colorbar_ax = axs.ravel().tolist() if len(arr) > 1 else axs
        fig.colorbar(
            subfigs[0],
            ax=colorbar_ax,
            label=colorbar_label,
            location='bottom',
            pad=0.05,
            shrink=0.5
        )

    fig.show()


def place_legend(fig, ax, data_size):
    '''
    Function: place_legend()
        Automatically place legend based on data (i.e. ensemble) size.
        A plot of:
        - one dataset will have a legend placed in the best position on the
          passed in axis
        - multiple datasets will have a legend below the figure, with columns
          of maximum 5

    Inputs:
    - fig (matplotlib.figure.Figure): figure to place legend on
    - ax (matplotlib.axes.Axes): first (or chosen) axis to place legend on if data_size = 1
    - data_size (integer): number of datasets plotted on figure

    Outputs: None
    '''
    if data_size > 1:
        handles = []
        labels = []
        # Remove duplicate labels
        for a in fig.axes:
            a_handles, a_labels = a.get_legend_handles_labels()
            for i, label in enumerate(a_labels):
                if label not in labels:
                    handles.append(a_handles[i])
                    labels.append(label)

        legend_ncol = np.min([data_size, 5])
        fig.legend(
            handles=handles,
            labels=labels,
            bbox_to_anchor=(0.5, -0.1),
            fontsize=16,
            loc='lower center',
            ncol=legend_ncol
        )
    else:
        ax.legend(loc='best')

    fig.tight_layout()


def time_series(
    data,
    title,
    xattr,
    ylabel,
    process=lambda x: x,
    years=np.arange(1980, 2101, 20),
    yrange=None
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
    '''
    fig, ax = plt.subplots(figsize=(15, 7))
    fig.suptitle(title)
    xmin = None
    xmax = None
    for i, item in enumerate(data):
        label = item['label']
        color = item['color'] if 'color' in item else None
        plot_kwargs = item['plot_kwargs'] if 'plot_kwargs' in item else {}
        data_mod = process(item['data'].copy())
        data_mod.plot(ax=ax, label=label, color=color, **plot_kwargs)
        data_x_min = np.nanmin(data_mod[xattr])
        data_x_max = np.nanmax(data_mod[xattr])
        xmin = np.nanmin([xmin, data_x_min]) if xmin != None else data_x_min
        xmax = np.nanmax([xmax, data_x_max]) if xmax != None else data_x_max

    ax.set(xlabel='Year', ylabel=ylabel),
    ax.set_title('')
    ax.grid()
    ax.set_xlim(xmin, xmax)
    yrange != None and ax.set_ylim(*yrange)

    year_ticks = years
    if xattr == 'time':
        year_ticks = [cftime.Datetime360Day(y, 1, 1, 0, 0, 0) for y in years]
    ax.set_xticks(year_ticks) #, years)
    ax.set_xticklabels(years)
    place_legend(fig, ax, len(data))
