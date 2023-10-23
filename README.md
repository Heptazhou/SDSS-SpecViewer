# SDSS SpecViewer
authors: Dr. Jennifer Li (UIUC) and Meg Davis (UConn, <megan.c.davis@uconn.edu>), 2021 <br />
authors: Pat Hall, Zezhou Zhu, and Kevin Welch (YorkU, <phall@yorku.ca>, <zzz@my.yorku.ca>), 2023

This is a demo for a multi-epoch spectral viewer for SDSSV-BHM using [plotly/dash](https://dash.plotly.com/). The ultimate goal is to build a web application that allows quick spectral visualization for SDSSV BHM data. The current version will access the data via url and it takes 1-2 seconds to load each spectra.

**Usage**: Please see the Getting Started section, below, before launching the tool. To launch the web app, you run the script `sdssv_spec_appREMOTE.py` as a regular python file. The web app will be at <http://127.0.0.1:8050/>, which you can open with any web browser.

---
## Getting Started

### Authentication

You **must** have the proper SDSS-V Proprietary Data username and password in the `authentication.txt` (created upon first run) to use this tool, the program will prompt you to input required authentication if the file does not exist yet. The code will immediately check the authentication upon start up.

### Dependencies
Please install the following Python packages to use this tool.
- dash
- plotly
- astropy
- requests
- numpy

If you use [conda](https://conda.io/), you may run (preferably, within some [environment](https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html)):
```shell
conda install astropy dash numpy plotly requests
```

If you use [pip](https://pip.pypa.io/), you may run (preferably, within some [environment](https://packaging.python.org/en/latest/tutorials/installing-packages/#creating-and-using-virtual-environments)):
```shell
pip install astropy dash numpy plotly requests
```

### Keeping up-to-date

The `dictionaries.txt` file is the backbone to this tool. By running the `update_dictionaries.jl` file, it will look for a FITS file (e.g., `spAll-lite-v6_1_1.fits`) on your local machine and update said dictionary file. The file provided here is up-to-date for BHM targets ***for GOOD fields ONLY*** as of 2023-10-16.

Please install [Julia](https://julialang.org/) to run `update_dictionaries.jl`. Runtime with 1 thread was ~1min on AMD Zen 1, or ~40s on AMD Zen 3, FWIW. With latest Julia installed (v1.6.2+ is required; you could either install the [official binary](https://julialang.org/downloads/) or install it with your package manager of choice), you may run:
```shell
julia --startup-file=no -t auto update_dictionaries.jl
```
You can safely ignore `--startup-file` argument if you do not have a startup file. And with Julia v1.7+, I highly recommend setting environment variable `JULIA_NUM_THREADS=auto` instead of specifing `-t`, then simply:
```shell
julia update_dictionaries.jl
```


### User's guide
- To change the x-axis and/or y-axis range and keep it changed as you adjust the smoothing or redshift, use the Y-axis range and X-axis range buttons below the plot.
- You can also select the x-axis and/or y-axis range by clicking and dragging; HOWEVER, this method does not update the Y-axis range or X-axis range buttons and your selection will be reset if the smoothing or redshift is changed.
- Rest-frame wavelengths appear along the top of the plot and observed-frame wavelengths along the bottom of the plot.
- Emission-line labels appear above the top of the plot, and their wavelengths are shown with solid vertical lines. Absorption-line labels appear at the bottom of the plot, and their wavelengths are shown with dotted vertical lines. In both cases, the wavelength(s) of the line(s) associated with that label are shown when the cursor hovers over the label.


## Features to be added
- include previous spectra from SDSS I-IV, provide downloadable links to all data
- include quick links to other databases (Simbad, Ned, etc...)
- include source information summary (RA, Dec, z, source types...)
- search with RA/Dec for objects
- renormalization of spectra (based on specific wavelength or line)
- DONE smoothing of spectra
- show the residual spectra in greyscale (could add as a second figure)
- DONE optimize the loading speed
- add session history
- S/N selection slider bar
- Fix colors

