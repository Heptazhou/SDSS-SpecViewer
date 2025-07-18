#	SDSS SpecViewer
[![CI status](https://github.com/Heptazhou/SDSS-SpecViewer/actions/workflows/CI.yml/badge.svg)](https://github.com/Heptazhou/SDSS-SpecViewer/actions/workflows/CI.yml)
[![codecov.io](https://codecov.io/gh/Heptazhou/SDSS-SpecViewer/branch/master/graph/badge.svg)](https://app.codecov.io/gh/Heptazhou/SDSS-SpecViewer)

authors: Dr. Jennifer Li (UIUC) and Meg Davis (UConn, <megan.c.davis@uconn.edu>), 2021<br />
authors: Pat Hall and Zezhou Zhu (YorkU, <phall@yorku.ca>, <zzz@my.yorku.ca>), 2023-2025

This is a multi-epoch spectral viewer for SDSSV-BHM using [plotly/dash](https://dash.plotly.com/). The goal is to build a web application that allows quick spectral visualization for SDSSV BHM data. The current version will access the data via url and it takes a few seconds to load the spectra.

**Usage**: Please see the Getting Started section, below, before launching the tool. To launch the web app, you run the script `sdssv_spec_appREMOTE.py` as a regular python file. The web app will be at <http://127.0.0.1:8050/>, which you can open with any web browser.

*****
##	Getting Started

###	Authentication
You **must** have the proper SDSS-V Proprietary Data username and password in the `authentication.txt` (created upon first run) to use this tool, the program will prompt you to input required authentication if the file does not exist yet. The code will immediately check the authentication upon start up.

###	Installation
Cloning this repository using Github Desktop is the best way to install this tool. Doing so will allow you to easily keep up to date with any updates.

###	Dependencies
Please install the following Python packages to use this tool, with the minimum required versions shown as such. See also the file [`pixi.toml`](pixi.toml) for a list of recommended package versions with which SpecViewer is guaranteed to work.
+	astropy-base >= 4.3.1
+	dash         >= 2.13.0
+	numpy        >= 1.21.4
+	plotly       >= 5.0.0
+	pyzstd       >= 0.15.9
+	requests     >= 2.23.0
<!-- ^ keep consistent with pyproject.toml -->

> [!NOTE]
> Python v3.10 or higher is required ([status of Python versions](https://devguide.python.org/versions/)).

*****
If you have [pixi](https://pixi.sh/latest/), you may simply do
```shell
pixi run main
```
to run the tool. Otherwise, see the following.

*****
If you are using [conda](https://docs.conda.io/) or [mamba](https://mamba.readthedocs.io/), you may run (preferably, within a separate [environment](https://docs.conda.io/projects/conda/en/latest/user-guide/getting-started.html#creating-environments)):
```shell
conda install astropy-base dash numpy plotly pyzstd requests types-requests
```
Also, to update:
```shell
conda update astropy-base dash numpy plotly pyzstd requests types-requests
```

*****
If you are using [pip](https://pip.pypa.io/), you may run (preferably, within a separate [environment](https://packaging.python.org/en/latest/tutorials/installing-packages/#creating-virtual-environments)):
```shell
pip install astropy dash numpy plotly pyzstd requests types-requests
```
Also, to update:
```shell
pip install -U astropy dash numpy plotly pyzstd requests types-requests
```

*****
Then, run this to start the tool:
```shell
python sdssv_spec_appREMOTE.py
```


###	Keeping up-to-date

The bhm.json.zst compressed dictionary file is the backbone to this tool. (It can be uncompressed using unzstd if desired.) By running the `update_dictionaries.jl` file, it will look for FITS file(s) (e.g., `spAll-lite-master.fits`; note: `v6_1_1` or higher required) on your machine and update said dictionary file. Runtime with 1 input file was ~50s on AMD Zen 1, or ~30s on AMD Zen 3, FWIW. The compressed dictionary file is not included in this distribution to avoid issues with proprietary SDSS data, but will be generated when the program is run and SDSS authentication is provided.

To update bhm.json.zst, install the latest version of [Julia](https://julialang.org/), and set environment variable `JULIA_NUM_THREADS=auto,auto` so you can omit the `-t auto` argument ([read more](https://docs.julialang.org/en/v1/manual/multi-threading/)).

Then, having the FITS files or archive files (each archive should contain only one FITS file, and would be used only if the filename to be extracted does not exist) accessible in the current directory (either hard copies or via symbolic links), run:
```shell
julia -t auto update_dictionaries.jl
```
Alternatively, provide paths as arguments:
```shell
julia -t auto update_dictionaries.jl <path/to/file>...
```
PS: The filename(s) shall match the pattern `/\bspall\b.*\.fits(\.tmp)?$/i` and not match `/\ballepoch\b/i`.


###	User's guide
+	To change the x-axis and/or y-axis range and keep it changed as you adjust the smoothing or redshift, use the Y-axis range and X-axis range buttons below the plot.
+	You can also select the x-axis and/or y-axis range by clicking and dragging; HOWEVER, this method does not update the Y-axis range or X-axis range buttons and your selection will be reset if the smoothing or redshift is changed.
+	Rest-frame wavelengths appear along the top of the plot and observed-frame wavelengths along the bottom of the plot.
+	Emission-line labels appear above the top of the plot, and their wavelengths are shown with solid vertical lines. Absorption-line labels appear at the bottom of the plot, and their wavelengths are shown with dotted vertical lines. In both cases, the wavelength(s) of the line(s) associated with that label are shown when the cursor hovers over the label.


##	Wish list of features to be added
+	renormalization of spectra/spectrum (based on specific wavelength or line, or input value)

