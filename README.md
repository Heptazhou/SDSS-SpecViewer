# SDSS SpecViewer
authors: Dr. Jennifer Li (UIUC) and Meg Davis (UConn, <megan.c.davis@uconn.edu>), 2021

authors: Pat Hall, Zezhou Zhu, and Kevin Welch (YorkU, <phall@yorku.ca>, <zzz@my.yorku.ca>), 2023

This is a demo for a multi-epoch spectral viewer for SDSSV-BHM using plotly/dash (<https://dash.plotly.com/>). The ultimate goal is to build a web application that allows quick spectral visualization for SDSSV BHM data. The current version will access the data via url and it takes 1-2 seconds to load each spectra.

**Usage**: Please see the Getting Started section, below, before launching the tool. To launch the web app, you run the script `sdssv_spec_appREMOTE.py` as a regular python file. The web app will be at <http://127.0.0.1:8050/>, which you can open with any web browser.

---
## Getting Started

### Authentication

You **must** have the proper SDSS-V Proprietary Data username and password in the `authentication.txt` (created upon first run) to use this tool, the program will prompt you to input required authentication if the file does not exist yet. The code will immediately check the authentication upon start up.

### Dependencies
Please install the following Python packages to use this tool. The provided "dependencies.sh" shell script will pip install these for you, if you run it with: `./dependencies.sh`.
- dash
- plotly
- astropy
- requests
- numpy

Or better, if you are using Conda (e.g. Miniconda/Anaconda), you may run (within some [environment](https://conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html)):
```shell
conda install astropy dash numpy plotly requests
```

### Keeping up-to-date

The `dictionaries.txt` file is the backbone to this tool. By running the `update_dictionaries.py` file, it will look for spAll-lite-v6_1_0.fits on your local machine and update said dictionary file. The file provided here is up-to-date for BHM targets ***for GOOD fields ONLY*** as of 2023-05-30. Runtime was ~1 hour on a 2.6 GHz Intel Core i7 MacBook Pro.


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

