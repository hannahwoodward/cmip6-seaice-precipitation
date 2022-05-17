from dask.diagnostics import ProgressBar
from pathlib import Path
import cftime
import json
import libs.utils
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
            merged_array = libs.utils.regrid(merged_array, **regrid_kwargs)
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
            compute=False,
            engine='netcdf4'
        )
        with ProgressBar():
            write.compute()

        merged_array.close()
        print('   -> Saved')
        return


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


def regrid(
    data, 
    grid=xesmf.util.grid_global(1.875, 1.25), 
    method='bilinear', 
    extrap_method=None, 
    save_file=None
):
    regridder = xesmf.Regridder(data, grid, method=method, extrap_method=extrap_method)
    data_regridded = regridder(data)
    save_file != None and data_regridded.to_netcdf(save_file)

    return data_regridded
