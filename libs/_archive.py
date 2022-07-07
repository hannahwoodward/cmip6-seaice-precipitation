from dask.diagnostics import ProgressBar
from pathlib import Path
import xarray

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
        `_data/cmip6/UKESM1-0-LL/{var}_{component}_UKESM1-0-LL_{e_id}_{variant_id}_gn_{y}.nc`

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
    - custom year ranges/grid size
    '''
    # Ensure `_data` dir exists
    base_path = Path('_data/cmip6')
    base_path.mkdir(parents=True, exist_ok=True)

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
        local_file = f'_data/cmip6/UKESM1-0-LL/{filename}'

        verbose and print(f'Loading {filename}')
        if not Path(local_file).exists():
            verbose and print(f'-> Error 404. Exiting.')
            return None

        files.append(local_file)

    # Merge into single xarray & return
    return xarray.open_mfdataset(paths=files, combine='by_coords')


def write_netcdf_with_encoding(data, path):
    spatial_encoding = {
        'zlib': True,
        'shuffle': False,
        'complevel': 4,
        'fletcher32': False,
        'contiguous': False
    }

    data.longitude.encoding = spatial_encoding
    data.longitude.encoding['chunksizes'] = data.longitude.shape
    data.longitude.encoding['original_shape'] = data.longitude.shape

    data.latitude.encoding = spatial_encoding
    data.latitude.encoding['chunksizes'] = data.latitude.shape
    data.latitude.encoding['original_shape'] = data.latitude.shape

    data.time.encoding['chunksizes'] = (1,)

    write = data.to_netcdf(
        path,
        compute=False,
        unlimited_dims=['time'],
        engine='netcdf4'
    )
    with ProgressBar():
        write.compute()


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


def monthly_variability_regional(
        ensemble_time_slices,
        plot_kwargs,
        weight,
        weighting_method,
        weighting_process
    ):
        for s in ensemble_time_slices:
            s_label = s['label']
            kwargs = dict(plot_kwargs)
            kwargs['title'] = kwargs['title'].format(s_label=s_label)

            libs.plot.monthly_variability_regional(
                s['ensemble'],
                calc_ensemble_mean=True,
                mask_type='ocean',
                process=lambda x: libs.analysis.monthly_weighted(
                    weighting_process(x),
                    weight,
                    method=weighting_method
                ),
                **kwargs
            )

            print(' ')


    def monthly_variability_full(
        ensemble_time_slices,
        plot_kwargs,
        weight,
        weighting_method,
        weighting_process,
        calc_ensemble_mean=True,
    ):
        for s in ensemble_time_slices:
            ensemble_processed = [{
                'color': item['color'],
                'data': libs.analysis.monthly_weighted(
                    weighting_process(item['data']),
                    weight,
                    method=weighting_method
                ),
                'label': item['label'],
                'plot_kwargs': item['plot_kwargs'] if 'plot_kwargs' in item else {}
            } for item in s['ensemble']]

            # Calculate and add ensemble mean
            calc_ensemble_mean and ensemble_processed.append(libs.analysis.ensemble_mean(ensemble_processed))

            s_label = s['label']
            kwargs = dict(plot_kwargs)
            kwargs['title'] = kwargs['title'].format(s_label=s_label)
            libs.plot.monthly_variability(ensemble_processed, **kwargs)
