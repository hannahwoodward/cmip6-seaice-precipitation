import libs.analysis
import libs.utils
import libs.plot
import libs.vars
import numpy as np
import xarray


def get_and_preprocess(
    component,
    experiment,
    variable_id,
    preprocess=lambda x, e, s, vl: x
):
    ensemble = libs.vars.ensemble()

    # Since variables have been regridded, can use UKESM areacello
    # for all ensemble member weighted means/sums
    areacello = libs.utils.get_data('Ofx', 'piControl', 'UKESM1-0-LL', 'areacello', 'r1i1p1f2').areacello
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

        var_base = libs.utils.get_data(
            component,
            experiment,
            source_id,
            variable_id,
            variant_label,
            include_hist=True
        )

        # Mask to arctic + nsidc regions
        var_base[variable_id] = var_base[variable_id]\
            .where(var_base[variable_id].latitude > 60)\
            .where(np.isin(nsidc_mask.values, nsidc_all['values']))

        ensemble[i]['data'] = preprocess(
            var_base[variable_id],
            experiment,
            source_id,
            variant_label
        )
        ensemble[i]['label'] = var_base.attrs['source_id']

    return ensemble, weight


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
    weighting_process
):
    for s in ensemble_time_slices:
        ensemble_processed = [{
            'color': item['color'],
            'data': libs.analysis.monthly_weighted(
                weighting_process(item['data']),
                weight,
                method=weighting_method
            ),
            'label': item['label']
        } for item in s['ensemble']]

        # Calculate and add ensemble mean
        ensemble_processed.append(libs.analysis.ensemble_mean(ensemble_processed))

        s_label = s['label']
        kwargs = dict(plot_kwargs)
        kwargs['title'] = kwargs['title'].format(s_label=s_label)
        libs.plot.monthly_variability(ensemble_processed, **kwargs)


def time_series_full_variability(ensemble_weighted_reduced, plot_kwargs):
    for item in ensemble_weighted_reduced:
        member = item['label']
        kwargs = dict(plot_kwargs)
        kwargs['title'] = kwargs['title'].format(member=member)
        libs.plot.time_series([item], xattr='time', **kwargs)


def time_series_weighted(ensemble, weight, weighting_method, weighting_process):
    ensemble_weighted_reduced = []
    ensemble_weighted_reduced_smooth = []

    for item in ensemble:
        item_data = weighting_process(item['data'])
        item_data_weighted = item_data.weighted(weight)

        # Reduce data, i.e. taking sum or average over spatial dimensions
        item_data_reduced = getattr(item_data_weighted, weighting_method)(
            dim=item_data_weighted.weights.dims,
            skipna=True
        ).fillna(0)

        item_base_kwargs = {
            'color': item['color'],
            'label': item['label']
        }

        ensemble_weighted_reduced.append(
            { **item_base_kwargs, **{ 'data': item_data_reduced } }
        )
        ensemble_weighted_reduced_smooth.append(
            { **item_base_kwargs, **{ 'data': libs.analysis.smoothed_mean(item_data_reduced) } }
        )

    ensemble_weighted_reduced_smooth.append(
        libs.analysis.ensemble_mean(ensemble_weighted_reduced_smooth)
    )

    return ensemble_weighted_reduced, ensemble_weighted_reduced_smooth
