from dask.diagnostics import ProgressBar
from pathlib import Path
import cftime
import json
import netCDF4
import urllib
import xarray
import xesmf


def convert_to_360_day(i):
    o = i.copy()
    o_time = i.time.copy()
    for i, time in enumerate(o_time.values):
        o_time.values[i] = cftime.Datetime360Day(
            time.year, 
            time.month, 
            16, 
            has_year_zero=time.has_year_zero
        )

    o = o.assign_coords({ 'time': o_time })
    o.time.encoding['calendar'] = '360_day'

    return o


def download_variable(
    experiment_id,
    source_id,
    variable_id,
    frequency=None,
    grid_label='gn',
    variant_label=None,
    force_write=False,
    process_files=False,
    regrid_kwargs=None,
    save_to_local=False
):
    '''
    Function: download_variable()
        Retrieve a CMIP6 model output variable from CEDA 
        `https://esgf-index1.ceda.ac.uk/search/cmip6-ceda/`

    Inputs:
    (used in ceda query):
    - experiment_id (string): model experiment, e.g. 'historical', 'ssp585'
    - source_id (string): model source, e.g. 'UKESM1-0-LL'
    - variable_id (string): variable, e.g. 'pr'
    - variant_id (string): model realisation, e.g. 'r2i1p1f2'
    - frequency (string): frequency to query, e.g. 'mon'
        default: None
    - grid_label (string): grid label to query, e.g. 'gn', 'gr'
        default: 'gn'

    (for processing):
    - force_write (bool): whether to force write the resulting processed file
        (i.e. force_write will overrwrite an already existing file)
        default: False
    - process_files (bool): whether to merge multiple files, remap time
        to cftime 360_day, and regrid using regrid_kwargs (if specified)
        default: False
    - regrid_kwargs (dict): kwargs for libs.utils.regrid() if process_files
        is True, e.g.
        {
            'grid': target_grid,
            'extrap_method': 'nearest_s2d'
        }
        default: None
    - save_to_local (bool): whether to download files to local
        default: False
    '''
    base_url = 'https://esgf-index1.ceda.ac.uk/esg-search/search/'
    query = {
        'experiment_id': experiment_id,
        'format': 'application/solr+json',
        'grid_label': grid_label,
        'latest': 'true',
        'limit': 20,
        'mip_era': 'CMIP6',
        'offset': 0,
        'replica': 'false',
        'source_id': source_id,
        'type': 'Dataset',
        'variable_id': variable_id
    }
    if frequency != None:
        query['frequency'] = frequency

    if variant_label != None:
        query['variant_label'] = variant_label
    
    # Set custom User-Agent headers
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; U; Linux i686) Gecko/20071127 Firefox/2.0.0.11'
    }
    url = f'{base_url}?{urllib.parse.urlencode(query)}'
    print('Requesting:')
    print(f'-> {url}')
    try:
        req = urllib.request.Request(url, headers=headers)
        response = urllib.request.urlopen(req)
        if response.status < 200 or response.status > 299:
            msg = '\n'.join([
                f'An error occurred making request:', 
                f'-> URL: {url}',
                f'-> Status code: {response.status}',
            ])
            raise ConnectionError(msg)
    except Exception as e:
        print('An error occurred during initial query', e, sep='\n')
        return

    results = json.load(response)['response']['docs']
    if len(results) == 0:
        print('No results found')
        return

    print('Results:')
    for item in results:
        item_id = item['id']
        print(f'-> {item_id}')

        if not save_to_local:
            continue

        item_source_id = item['source_id'][0]
        item_local_path = f'_data/cmip6/{item_source_id}'
        try:
            local_filenames = download_remote_files(item, item_local_path, headers)
        except Exception as e:
            print('An error occurred downloading remote files', e, sep='\n')
            return

        if not process_files or len(local_filenames) == 0:
            continue

        print('-> Processing:')
        # Create merged array from files
        merged_array = xarray.open_mfdataset(
            paths=local_filenames, 
            combine='by_coords', 
            autoclose=True,
            use_cftime=True
        )
        merged_array = merged_array.chunk()
        print('   -> Merged')

        # Set time coord to 360_day and set encoding if merging and monthly data
        if 'time' in merged_array:
            if len(local_filenames) > 1:
                first_file = xarray.open_mfdataset(
                    paths=local_filenames[0], 
                    combine='by_coords', 
                    autoclose=True,
                    use_cftime=True
                )
                merged_array.time.encoding['units'] = first_file.time.encoding['units']
                merged_array.time.encoding['calendar'] = first_file.time.encoding['calendar']
                print('   -> Set time encoding')

            if merged_array.time.encoding['calendar'] != '360_day' and frequency == 'mon':
                merged_array = convert_to_360_day(merged_array)
                print('   -> Converted calendar to 360_day')

            # Select slice
            merged_array = merged_array.sel(time=slice('2015-01-01', '2101-01-01'))

        # Perform regridding
        if regrid_kwargs != None:
            merged_array = regrid(merged_array, **regrid_kwargs)
            print('   -> Regridded')

        # Generate new filename with updated date ranges
        merged_array_dates = merged_array[variable_id].time.values
        first_filename = str(local_filenames[0]).split('/')[-1]
        filename_split = first_filename.split('_')[0:-1] # Remove date range
        date_start = merged_array_dates[0].strftime('%Y%m')
        date_end = merged_array_dates[-1].strftime('%Y%m')
        filename_split.append(f'{date_start}-{date_end}') # Add new date range
        combined_filename = '_'.join(filename_split) + '_processed.nc'
        combined_path = Path(item_local_path, combined_filename)

        if combined_path.exists() and not force_write:
            print('   -> Processed file already exists, skipping write')
            merged_array.close()
            return

        # Write to file
        print(f'   -> Writing to {combined_path}')
        write = merged_array.to_netcdf(
            combined_path,
            compute=False
            #, engine='netcdf4'
        )
        with ProgressBar():
            write.compute()

        merged_array.close()
        print('   -> Saved')
        return combined_path


