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
