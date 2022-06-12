# -*- coding: utf-8 -*-


def default_time_slices():
    '''
    Function: default_time_slices()
        Get the default time periods for analysis,
        use with .sel(**item['slice'])

    Outputs:
    - (array): slices
        format: [
            { 'slice': { 'time': slice('1980-01-01', '2011-01-01') }, 'label': '1980-2010' },
            { 'slice': { 'time': slice('2040-01-01', '2061-01-01') }, 'label': '2040-2060' },
            { 'slice': { 'time': slice('2080-01-01', '2101-01-01') }, 'label': '2080-2100' }
        ]
    '''

    return [
        { 'slice': { 'time': slice('1980-01-01', '2011-01-01') }, 'label': '1980-2010' },
        { 'slice': { 'time': slice('2040-01-01', '2061-01-01') }, 'label': '2040-2060' },
        { 'slice': { 'time': slice('2080-01-01', '2101-01-01') }, 'label': '2080-2100' }
    ]


def ensemble():
    return [
        {
            'areacello_variant_label': 'r1i1p1f2',
            'color': '#1982C4',
            'experiment_id': 'ssp585',
            'source_id': 'UKESM1-0-LL',
            'variant_label': 'r2i1p1f2'
        }, {
            'color': '#43AA8B',
            'experiment_id': 'ssp585',
            'source_id': 'NorESM2-LM',
            'variant_label': 'r1i1p1f1',
        }, {
        # NB currently status 404
        #    'experiment_id': 'ssp585',
        #    'source_id': 'CESM2-WACCM',
        #    'variant_label': 'r4i1p1f1',
        #}, {
        #    'experiment_id': 'ssp585',
        #    'source_id': 'CESM2',
        #   'variant_label': 'r4i1p1f1',
        #}, {
            # missing: sipr, dynamics, frazil, lateral melt, evapsubl
            'color': '#90BE6D',
            'experiment_id': 'ssp585',
            'source_id': 'CanESM5',
            'variant_label': 'r1i1p2f1',
        }, {
        # not included in keen et al. 2021
        #    'color': None,
        #    'experiment_id': 'ssp585',
        #    'source_id': 'CMCC-ESM2',
        #    'variant_label': 'r1i1p1f1',
        #}, {
            # No explicit lateral melt or frazil ice formation
            'color': '#FF924C',
            'experiment_id': 'ssp585',
            'source_id': 'ACCESS-CM2',
            'variant_label': 'r1i1p1f1',
        }, {
        # #F94144 #F3722C #577590 #4267AC #565AA0 #6A4C93
        #    # missing: No explicit lateral melt
            'color': '#FFCA3A',
            'experiment_id': 'ssp585',
            'source_id': 'EC-Earth3',
            'variant_label': 'r4i1p1f1',
            'evspsbl': { 'grid_label': 'gr' },
            'pr': { 'grid_label': 'gr' },
            'pr_siconc': { 'grid_label': 'gr' },
            'prsn': { 'grid_label': 'gr' },
            'prsn_siconc': { 'grid_label': 'gr' },
            'prra': { 'grid_label': 'gr' },
            'prra_siconc': { 'grid_label': 'gr' },
            'tas': { 'grid_label': 'gr' },
            'tas_siconc': { 'grid_label': 'gr' }
        }
    ]


def nsidc_regions():
    '''
    Function: nsidc_regions()
        Retrieve nsidc region mask values

        See:
        - https://github.com/CPOMUCL/CMIP6_data/blob/main/CMIP6_open_processed.ipynb
    '''
    return [
        { 'values': [6,7,8,9,10,11,12,13,15], 'label': 'All' },
        { 'values': [8,9,10,11,12,13,15], 'label': 'Arctic Ocean' },
        { 'values': [6], 'label': 'Labrador' },
        { 'values': [7], 'label': 'Greenland' },
        { 'values': [8], 'label': 'Barents' },
        { 'values': [9], 'label': 'Kara' },
        { 'values': [10], 'label': 'Siberian' },
        { 'values': [11], 'label': 'Laptev' },
        { 'values': [12], 'label': 'Chukchi' },
        { 'values': [13], 'label': 'Beaufort' },
        { 'values': [15], 'label': 'Central' },
    ]


