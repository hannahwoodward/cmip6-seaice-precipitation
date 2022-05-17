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
