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

def time_slices_20y():
    # https://coolors.co/palette/f94144-f3722c-f8961e-f9c74f-90be6d-43aa8b-4d908e-277da1
    return [
        { 'slice': { 'time': slice('1980-01-01', '2001-01-01') }, 'label': '1980-2000', 'color': '#43aa8b' },
        { 'slice': { 'time': slice('2000-01-01', '2021-01-01') }, 'label': '2000-2020', 'color': '#90be6d' },
        { 'slice': { 'time': slice('2020-01-01', '2041-01-01') }, 'label': '2020-2040', 'color': '#f9c74f' },
        { 'slice': { 'time': slice('2040-01-01', '2061-01-01') }, 'label': '2040-2060', 'color': '#f8961e' },
        { 'slice': { 'time': slice('2060-01-01', '2081-01-01') }, 'label': '2060-2080', 'color': '#f3722c' },
        { 'slice': { 'time': slice('2080-01-01', '2101-01-01') }, 'label': '2080-2100', 'color': '#f94144' },
    ]


def ensemble():
    # unstructured mesh, only daily data
    #    'color': '#FF924C',
    #    'experiment_id': 'ssp585',
    #    'source_id': 'AWI-CM-1-1-MR',
    #    'variant_label': 'r1i1p1f1',
    # }, {
    # no siconc (has siconca)
    #    'color': '#9b2226',
    #    'experiment_id': 'ssp585',
    #    'source_id': 'GISS-E2-1-G',
    #    'variant_label': 'r1i1p5f1',
    #}, {
    # no siconc (has siconca)
    #    'color': '#bb3e03',
    #    'experiment_id': 'ssp585',
    #    'source_id': 'GISS-E2-2-G',
    #    'variant_label': 'r1i1p3f1',
    #}, {
    # no historical prsn!
    #    'color': '#ff924c',
    #    'experiment_id': 'ssp585',
    #    'source_id': 'CESM2-WACCM',
    #    'variant_label': 'r4i1p1f1',
    #}, {
    #    'experiment_id': 'ssp585',
    #    'source_id': 'CESM2',
    #   'variant_label': 'r4i1p1f1',
    #}, {
    # not included in keen et al. 2021, poor sea-ice representation
    #    'color': None,
    #    'experiment_id': 'ssp585',
    #    'source_id': 'CMCC-ESM2',
    #    'variant_label': 'r1i1p1f1',
    #}, {
    # #F94144 #F3722C #577590 #4267AC #565AA0 #6A4C93
    # green 8ac926
    return [
        {
            # No explicit lateral melt or frazil ice formation
            'color': '#f28c87',
            'experiment_id': 'ssp585',
            'si_collapse': False,
            'source_id': 'ACCESS-CM2',
            'variant_label': 'r1i1p1f1',
        }, {
            # missing: sipr, dynamics, frazil, lateral melt
            'color': '#ff595e',
            'experiment_id': 'ssp585',
            'si_collapse': True,
            'source_id': 'CanESM5',
            'variant_label': 'r1i1p2f1',
        }, {
            # missing: No explicit lateral melt
            'color': '#ffca3a',
            'experiment_id': 'ssp585',
            'si_collapse': False,
            'source_id': 'EC-Earth3',
            'variant_label': 'r4i1p1f1',
            'evspsbl': { 'grid_label': 'gr' },
            'evspsbl_siconc': { 'grid_label': 'gr' },
            'pr': { 'grid_label': 'gr' },
            'prnet': { 'grid_label': 'gr' },
            'pr_siconc': { 'grid_label': 'gr' },
            'prsn': { 'grid_label': 'gr' },
            'prsn_siconc': { 'grid_label': 'gr' },
            'prra': { 'grid_label': 'gr' },
            'prra_siconc': { 'grid_label': 'gr' },
            'tas': { 'grid_label': 'gr' },
            'tas_siconc': { 'grid_label': 'gr' }
        }, {
            'color': '#babb74',
            'experiment_id': 'ssp585',
            'si_collapse': True,
            'source_id': 'HadGEM3-GC31-MM',
            'variant_label': 'r1i1p1f3',
        }, {
            'color': '#8ab17d',
            'experiment_id': 'ssp585',
            'si_collapse': True,
            'source_id': 'IPSL-CM6A-LR',
            'variant_label': 'r1i1p1f1',
            'evspsbl': { 'grid_label': 'gr' },
            'evspsbl_siconc': { 'grid_label': 'gr' },
            'pr': { 'grid_label': 'gr' },
            'prnet': { 'grid_label': 'gr' },
            'pr_siconc': { 'grid_label': 'gr' },
            'prsn': { 'grid_label': 'gr' },
            'prsn_siconc': { 'grid_label': 'gr' },
            'prra': { 'grid_label': 'gr' },
            'prra_siconc': { 'grid_label': 'gr' },
            'tas': { 'grid_label': 'gr' },
            'tas_siconc': { 'grid_label': 'gr' }
        }, {
            'color': '#2a9d8f',
            'experiment_id': 'ssp585',
            'si_collapse': False,
            'source_id': 'MIROC6',
            'variant_label': 'r1i1p1f1',
        }, {
            'color': '#3185fc',
            'experiment_id': 'ssp585',
            'si_collapse': False,
            'source_id': 'MPI-ESM1-2-LR',
            'variant_label': 'r1i1p1f1',
        }, {
            'color': '#287271',
            'experiment_id': 'ssp585',
            'si_collapse': False,
            'source_id': 'MRI-ESM2-0',
            'variant_label': 'r1i1p1f1',
        }, {
            'color': '#6a4c93',
            'experiment_id': 'ssp585',
            'si_collapse': False,
            'source_id': 'NorESM2-LM',
            'variant_label': 'r1i1p1f1',
        }, {
            'areacello_variant_label': 'r1i1p1f2',
            'color': '#997b66',
            'experiment_id': 'ssp585',
            'si_collapse': True,
            'source_id': 'UKESM1-0-LL',
            'variant_label': 'r2i1p1f2'
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
        { 'values': [9,10,11,12,13,15], 'label': 'Higher Latitudes' },
        { 'values': [6,7,8], 'label': 'Lower Latitudes' },
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


def preprocess_temp(data, experiment, source_id, variant_label):
    # Convert K -> C
    return data - 273.15


def variables():
    return [
        {
            'component': 'SImon',
            'obs': [
                {
                    'color': '#002ea5',
                    'filename': 'HadISST_ice_processed.nc',
                    'source_id': 'HadISST1',
                    'variable_id': 'sic'
                },
                {
                    'filename': 'HadISST.2.2.0.0_sea_ice_concentration_processed.nc',
                    'color': '#7600a5',
                    'source_id': 'HadISST.2.2.0.0',
                    'variable_id': 'sic'
                }

            ],
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
            'component': 'SImon',
            'text': 'sea-ice melt pond concentration',
            'units': '%',
            'variable_id': 'simpconc',
            'weighting_method': 'mean',
            'weighting_process': lambda x: x
        },
        {
            'component': 'SImon',
            'text': 'sea-ice melt pond area',
            'units': 'km²',
            'variable_id': 'simpconc_area',
            'weighting_method': 'sum',
            # Convert m2 => km2 and % to frac
            'weighting_process': lambda x: x / (1000 * 1000 * 100)
        },
        {
            'component': 'SImon',
            'text': 'thickness of melt pond',
            'units': 'm',
            'variable_id': 'simpmass',
            'weighting_method': 'mean',
            'weighting_process': lambda x: x
        },
        {
            'component': 'SImon',
            'text': 'thickness of refrozen ice on melt pond',
            'units': 'm',
            'variable_id': 'simprefrozen',
            'weighting_method': 'mean',
            'weighting_process': lambda x: x
        },
        {
            'component': 'Amon',
            'obs': [
                {
                    'filename': 'era5_total_precipitation_1980-2020_processed.nc',
                    'color': '#002ea5',
                    'source_id': 'ERA5',
                    'variable_id': 'tp'
                }
            ],
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
            'text': 'net precipitation over sea-ice and ocean',
            'units': 'mm day⁻¹',
            'variable_id': 'prnet',
            'weighting_method': 'mean',
            'weighting_process': lambda x: x
        },
        {
            'component': 'Amon',
            'obs': [
                {
                    'filename': 'era5_snowfall_1980-2020_processed.nc',
                    'color': '#002ea5',
                    'source_id': 'ERA5',
                    'variable_id': 'sf'
                }
            ],
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
            'obs': [
                {
                    'filename': 'era5_2m_temperature_1980-2020_processed.nc',
                    'color': '#002ea5',
                    'source_id': 'ERA5',
                    'variable_id': 't2m'
                }
            ],
            'preprocess': preprocess_temp,
            'text': 'surface air temperature over sea-ice and ocean',
            'units': '°C',
            'variable_id': 'tas',
            'weighting_method': 'mean',
            'weighting_process': lambda x: x
        },
        {
            'component': 'Amon',
            'preprocess': preprocess_temp,
            'text': 'surface air temperature over sea-ice',
            'units': '°C',
            'variable_id': 'tas_siconc',
            'weighting_method': 'mean',
            'weighting_process': lambda x: x
        },
        {
            'component': 'Amon',
            'obs': [
                {
                    'filename': 'era5_evaporation_1980-2020_processed.nc',
                    'color': '#002ea5',
                    'source_id': 'ERA5',
                    'variable_id': 'e'
                }
            ],
            'preprocess': preprocess_evspsbl,
            'text': 'evaporation and sublimation over sea-ice and ocean',
            'units': 'mm day⁻¹',
            'variable_id': 'evspsbl',
            'weighting_method': 'mean',
            'weighting_process': lambda x: x
        },
         {
            'component': 'Amon',
            'preprocess': preprocess_evspsbl,
            'text': 'evaporation and sublimation over sea-ice',
            'units': 'mm day⁻¹',
            'variable_id': 'evspsbl_siconc',
            'weighting_method': 'mean',
            'weighting_process': lambda x: x
        },
        {
            'component': 'Omon',
            'obs': [
                {
                    'filename': 'era5_sea_surface_temperature_1980-2020_processed.nc',
                    'color': '#002ea5',
                    'source_id': 'ERA5',
                    'variable_id': 'sst'
                }
            ],
            'text': 'sea surface temperature',
            'units': '°C',
            'variable_id': 'tos',
            'weighting_method': 'mean',
            'weighting_process': lambda x: x
        },
        {
            'component': 'Omon',
            'text': 'sea surface temperature under sea-ice',
            'units': '°C',
            'variable_id': 'tos_siconc',
            'weighting_method': 'mean',
            'weighting_process': lambda x: x
        }
    ]