def preprocess_evspsbl(data, experiment, source_id, variant_label):
    # Convert to s-1 => day-1
    data *= 86400

    # Fix inverted data
    if source_id == 'EC-Earth3':
        data *= -1

    return data


def preprocess_pr(data, experiment, source_id, variant_label):
    # Convert to s-1 => day-1
    return data * 86400


def preprocess_tas(data, experiment, source_id, variant_label):
    # Convert K -> C
    return data - 273.15


def variables():
    return [
        {
            'component': 'SImon',
            'text': 'sea-ice area',
            'units': 'km²',
            'variable_id': 'siconc',
            'weighting_method': 'sum',
            # Convert m2 => km2 and % to frac
            'weighting_process': lambda x: x / (1000 * 1000 * 100)
        },
        {
            'component': 'SImon',
            'text': 'sea-ice mass',
            'units': 'kg',
            'variable_id': 'simass',
            'weighting_method': 'sum',
            'weighting_process': lambda x: x
        },
        {
            'component': 'SImon',
            'text': 'sea-ice thickness',
            'units': 'm',
            'variable_id': 'sithick',
            'weighting_method': 'mean',
            'weighting_process': lambda x: x
        },
        {
            'component': 'SImon',
            'text': 'sea-ice snow layer thickness',
            'units': 'm',
            'variable_id': 'sisnthick',
            'weighting_method': 'mean',
            'weighting_process': lambda x: x
        },
        {
            'component': 'Amon',
            'preprocess': preprocess_pr,
            'text': 'precipitation over sea-ice and ocean',
            'units': 'mm day⁻¹',
            'variable_id': 'pr',
            'weighting_method': 'mean',
            'weighting_process': lambda x: x
        },
        {
            'component': 'Amon',
            'preprocess': preprocess_pr,
            'text': 'snowfall over sea-ice and ocean',
            'units': 'mm day⁻¹',
            'variable_id': 'prsn',
            'weighting_method': 'mean',
            'weighting_process': lambda x: x
        },
        {
            'component': 'Amon',
            'preprocess': preprocess_pr,
            'text': 'rainfall over sea-ice and ocean',
            'units': 'mm day⁻¹',
            'variable_id': 'prra',
            'weighting_method': 'mean',
            'weighting_process': lambda x: x
        },
        {
            'component': 'Amon',
            'preprocess': preprocess_pr,
            'text': 'precipitation over sea-ice',
            'units': 'mm day⁻¹',
            'variable_id': 'pr_siconc',
            'weighting_method': 'mean',
            'weighting_process': lambda x: x
        },
        {
            'component': 'Amon',
            'preprocess': preprocess_pr,
            'text': 'snowfall over sea-ice',
            'units': 'mm day⁻¹',
            'variable_id': 'prsn_siconc',
            'weighting_method': 'mean',
            'weighting_process': lambda x: x
        },
        {
            'component': 'Amon',
            'preprocess': preprocess_pr,
            'text': 'rainfall over sea-ice',
            'units': 'mm day⁻¹',
            'variable_id': 'prra_siconc',
            'weighting_method': 'mean',
            'weighting_process': lambda x: x
        },
        {
            'component': 'Amon',
            'preprocess': preprocess_tas,
            'text': 'surface air temperature over sea-ice and ocean',
            'units': '°C',
            'variable_id': 'tas',
            'weighting_method': 'mean',
            'weighting_process': lambda x: x
        },
        {
            'component': 'Amon',
            'preprocess': preprocess_tas,
            'text': 'surface air temperature over sea-ice',
            'units': '°C',
            'variable_id': 'tas_siconc',
            'weighting_method': 'mean',
            'weighting_process': lambda x: x
        },
        {
            'component': 'Amon',
            'preprocess': preprocess_evspsbl,
            'text': 'evaporation and sublimation over sea-ice and ocean',
            'units': 'mm day⁻¹',
            'variable_id': 'evspsbl',
            'weighting_method': 'mean',
            'weighting_process': lambda x: x
        }
    ]
