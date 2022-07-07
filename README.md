# cmip6-seaice-precipitation

Codebase for dissertation project which aims to investigate the effect of rainfall on sea-ice in the Arctic, using a subset of the CMIP6 ensemble under the ssp585 scenario.


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


### Local

- Follow instructions at [hannahwoodward/docker-jupyter-climate](https://github.com/hannahwoodward/docker-jupyter-climate) to install Docker desktop and pull the image
- Clone repo and cd inside
- Run `start.sh` to start the Docker container


## Data download & pre-processing

The following notebooks must be processed in this order before running any other notebooks:
- Run `preprocessing/remote-download.ipynb` to download and pre-process all variables
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
