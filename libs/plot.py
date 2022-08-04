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


def legend_standalone(fig, legend_confs=[]):
    for i, a in enumerate(fig.axes):
        fig_legend, ax_legend = plt.subplots(1, 1, figsize=(1, 1))
        ax_legend.set_visible(False)

        exclude_list = legend_confs[i]['exclude']
        ncol = legend_confs[i]['ncol']
        handles = []
        labels = []
        a_handles, a_labels = a.get_legend_handles_labels()
        for i, label in enumerate(a_labels):
            if (label not in labels) and (label not in exclude_list):
                handles.append(a_handles[i])
                labels.append(label)

        fig_legend.legend(
            handles=handles,
            labels=labels,
            fontsize=15,
            ncol=ncol
        )


def monthly_variability(
    data,
    ylabel,
    cols=None,
    ax=None,
    fig=None,
    legend_below=False,
    show_legend=True,
    title=None,
    variables=None,
    yrange=None
):
    '''
    Function: monthly_variability()
        Plot a selection of data array variables
        with monthly averages on a single figure

    Inputs:
    - data (xarray or list(xarray)):
        DataArray/DataSet of time series data to plot.
        Optional used attrs: 'label', 'color'
    - title (string): title of plot
    - ylabel (string): y-axis label
    - yrange (array): y-axis range
        format: (min, max)
        default: None

    Outputs: None
    '''
    if type(data) != list:
        data = [data]

    variables = variables if variables != None else list(data[0])
    arr = [item[v] for item in data for v in variables if v in item]

    if fig == None:
        fig, ax = plt.subplots(figsize=(15, 7))
        fig.suptitle(title)

    yrange != None and ax.set_ylim(*yrange)
    monthly_variability_subplot(arr, ax, '', ylabel)
    show_legend and place_legend(fig, ax, len(variables), cols=cols, force_below=legend_below)
    fig.show()

    return fig


def monthly_variability_model(
    arr,
    title,
    ylabel,
    cols=None,
    legend_below=False,
    shape=(3, 3),
    variables=None,
    yrange=None
):
    fig, axs = plt.subplots(*shape, figsize=(5 * shape[1], 5 * shape[0]))
    axs = axs.flatten()
    fig.suptitle(title)

    for i, model_data in enumerate(arr):
        ax = axs[i]
        model_data = model_data if type(model_data) == list else [model_data]
        model_label = model_data[0].name
        monthly_variability_subplot(model_data, ax, model_label, ylabel)

    yrange != None and plt.setp(axs, ylim=yrange)
    place_legend(fig, axs[0], len(arr), cols=cols, force_below=legend_below)
    fig.show()


def monthly_variability_regional(
    arr,
    title,
    ylabel,
    cols=None,
    legend_below=False,
    shape=(3, 3),
    variables=None,
    yrange=None
):
    arr0 = arr[0][0] if type(arr[0]) == list else arr[0]
    variables = variables if variables != None else list(arr0)
    fig, axs = plt.subplots(*shape, figsize=(15, 15))
    axs = axs.flatten()
    fig.suptitle(title)

    for i, regional_data in enumerate(arr):
        ax = axs[i]
        regional_data = regional_data if type(regional_data) == list else [regional_data]
        regional_label = regional_data[0].attrs['region']
        regional_arr = [item[v] for item in regional_data for v in variables]
        monthly_variability_subplot(regional_arr, ax, regional_label, ylabel)

    yrange != None and plt.setp(axs, ylim=yrange)
    place_legend(fig, axs[0], len(variables), cols=cols, force_below=legend_below)
    fig.show()


def monthly_variability_subplot(arr, ax, title, ylabel):
    '''
    Function: monthly_variability_subplot()
        Plot an array of data on a given axis with
        monthly averages on a single figure

    Inputs:
    - arr (array): array of time series data to plot
        format: [{ 'data': (xarray), 'label': (string) }]
    - ax (matplotlib.pyplot.axis): axis on which to plot
    - title (string): axis title
    - ylabel (string): y-axis label

    Outputs: None
    '''
    for item in arr:
        color = item.attrs['color'] if 'color' in item.attrs else None
        label = item.attrs['label'] if 'label' in item.attrs else None
        plot_kwargs = item.attrs['plot_kwargs'] if 'plot_kwargs' in item.attrs else {}
        item.plot(ax=ax, label=label, color=color, **plot_kwargs)

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


