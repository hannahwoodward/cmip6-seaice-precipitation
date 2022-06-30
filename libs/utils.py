from dask.diagnostics import ProgressBar
from datetime import datetime
from nco import Nco
from pathlib import Path
import cftime
import json
import netCDF4
import urllib
import xarray
import xesmf


def compress_nc_file(path, output, options=['-7 -L 1']):
    '''
    Function compress_nc_file():
        Compress .nc file using `ncks` via pynco
        This can also be achieved via command line,
        e.g. cdo -f nc4c -z zip_9 copy $path $output
        See:
            https://github.com/nco/pynco
            http://nco.sourceforge.net/nco.html

    Inputs:
        - path (array): path of file to compress
        - output (string): filepath to write compressed to

    Output:
        - (string): compressed file path (same as output)
    '''
    nco = Nco()
    nco.ncks(input=str(path), output=str(output), options=options)
    return output


def convert_to_360_day(i):
    o = i.copy()
    o_time = i.time.copy()
    for i, time in enumerate(o_time.values):
        o_time.values[i] = cftime.Datetime360Day(
            time.year,
            time.month,
            16 #, has_year_zero=time.has_year_zero
        )

    o = o.assign_coords({ 'time': o_time })
    o.time.encoding['calendar'] = '360_day'

    return o


def daterange_from_filename(filename):
    '''
    Function daterange_from_filename():
        Get date range (as datetime objects) from filename.
        Assumes a filename ends with '_{date_start}-{date_stop}.nc'
        where dates are formatted as '%Y%m'

    Inputs:
        - filename (string): filename to get date range from

    Output:
        - (tuple): daterange (date_start, date_top)
    '''
    dates = filename.replace('.nc', '').split('_')[-1].split('-')

    return (
        datetime.strptime(dates[0], '%Y%m'),
        datetime.strptime(dates[1], '%Y%m')
    )


