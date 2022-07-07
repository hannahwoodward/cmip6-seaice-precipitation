from pathlib import Path
import libs.vars
import xarray

def get_data(
    component,
    experiment_id,
    source_id,
    variable_id,
    variant_label,
    grid_label='gn',
    include_hist=False,
    suffix=None
):
    '''
    Function: get_data()
        Load a CMIP6 model output variable from a local path with xarray.
        Format:
        `_data/cmip6/{source_id}/{var}_{component}_{source_id}_{e_id}_{variant_id}_{grid_label}_{y}.nc`

    Inputs:
    - component (string): model components, e.g. 'Amon', 'SImon'
    - experiment_id (string): model experiment, e.g. 'historical', 'ssp585'
    - source_id (string): model family, e.g. 'UKESM1-0-LL'
    - variable_id (string): variable, e.g. 'pr', 'siconc'
    - variant_label (string): model realisation, e.g. 'r2i1p1f2'
    - grid_label (string): grid label, e.g. 'gn', 'gr'
        default: 'gn'
    - include_hist (bool): whether to join historical data (suffix '_198001-201412_processed')
        default: False
    - suffix (string): filename suffix, e.g. '_201501-210012_processed'
        default: None

    Outputs:
    - (xarray): loaded data
    '''
    if suffix == None:
        suffix = '' if variable_id in ['areacella', 'areacello'] else '_201501-210012_processed'

    basepath = f'_data/cmip6/{source_id}/{variable_id}/'
    filename = f'{variable_id}_{component}_{source_id}_{experiment_id}_{variant_label}_{grid_label}{suffix}.nc'
    filepaths = [f'{basepath}{filename}']

    if include_hist:
        experiment_id = 'historical'
        suffix = '_198001-201412_processed'

        filename = f'{variable_id}_{component}_{source_id}_{experiment_id}_{variant_label}_{grid_label}{suffix}.nc'
        filepaths.append(f'{basepath}{filename}')

    for filepath in filepaths:
        if not Path(filepath).exists():
            print('Error 404', f'-> {filepath}', sep='\n')
            return None

    return xarray.open_mfdataset(paths=filepaths, combine='by_coords', use_cftime=True)


def get_ensemble_regional_series(variable_id, experiment, suffix=''):
    return [get_ensemble_series(
        variable_id,
        experiment,
        region=r['label'],
        suffix=suffix
    ) for r in libs.vars.nsidc_regions() if len(r['values']) == 1]


def get_ensemble_series(variable_id, experiment, region='All', suffix=''):
    time_series_filename = f'{variable_id}_{experiment}_{region}_198001-210012{suffix}.nc'
    time_series_path = f'_data/_cache/{variable_id}/{time_series_filename}'

    data = xarray.open_mfdataset(paths=time_series_path, combine='by_coords', use_cftime=True)

    for variable in list(data):
        if 'label' not in data[variable].attrs:
            data[variable].attrs['label'] = variable

    return data
