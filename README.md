# cmip6-seaice-precipitation

Codebase for dissertation project which aims to investigate the effect of rainfall on sea-ice in the Arctic, using a subset of the CMIP6 ensemble under the ssp585 scenario.

## Figures

1. NSIDC regions (regions.ipynb TODO)
2. Sea ice area min/max & seasonal trends (ensemble-siconc.ipynb [8])
3. Sea ice concentration spatial (ensemble-siconc.ipynb [14, 15])
4. Sea ice thickness min/max & spatial (ensemble-sithick.ipynb [8, 12, 13])
5. Sea ice snow thickness min/max (ensemble-sisnthick.ipynb [7])
6. Surface air and sea temperature, annual mean & seasonal trends (ensemble-trends-tas-tos.ipynb [4])
7. Precipitation, evaporation, snowfall, and rainfall, annual mean & seasonal trends (ensemble-trends-pr-evspsbl.ipynb [4], ensemble-trends-prra-prsn.ipynb [4])
8. Evaporation/precipitation ratio, regional seasonal trends (ensemble-evspsbl.ipynb [9])
9. Spatial correlation of evaporation and sea ice concentration (analysis/analysis-spatial-siconc.ipynb [9])
10. Evaporation/precipitation ratio, 2080-2100 average seasonal cycle (ensemble-regional-trends.ipynb [13])
11. Inter-model correlation of sea ice area and evaporation/precipitation ratio for 2080-2100 average seasonal cycle ()
12. Contribution of evaporation from sea ice loss to total evaporation and precipitation ()


## Stats

- Sea ice free (ensemble-siconc.ipynb [9])
- Sea ice thickness change (ensemble-sithick.ipynb [7])
- Sea ice snow thickness change (ensemble-sithick.ipynb [6])
- Surface air and sea temperature (ensemble-trends-tas-tos.ipynb [5])
- Precipitation & evaporation changes (ensemble-trends-pr-evspsbl.ipynb [5])
- Rainfall & snowfall changes (ensemble-trends-prra-prsn.ipynb [5, 6])
- Spatial correlation of evaporation and sea ice concentration (analysis/analysis-spatial-siconc.ipynb [10, 11])


## Setup

### JASMIN Notebook service

- Log in to JASMIN notebook service
- Create new file named `climate.yml` in root in JASMIN and paste environment config from [hannahwoodward/docker-jupyter-climate](https://github.com/hannahwoodward/docker-jupyter-climate/blob/main/environment.yml)
- Install and activate climate conda environment (ref: https://github.com/cedadev/ceda-notebooks/blob/master/notebooks/docs/add_conda_envs.ipynb)

```
!conda env create -f climate.yml --quiet
!source activate climate
!conda run -n climate python -m ipykernel install --user --name climate
```

- Clone repo:

```
!git clone https://github.com/hannahwoodward/cmip6-seaice-precipitation.git
```

- [Follow instructions to create an account and generate API key for cdsapi](https://cds.climate.copernicus.eu/api-how-to#install-the-cds-api-key). This is used for downloading ERA5 reanalysis.


### Local

- Follow instructions at [hannahwoodward/docker-jupyter-climate](https://github.com/hannahwoodward/docker-jupyter-climate) to install Docker desktop and pull the image
- Clone repo and cd inside
- Run `start.sh` to start the Docker container


## Data download & pre-processing

The following notebooks must be processed in this order before running any other notebooks:
- Run `preprocessing/remote-download.ipynb` to download and pre-process all variables
- Run `preprocessing/remote-download-obs.ipynb` to download and pre-process all observational/reanalysis data
- Run `preprocessing/create-prra.ipynb` to create `prra` variable
- Run `preprocessing/create-prnet.ipynb` to create `prra` variable
- Run `preprocessing/create-vars-siconc.ipynb` to create variables masked to `siconc > 0`
- Run `preprocessing/create-vars-siconc-weighted.ipynb` to create variables multiplied by `siconc`
- Run `preprocessing/create-time-series-regional.ipynb` to create time series for each [NSIDC region](https://github.com/hannahwoodward/cmip6-seaice-precipitation/blob/5b977709929f503c07c84979dbf1dbfd1b8186f7/libs/vars.py#L96)


## Useful links

- [CMIP6 data search](https://esgf-node.llnl.gov/search/cmip6/)
- [CEDA CMIP6 catalogue](https://data.ceda.ac.uk/badc/cmip6)
- [Ensemble members](https://github.com/hannahwoodward/cmip6-seaice-precipitation/blob/5b977709929f503c07c84979dbf1dbfd1b8186f7/libs/vars.py#L26)
- [NSIDC regions](https://github.com/hannahwoodward/cmip6-seaice-precipitation/blob/5b977709929f503c07c84979dbf1dbfd1b8186f7/libs/vars.py#L96)
- [Variables](https://github.com/hannahwoodward/cmip6-seaice-precipitation/blob/5b977709929f503c07c84979dbf1dbfd1b8186f7/libs/vars.py#L140)
