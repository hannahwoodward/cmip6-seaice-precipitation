import libs.analysis
import libs.local
import libs.plot
import libs.vars
import numpy as np
import xarray
xarray.set_options(keep_attrs=True);

def calc_variable_mean(data, subset=None, to_array='variable', var_name='Ensemble mean'):
    # Just in case 'Ensemble mean' already exists, delete + re-calculate
    if var_name in data:
        del data[var_name]

    ds = data
    if subset != None:
        ds = ds[subset]

    ensemble_mean = ds.to_array(to_array).mean(to_array, skipna=True)
    ensemble_mean.attrs['color'] = '#000'
    ensemble_mean.attrs['label'] = 'Ensemble mean'
    data[var_name] = ensemble_mean

    return data


def get_and_preprocess(
    component,
    experiment,
    variable_id,
    preprocess=lambda x, e, s, vl: x
):
    ensemble = libs.vars.ensemble()

    # Since variables have been regridded, can use UKESM areacello
    # for all ensemble member weighted means/sums
    areacello = libs.local.get_data('Ofx', 'piControl', 'UKESM1-0-LL', 'areacello', 'r1i1p1f2').areacello
    weight = areacello.fillna(0)

    # Get nsidc region mask, which has been regridded to UKESM ocean grid
    path_nsidc_mask = '_data/_cache/NSIDC_Regions_Masks_Ocean_nearest_s2d.nc'
    nsidc_mask = xarray.open_mfdataset(paths=path_nsidc_mask, combine='by_coords').mask
    nsidc_all = [
        r for r in libs.vars.nsidc_regions() if r['label'] == 'All'
    ][0]

    # Retrieve all ensemble data
    for i, item in enumerate(ensemble):
        source_id = item['source_id']
        variant_label = item['variant_label']

        kwargs = {
            'component': component,
            'experiment_id': experiment,
            'source_id': source_id,
            'variable_id': variable_id,
            'variant_label': variant_label,
            'include_hist': True
        }

        if variable_id in item:
            kwargs = { **kwargs, **item[variable_id] }

        var_base = libs.local.get_data(**kwargs)
        if type(var_base) not in [
            xarray.core.dataarray.DataArray,
            xarray.core.dataset.Dataset
        ]:
            continue

        # Mask to arctic + nsidc regions
        var_base[variable_id] = var_base[variable_id]\
            .where(var_base[variable_id].latitude > 60)\
            .where(np.isin(nsidc_mask.values, nsidc_all['values']))

        var_base[variable_id].attrs['label'] = var_base.attrs['source_id']
        var_base[variable_id].attrs['color'] = item['color']

        ensemble[i]['data'] = preprocess(
            var_base[variable_id],
            experiment,
            source_id,
            variant_label
        )
        ensemble[i]['label'] = var_base.attrs['source_id']

    ensemble = [item for item in ensemble if 'data' in item]

    return ensemble, weight


def time_series_full_variability(ensemble_series, plot_kwargs):
    for member in list(ensemble_series):
        kwargs = dict(plot_kwargs)
        kwargs['title'] = kwargs['title'].format(member=member)
        libs.plot.time_series_from_vars(ensemble_series, xattr='time', variables=[member], **kwargs)


def time_series_weighted(
    ensemble,
    weight,
    weighting_method,
    weighting_process,
    fillna=0,
    item_plot_kwargs={}
):
    ensemble_weighted_reduced = []
    ensemble_weighted_reduced_smooth = []

    for item in ensemble:
        item_data = weighting_process(item['data'])
        item_data_weighted = item_data.weighted(weight)

        # Reduce data, i.e. taking sum or average over spatial dimensions
        item_data_reduced = getattr(item_data_weighted, weighting_method)(
            dim=item_data_weighted.weights.dims,
            skipna=True
        )

        if fillna != None:
            item_data_reduced = item_data_reduced.fillna(fillna)

        item_base_kwargs = {
            'color': item['color'],
            'label': item['label'],
            'plot_kwargs': item_plot_kwargs
        }

        ensemble_weighted_reduced.append(
            { **item_base_kwargs, **{ 'data': item_data_reduced } }
        )
        ensemble_weighted_reduced_smooth.append(
            { **item_base_kwargs, **{ 'data': libs.analysis.smoothed_mean(item_data_reduced.fillna(0)) } }
        )

    return ensemble_weighted_reduced, ensemble_weighted_reduced_smooth