def place_legend(fig, ax, data_size, cols=None, force_below=False):
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
    if force_below or data_size > 1:
        handles = []
        labels = []
        # Remove duplicate labels
        for a in fig.axes:
            a_handles, a_labels = a.get_legend_handles_labels()
            for i, label in enumerate(a_labels):
                if label not in labels:
                    handles.append(a_handles[i])
                    labels.append(label)

        legend_ncol = cols if cols != None else np.min([len(labels), 6])
        bbox_y = -0.1 if len(fig.axes) > 1 else -0.15
        fig.legend(
            handles=handles,
            labels=labels,
            bbox_to_anchor=(0.5, bbox_y),
            fontsize=15,
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
    cols=None,
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

    ax.set(xlabel='Year', ylabel=ylabel)
    ax.set_title('')
    ax.grid()
    ax.set_xlim(xmin, xmax)
    yrange != None and ax.set_ylim(*yrange)

    year_ticks = years
    if xattr == 'time':
        year_ticks = [cftime.Datetime360Day(y, 1, 1, 0, 0, 0) for y in years]
    ax.set_xticks(year_ticks) #, years)
    ax.set_xticklabels(years)
    place_legend(fig, ax, len(data), cols=cols)


def time_series_from_vars(
    data,
    xattr,
    ylabel,
    ax=None,
    fig=None,
    figsize=(15, 7),
    process=lambda x: x,
    show_legend=True,
    title='',
    variables=None,
    years=np.arange(1980, 2101, 20),
    yrange=None
):
    '''
    Function: time_series()
        Plot an array of time series on a single figure

    Inputs:
    - data (DataArray/DataSet or Array of DataArray/DataSet):
        array of time series data to plot
    - title (string): title of plot
    - xattr (string): time attribute name, e.g. 'time', 'year'
    - ylabel (string): y-axis label
    - process (function): process data before plotting
        default: lambda x: x
    - variables (array)
    - years (array): list of years to show on x-axis ticks
        default: np.arange(1980, 2101, 20)
    - yrange (array): y-axis range
        format: [min, max]
        default: None

    Outputs: None
    '''
    if type(data) != list:
        data = [data]

    variables = variables if variables != None else list(data[0])
    if fig == None:
        fig, ax = plt.subplots(figsize=figsize)
        title and fig.suptitle(title)

    xmin = None
    xmax = None
    for i, key in enumerate(variables):
        for item in data:
            if key not in item:
                continue

            label = key
            color = item[key].attrs['color'] if 'color' in item[key].attrs else None
            plot_kwargs = item[key].attrs['plot_kwargs'] if 'plot_kwargs' in item[key].attrs else {}
            item_mod = process(item[key].copy())
            item_mod.plot(ax=ax, label=label, color=color, **plot_kwargs)
            item_x_min = np.nanmin(item_mod[xattr])
            item_x_max = np.nanmax(item_mod[xattr])
            xmin = np.nanmin([xmin, item_x_min]) if xmin != None else item_x_min
            xmax = np.nanmax([xmax, item_x_max]) if xmax != None else item_x_max

    ax.set(xlabel='Year', ylabel=ylabel)
    ax.set_title('')
    ax.grid()
    ax.set_xlim(xmin, xmax)
    yrange != None and ax.set_ylim(*yrange)

    year_ticks = years
    if xattr == 'time':
        year_ticks = [cftime.Datetime360Day(y, 1, 1, 0, 0, 0) for y in years]
    ax.set_xticks(year_ticks) #, years)
    ax.set_xticklabels(years)
    show_legend and place_legend(fig, ax, len(variables))

    return fig