def download_variable(
    experiment_id,
    source_id,
    variable_id,
    frequency=None,
    grid_label='gn',
    table_id=None,
    variant_label=None,
    force_write=False,
    process_files=False,
    regrid_kwargs=None,
    save_to_local=False,
    time_slice=slice('2015-01-01', '2101-01-01')
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
    - frequency (string): frequency to query, e.g. 'mon'
        default: None
    - grid_label (string): grid label to query, e.g. 'gn', 'gr'
        default: 'gn'
    - table_id (string): grid label to query, e.g. 'Amon', 'SImon'
        default: None
    - variant_label (string): model realisation, e.g. 'r2i1p1f2'
        default: None

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
    #base_url = 'https://esgf-node.llnl.gov/esg-search/search/'
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

    if table_id != None:
        query['table_id'] = table_id

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

        date_out_of_bounds = False
        if time_slice != None:
            date_out_of_bounds = test_date_bounds(
                time_slice,
                test_start=datetime.strptime(item['datetime_start'], '%Y-%m-%dT%H:%M:%SZ'),
                test_stop=datetime.strptime(item['datetime_stop'], '%Y-%m-%dT%H:%M:%SZ')
            )

        if not save_to_local or date_out_of_bounds:
            continue

        item_source_id = item['source_id'][0]
        item_local_path = f'_data/cmip6/{item_source_id}/{variable_id}'
        try:
            local_filenames = download_remote_files(item, item_local_path, headers, time_slice)
        except Exception as e:
            print('An error occurred downloading remote files', e, sep='\n')
            return

        if not process_files or len(local_filenames) == 0:
            continue

        print('-> Processing:')

        # Merge into temp file for further processing
        # NB this uses ncrcat which preserves original compression
        merged_file_path = merge_nc_files(local_filenames, f'{item_local_path}/_merged.nc')
        print('   -> Merged')

        # Open merged file
        merged_array = xarray.open_mfdataset(
            paths=merged_file_path,
            combine='by_coords',
            autoclose=True,
            use_cftime=True
        )

        # Set time coord to 360_day and set encoding if merging and monthly data
        if 'time' in merged_array:
            if merged_array.time.encoding['calendar'] != '360_day' and frequency == 'mon':
                merged_array = convert_to_360_day(merged_array)
                print('   -> Converted calendar to 360_day')

            # Select slice
            merged_array = merged_array.sel(time=time_slice)

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
            # Cleanup & return
            print('   -> Processed file already exists, skipping write')
            merged_array.close()
            Path(merged_file_path).unlink()
            return combined_path

        # Write to file
        print(f'   -> Writing to {combined_path}')
        write = merged_array.to_netcdf(
            combined_path,
            compute=False,
            engine='netcdf4',
            unlimited_dims=['time']
        )
        with ProgressBar():
            write.compute()

        merged_array.close()
        print('   -> Saved to disk')

        # Finally, compress as to_netcdf() seems to produce large file sizes
        combined_path = compress_nc_file(combined_path, combined_path)
        print('   -> Compressed')

        # Delete temporary _merged.nc
        Path(merged_file_path).unlink()

        return combined_path


def download_remote_files(item, local_path, headers, time_slice=None):
    '''
    Function: download_remote_files()
        Downlaoad remote files based off CEDA response item
        `https://esgf-index1.ceda.ac.uk/search_files/{item_id}/{item_index_node}/`

    Inputs:
    - item (dict): item from array response['response']['docs'] from request
        'https://esgf-index1.ceda.ac.uk/esg-search/search/'
    - local_path (string): path to save to (not including filename)
    - headers
    - time_slice (slice): filter files against time_slice before downloading
        e.g. slice('2015-01-01', '2101-01-01')
        default: None

    Outputs:
    - (array): array of local paths
    '''
    item_id = item['id']
    item_index_node = item['index_node']
    url = f'https://esgf-index1.ceda.ac.uk/search_files/{item_id}/{item_index_node}/?limit=1000'
    #url = f'https://esgf-node.llnl.gov/search_files/{item_id}/{item_index_node}/?limit=1000'
    print(url)
    req = urllib.request.Request(url, headers=headers)
    response = urllib.request.urlopen(req)
    if response.status < 200 or response.status > 299:
        msg = '\n'.join([
            f'An error occurred making request:',
            f'-> URL: {url}',
            f'-> Status code: {response.status}'
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

        if time_slice != None:
            date_out_of_bounds = test_date_bounds(
                time_slice,
                *daterange_from_filename(filename)
            )
            if date_out_of_bounds:
                continue

        local_filename = Path(local_path, filename)
        local_filename.parent.mkdir(parents=True, exist_ok=True)
        local_filenames.append(str(local_filename))

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


def merge_nc_files(paths, output):
    '''
    Function merge_nc_files():
        Merge .nc files using `ncrcat` via pynco,
        which preserves original compression
        See:
            https://github.com/nco/pynco
            http://nco.sourceforge.net/nco.html

    Inputs:
        - paths (array): list of file paths to merge
        - output (string): merged filepath to write to

    Output:
        - (string): merged filepath (same as output)
    '''
    nco = Nco()
    nco.ncrcat(input=paths, output=output)
    return output


def regrid(
    data,
    grid=xesmf.util.grid_global(1.875, 1.25),
    method='bilinear',
    extrap_method=None,
    copy_dims=[],
    save_file=None
):
    # Check if the data already has the target grid
    if hasattr(data, 'attrs') and hasattr(grid, 'attrs'):
        if data.attrs['grid'] == grid.attrs['grid']:
            return data

    # Perform regridding
    regridder = xesmf.Regridder(data, grid, method=method, extrap_method=extrap_method)
    data_regridded = regridder(data)

    # Re-add attributes from original data
    if hasattr(data, 'attrs'):
        for k in data.attrs:
            data_regridded.attrs[k] = data.attrs[k]

        # And for the main variable
        if 'variable_id' in data.attrs:
            var = data.attrs['variable_id']
            for k in data[var].attrs:
                data_regridded[var].attrs[k] = data[var].attrs[k]

    # Add new grid attribute
    if hasattr(grid, 'attrs') and ('grid' in grid.attrs):
        # Preserve original grid attribute just in case
        if 'grid' in data_regridded.attrs:
            data_regridded.attrs['grid_original'] = data_regridded.attrs['grid']

        data_regridded.attrs['grid'] = grid.attrs['grid']

    for dim in copy_dims:
        data_regridded[dim] = grid[dim]

    if save_file != None:
        write = data_regridded.to_netcdf(save_file, compute=False)
        with ProgressBar():
            write.compute()

    return data_regridded


def test_date_bounds(time_slice, test_start, test_stop):
    time_stop = datetime.strptime(time_slice.stop, '%Y-%m-%d')
    date_out_of_bounds = test_start < test_start
    if date_out_of_bounds:
        return date_out_of_bounds

    time_start = datetime.strptime(time_slice.start, '%Y-%m-%d')
    date_out_of_bounds = time_start > test_stop
    return date_out_of_bounds
