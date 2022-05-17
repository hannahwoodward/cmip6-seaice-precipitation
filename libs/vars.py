# -*- coding: utf-8 -*-


def ensemble():
    return [
        {
            'experiment_id': 'ssp585',
            'source_id': 'UKESM1-0-LL',
            'variant_label': 'r2i1p1f2',
        }, {
            'experiment_id': 'ssp585',
            'source_id': 'NorESM2-LM',
            'variant_label': 'r1i1p1f1',
        }, {
            'experiment_id': 'ssp585',
            'source_id': 'CESM2-WACCM',
            'variant_label': 'r4i1p1f1',
        }, {
            'experiment_id': 'ssp585',
            'source_id': 'CESM2',
            'variant_label': 'r4i1p1f1',
        }, {
            # missing: sipr, dynamics, frazil, lateral melt, evapsubl
            'experiment_id': 'ssp585',
            'source_id': 'CanESM5',
            'variant_label': 'r1i1p2f1',
        }, {
            'experiment_id': 'ssp585',
            'source_id': 'CMCC-ESM2',
            'variant_label': 'r1i1p1f1',
        }, {
            # No explicit lateral melt or frazil ice formation
            'experiment_id': 'ssp585',
            'source_id': 'ACCESS-CM2',
            'variant_label': 'r1i1p1f1',
        }
        #, {
        #    # missing: sipr, No explicit lateral melt
        #    'experiment_id': 'ssp585',
        #    'source_id': 'GFDL-ESM4',
        #    'variant_label': 'r1i1p1f1'
        #}
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
