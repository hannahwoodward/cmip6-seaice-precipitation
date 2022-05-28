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
            'pr': { 'grid_label': 'gr' },
            'prsn': { 'grid_label': 'gr' },
            'prra': { 'grid_label': 'gr' },
            'tas': { 'grid_label': 'gr' }
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