def download_remote_files(item, local_path, headers):
    '''
    Function: download_remote_files()
        Downlaoad remote files based off CEDA response item
        `https://esgf-index1.ceda.ac.uk/search_files/{item_id}/{item_index_node}/`

    Inputs:
    - item (dict): item from array response['response']['docs'] from request
        'https://esgf-index1.ceda.ac.uk/esg-search/search/'
    - local_path (string): path to save to (not including filename)

    Outputs:
    - (array): array of local paths
    '''
    item_id = item['id']
    item_index_node = item['index_node']
    url = f'https://esgf-index1.ceda.ac.uk/search_files/{item_id}/{item_index_node}/'
    req = urllib.request.Request(url, headers=headers)
    response = urllib.request.urlopen(req)
    if response.status < 200 or response.status > 299:
        msg = '\n'.join([
            f'An error occurred making request:', 
            f'-> URL: {url}',
            f'-> Status code: {response.status}',
            #f'-> Reason: {response.reason}'
        ])
        raise ConnectionError(msg)

    results = json.load(response)['response']['docs']
    local_filenames = []

    for item in results:
        file_url = [url.split('|')[0] for url in item['url'] if 'HTTPServer' in url]
        if len(file_url) == 0:
            continue

        file_url = file_url[0]
        filename = urllib.parse.urlparse(file_url).path.split('/')[-1]
        local_filename = Path(local_path, filename)
        local_filename.parent.mkdir(parents=True, exist_ok=True)
        local_filenames.append(local_filename) 

        if local_filename.exists():
            print(f'   -> Already exists, skipping: {local_filename}')
            continue

        print(f'   -> Downloading:')
        print(f'   -> {file_url}')
        print(f'   -> {local_filename}')
        file_response = urllib.request.urlretrieve(
            file_url,
            local_filename
        )

    return local_filenames


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


def regrid(
    data, 
    grid=xesmf.util.grid_global(1.875, 1.25), 
    method='bilinear', 
    extrap_method=None, 
    save_file=None
):
    regridder = xesmf.Regridder(data, grid, method=method, extrap_method=extrap_method)
    data_regridded = regridder(data)

    # Re-add attributes from original data
    if 'attrs' in data:
        for k in data.attrs:
            data_regridded.attrs[k] = data.attrs[k]

        # And for the main variable
        if 'variable_id' in data.attrs:
            var = data.attrs['variable_id']
            for k in data[var].attrs:
                data_regridded[var].attrs[k] = data[var].attrs[k]

    # Add new grid attribute
    if 'attrs' in grid and 'grid' in grid.attrs:
        # Preserve original grid attribute just in case
        if 'grid' in data_regridded.attrs:
            data_regridded.attrs['grid_original'] = data_regridded.attrs['grid']

        data_regridded.attrs['grid'] = grid.attrs['grid']

    if save_file != None:
        write = data_regridded.to_netcdf(save_file, compute=False)
        with ProgressBar():
            write.compute()

    return data_regridded
