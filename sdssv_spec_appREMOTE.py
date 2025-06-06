### SpecViewer for Python v3.10+

"""
Excelsior!
"""

import json
import math
import sys
from base64 import b64decode
from io import BytesIO
from pathlib import Path
from re import IGNORECASE, fullmatch
from tempfile import TemporaryDirectory
from traceback import print_exc

import dash
import numpy
import requests
from astropy.convolution import Box1DKernel, convolve  # type: ignore
from astropy.io import fits as FITS  # type: ignore
from astropy.io.fits import BinTableHDU, FITS_rec, HDUList  # type: ignore
from dash import dcc, html
from dash.dependencies import Input, Output, State
from numpy import mean, median, sqrt, std
from numpy.typing import NDArray
from plotly.graph_objects import Figure, Scatter
from requests.exceptions import HTTPError

from util import SDSSV_buildURL, identity, object_links

# https://docs.python.org/3/library/tomllib.html
# https://peps.python.org/pep-0680/
# if sys.version_info < (3, 11): import tomli as tomllib
# if sys.version_info > (3, 11): import tomllib

###
### input the data directory path
###

# dictionaries = json.load(open("dictionaries.txt"))
authentication = "authentication.txt"
# programs: dict[str, list[int]] = dictionaries[0]
# fieldIDs: dict[str, list[int]] = dictionaries[1]
# catalogs: dict[str, list[list | int]] = dictionaries[2]

bhm_meta = json.load(open("data/bhm.meta.json"))
bhm_data = json.load(open("data/bhm.json"))

programs: dict[str, list[int]] = bhm_data["prg"]
fieldIDs: dict[str, list[int]] = bhm_data["fld"]
sdss_IDs: dict[str, list[int]] = bhm_data["sid"]
catalogs: dict[str, list[int]] = bhm_data["cat"]

# for testing
# print(programs)
# print("those were programs")
# print(fieldIDs)
# print("those were fieldIDs")
# print(catalogs)
# print("those were catalogs")
# print("catalog*5", catalogs["27021598109009995"])
# print("field17049", fieldIDs["17049"])

# the redshift and stepping to easily adjust redshift using arrow keys or mouse wheel, disabled by default
# because unfortunately, setting a numeric `step` attribute for an `input` element also means the value of
# it must adhere such granularity (specified by the HTML specification, no way to bypass this behavior),
# making an arbitrary input to be invalid, but we always want to accept redshift of any precision
redshift_default = 0
redshift = None
stepping = None

# global dict to save results of `SDSSV_fetch` and `fetch_catID`
cache: dict[tuple, tuple] = {}

# default y-axis range of spectrum plots
y_max_default = 20
y_min_default = 0

# smoothing along x-axis, disabled by default (one means no smoothing)
# we need an upper limit since a very large value freezes the program
smooth_default = 1
smooth_max = 1000

### css files
external_stylesheets = [ "https://codepen.io/chriddyp/pen/bWLwgP.css",
                         "https://maxcdn.bootstrapcdn.com/bootstrap/3.4.1/css/bootstrap.min.css",
                         "https://aladin.u-strasbg.fr/AladinLite/api/v2/latest/aladin.min.css",
                         "https://use.fontawesome.com/releases/v5.15.4/css/all.css",
                         "https://use.fontawesome.com/releases/v5.15.4/css/v4-shims.css", ]

###
### Any necessary functions
###

def SDSSV_fetch(username: str, password: str, field: int | str, mjd: int, obj: int | str, branch="") \
	-> tuple[FITS_rec, NDArray, NDArray, NDArray]:
	"""
	Fetch spectral data for a SDSS-RM object on a
	specific field on a specific MJD, using the user
	supplied authentication.
	"""
	if type(field) == str:
		if fullmatch(r"\d+p", field):
			field = field.rstrip("p")
			branch = branch or "v6_0_4"
		if fullmatch(r"\d+", field):
			field = int(field)
	if type(field) == int:
		# PBH: field numbers 1 to 3509 (and 8015 & 8033) indicate SDSS-I/II data, but 00000 reserved for eFEDS
		match field:
			case n if n <= 0:
				pass
			case n if n <= 3509 or n in (8015, 8033): # SDSS-I/II
				branch = branch or "legacy" # SDSS Legacy & SEGUE programs
			case n if n < 15000: # SDSS-III/IV
				branch = branch or "v5_13_2"
	field, obj = str(field), str(obj) # ensure type

	# Program will try all the branches below in the order listed
	if not branch or branch == "legacy":
		for v in ("26", "104", "103") if branch == "legacy" \
			else ("master", "v6_2_1", "v6_2_0", "v6_1_3", "v6_1_0"):
			try: return SDSSV_fetch(username, password, field, mjd, obj, v)
			except HTTPError: pass
			except Exception: print_exc()
		raise HTTPError(f"[SDSSV_fetch] {(field, mjd, obj)}")
	if not (field and mjd and obj):
		raise HTTPError(f"[SDSSV_fetch] {(field, mjd, obj, branch)}")
	if (field, mjd, obj, branch) in cache:
		return cache[(field, mjd, obj, branch)]

	url = SDSSV_buildURL(field, mjd, obj, branch)
	# print(url)

	rv = requests.get(url, auth=(username, password) if "/sdsswork/" in url else None)
	rv.raise_for_status()
	print(rv.status_code, url)
	numpy.seterr(divide="ignore") # Python does not comply with IEEE 754 :(
	fits: HDUList = FITS.open(BytesIO(rv.content))
	hdu2: BinTableHDU = fits["COADD"] if "COADD" in fits else fits[1]
	hdu3: BinTableHDU = fits["SPALL"] if "SPALL" in fits else fits[2]
	meta: FITS_rec = hdu3.data
	wave: NDArray = hdu2.data["LOGLAM"] # lg(λ)
	flux: NDArray = hdu2.data["FLUX"]   # f_λ
	errs: NDArray = hdu2.data["IVAR"]   # τ = σ⁻²
	wave = 10**wave                     # λ
	errs = 1 / sqrt(errs)               # σ
	# print(f"meta: {type(meta)} = {str(meta)[:100]}")
	# print(f"wave: {type(wave)} = {str(wave)[:100]}")
	# print(f"flux: {type(flux)} = {str(flux)[:100]}")
	r = meta, wave, flux, errs
	cache[(field, mjd, obj, branch)] = r
	return r

def SDSSV_fetch_allepoch(username: str, password: str, mjd: int, obj: int | str):
	"""
	Fetch all epoch spectral data for a given MJD and object using authentication.
	"""
	if mjd >= 59187:
		for x in ["allepoch_apo"] if mjd < 60000 else ["allepoch_apo", "allepoch_lco"]:
			try: return SDSSV_fetch(username, password, x, mjd, obj, branch="v6_2_0")
			except: pass
		for x in ["allepoch"    ] if mjd < 60000 else ["allepoch", "allepoch_lco"    ]:
			try: return SDSSV_fetch(username, password, x, mjd, obj, branch="v6_1_3")
			except: pass
	if mjd >= 59164:
		for x in ["allepoch"    ]:
			try: return SDSSV_fetch(username, password, x, mjd, obj, branch="v6_1_1")
			except: pass
	field = "allepoch*"
	raise HTTPError(f"[SDSSV_fetch] {(field, mjd, obj)}")

def fetch_catID(field: int | str, catID: int | str, extra="", match_sdss_id=True) \
	-> tuple[dict[str, int | float], list[str], list[NDArray], list[NDArray], list[NDArray]]:
	if not (extra or catID): # consider as incomplete user input
		raise Exception()    # so abort quietly
	if not (extra or catID and field):
		raise Exception((field, catID, extra))
	field = str(field).replace(" ", "") if not match_sdss_id else "all"
	catID = str(catID).replace(" ", "")
	extra = str(extra).replace(" ", "")
	if (field, catID, extra, match_sdss_id) in cache:
		return cache[(field, catID, extra, match_sdss_id)]

	name, wave, flux, errs = list[str](), list[NDArray](), list[NDArray](), list[NDArray]()

	cats: list[int] = [int(catID)]
	meta: dict[str, list] = {
		"DEC": [],
		"RA": [],
		"RCHI2": [],
		"Z": [],
		"ZWARNING": [],
	}
	if (sdss_id := catalogs.get(catID, [0])[0]) > 0 and match_sdss_id:
		for cat in sdss_IDs.get(f"{sdss_id}", []):
			if not cat in cats: cats.append(cat)
		cats = sorted(cats)
	# print(f"[sdss_id] {catID} => {sdss_id} => {cats} # {match_sdss_id}")

	for x in extra.split(","):
		x, ver = [*x.split("@", 1), ""][:2]
		if not fullmatch(r"\d+p?-\d+-[^-](.*[^-])?", x): continue
		fid, mjd, obj = x.split("-", 2)
		mjd = int(mjd)
		try:
			dat = SDSSV_fetch(username, password, fid, mjd, obj, ver)
		except Exception as e:
			if str(e): print(e) if isinstance(e, HTTPError) else print_exc()
			continue
		mjd_final = str((dat[0]["MJD_FINAL"] if hasattr(dat[0], "MJD_FINAL") else dat[0]["MJD"])[0])
		name.append(mjd_final)
		wave.append(dat[1])
		flux.append(dat[2])
		errs.append(dat[3])
	if fullmatch(r"\d+p?-\d+", field):
		obj, ver = [*catID.split("@", 1), ""][:2]
		fid, mjd = field.split("-", 1)
		mjd = int(mjd)
		try:
			dat = SDSSV_fetch(username, password, fid, mjd, obj, ver)
		except Exception as e:
			if str(e): print(e) if isinstance(e, HTTPError) else print_exc()
			raise # re-raise
		# print(f"{dat[0].columns=}")
		meta_DEC = dat[0]["DEC"][0] if hasattr(dat[0], "DEC") else None
		meta_R_A = dat[0]["RA" ][0] if hasattr(dat[0], "RA" ) else None
		meta["DEC"     ].append(dat[0]["DECCAT"  ][0] if hasattr(dat[0], "DECCAT") else meta_DEC)
		meta["RA"      ].append(dat[0]["RACAT"   ][0] if hasattr(dat[0], "RACAT" ) else meta_R_A)
		meta["RCHI2"   ].append(dat[0]["RCHI2"   ][0])
		meta["Z"       ].append(dat[0]["Z"       ][0])
		meta["ZWARNING"].append(dat[0]["ZWARNING"][0])
		mjd_final = str((dat[0]["MJD_FINAL"] if hasattr(dat[0], "MJD_FINAL") else dat[0]["MJD"])[0])
		mjd_list = [mjd]
		name.append(mjd_final)
		wave.append(dat[1])
		flux.append(dat[2])
		errs.append(dat[3])
	else:
		mjd_list = []
		for cat in cats:
			for fieldmjd in catalogs.get(f"{cat}", [0])[1:]: # {13'FIELD,5'MJD}
				fid, mjd = divmod(abs(fieldmjd), 10**5)
				if field != "all" and int(field) != fid: continue
				dat = SDSSV_fetch(username, password, fid, mjd, cat)
				meta_DEC = dat[0]["DEC"][0] if hasattr(dat[0], "DEC") else None
				meta_R_A = dat[0]["RA" ][0] if hasattr(dat[0], "RA" ) else None
				meta["DEC"     ].append(dat[0]["DECCAT"  ][0] if hasattr(dat[0], "DECCAT") else meta_DEC)
				meta["RA"      ].append(dat[0]["RACAT"   ][0] if hasattr(dat[0], "RACAT" ) else meta_R_A)
				meta["RCHI2"   ].append(dat[0]["RCHI2"   ][0])
				meta["Z"       ].append(dat[0]["Z"       ][0])
				meta["ZWARNING"].append(dat[0]["ZWARNING"][0])
				mjd_final = str((dat[0]["MJD_FINAL"] if hasattr(dat[0], "MJD_FINAL") else dat[0]["MJD"])[0])
				name.append(mjd_final)
				wave.append(dat[1])
				flux.append(dat[2])
				errs.append(dat[3])
				if mjd not in mjd_list: mjd_list.append(mjd)
		mjd_list.sort(reverse=True)
	# print(mjd_list)

	meta["DEC"     ] = meta["DEC"     ][-1]
	meta["RA"      ] = meta["RA"      ][-1]
	meta["RCHI2"   ] = meta["RCHI2"   ][-1]
	meta["Z"       ] = meta["Z"       ][-1]
	meta["ZWARNING"] = meta["ZWARNING"][-1]

	# allplate
	for cat in cats:
		for mjd in (x for x in mjd_list if x <= 59392):
			try:
				dat = SDSSV_fetch_allepoch(username, password, mjd, cat)
			except Exception as e:
				# if str(e): print(e) if isinstance(e, HTTPError) else print_exc()
				continue
			name.append(f"allplate-{mjd}")
			wave.append(dat[1])
			flux.append(dat[2])
			errs.append(dat[3])
			break
	# allFPS
	for cat in cats:
		for mjd in (x for x in mjd_list if x >= 59393):
			try:
				dat = SDSSV_fetch_allepoch(username, password, mjd, cat)
			except Exception as e:
				# if str(e): print(e) if isinstance(e, HTTPError) else print_exc()
				continue
			name.append(f"allFPS-{mjd}")
			wave.append(dat[1])
			flux.append(dat[2])
			errs.append(dat[3])
			break
	if not (meta and name and wave and flux):
		raise HTTPError(f"[fetch_catID] {(field, catID, extra)}")
	r = meta, name, wave, flux, errs
	cache[(field, catID, extra, match_sdss_id)] = r
	return r

###
### Authentication
###
try:
	print("Reading authentication file.")
	with open(authentication, "r", newline="") as io:
		lines = io.readlines()
		username = lines[0].strip()
		password = lines[1].strip()
except: # any error from above will fall through to here.
	print("authentication.txt broken or not exist. Please enter authentication.")
	username = input("Enter SDSS-V username: ").strip()
	password = input("Enter SDSS-V password: ").strip()
	sys.stdout.write("\r\x1bc\r") # "\ec"
	sys.stdout.flush()
finally:
	with open(authentication, "w", newline="") as io:
		io.write(f"{username}\n{password}\n")

try:
	print("Verifying authentication...")
	# fetch_test = SDSSV_fetch(username, password, 15173, 59281, 4350951054)
	# fetch_test = SDSSV_fetch(username, password, 112359, 60086, 27021600949438682)
	fetch_test = SDSSV_fetch(username, password, 101126, 60477, 63050394846126565)
	# url = SDSSV_buildURL("102236", "60477", "63050394846126565", "")
	# print(url)
	print("Verification succeeded.")
	print("Try loading http://127.0.0.1:8050/?<field>-<mjd>-<catid>")
	print("         or http://127.0.0.1:8050/?<field>-<mjd>-<catid>&prev=<plate>-<mjd>-<fiber>@<branch>")
	print("       e.g. http://127.0.0.1:8050/?101126-60477-63050394846126565")
	print("         or http://127.0.0.1:8050/?104623-60251-63050395075696130&prev=7670-57328-0918#m=5&x=3565,10350&y=0,18&z=2.66")
	print("Change any setting after loading to reset redshift from z=0.")
except:
	print("Verification failed.")
	print("Please make sure you have internet access and/or fix authentication.txt.")
	print("You may either edit the file to fix it, or simply delete it and rerun this program.")
	# print("Contact Meg (megan.c.davis@uconn.edu) if the issue persists.")
	exit(1)



### spectral lines to label in plot
# https://classic.sdss.org/dr6/algorithms/linestable.html
# https://github.com/desihub/desisim/blob/main/py/desisim/data/forbidden_lines.ecsv
# https://github.com/desihub/desisim/blob/main/py/desisim/data/recombination_lines.ecsv
# https://github.com/desihub/desisim/blob/main/py/desisim/lya_spectra.py
# https://github.com/sdss/idlspec2d/blob/master/etc/emlines.par
# https://physics.nist.gov/PhysRefData/Handbook/Tables/irontable2.htm
# the first column means whether to show this line or not by default
# the second column is the wavelength, which must be unique
spec_line_emi = numpy.asarray([
	# [1, 7753.1900, "[Ar III]"],
	# [1, 7137.7700, "[Ar III]"],
	[1, 6564.6130, "H α"     ],
	# [0, 6365.5350, "[O I]"   ],
	# [0, 6302.0460, "[O I]"   ],
	[0, 5877.2990, "He I"    ],
	# [0, 5577.3390, "[O I]"   ],
	# [0, 5411.5200, "He II"   ],
	[1, 5008.2390, "[O III]" ],
	[1, 4960.2950, "[O III]" ],
	[1, 4862.6830, "H β"     ],
	[0, 4685.6800, "He II"   ],
	[0, 4363.2090, "[O III]" ],
	[1, 4341.6840, "H γ"     ],
	[1, 4102.8920, "H δ"     ],
	# [0, 3971.1950, "H ε"     ],
	[0, 3968.5800, "[Ne III]"],
	# [0, 3890.1510, "H ζ"     ],
	[0, 3889.7520, "He I"    ],
	[0, 3869.8500, "[Ne III]"],
	# [0, 3850.8100, "Fe I"    ], # 3886.2822 3859.9114 3820.4253
	# [0, 3739.3497, "Fe I"    ], # 3758.2329 3749.4854 3748.2622 3745.5613 3737.1316 3734.8638 3719.9348
	[1, 3728.4830, "[O II]"  ], # 3729.8740 3727.0920
	[0, 3426.8400, "[Ne V]"  ],
	[0, 3346.8200, "[Ne V]"  ],
	# [0, 3524.9583, "Fe I"    ], # 3581.1931 3440.606
	# [0, 3524.9583, "Fe I"    ], # 3581.1931 3440.606
	[1, 2799.9410, "Mg II"   ], # 2803.5300 2796.3520
	[0, 2748.7814, "Fe II"   ], # 2755.7365 2749.3216 2739.5474
	[0, 2631.8295, "Fe II"   ], # 2611.8736 2607.0871 2599.3956 2598.3692 2585.8758 2493.2637
	# [0, 2492.2473, "Fe I"    ], # 2522.8494 2490.6443 2488.1426 2483.2708
	[0, 2414.0421, "Fe II"   ], # 2404.8858 2395.6254 2382.0376 2343.4951
	[1, 2326.0000, "C II"    ],
	[1, 1908.7340, "C III]"  ],
	[0, 1786.7520, "Fe II"   ],
	[0, 1750.4600, "N III]"  ],
	[0, 1640.4200, "He II"   ],
	[1, 1549.4800, "C IV"    ],
	[0, 1486.4960, "N IV]"   ],
	[1, 1396.7500, "Si IV"   ],
	[0, 1303.4900, "O I"     ],
	[1, 1240.8100, "N V"     ],
	[1, 1215.6710, "Ly α"    ],
	# [0, 1123.0000, "P V"     ],
	[1, 1034.0000, "O VI"    ],
	[1, 1025.7220, "Ly β"    ],
])
# custom absorption line list for quasars
# the second column is the multiplicity of the line, and gives the number of lines that will share a single label
# the third column is the wavelength list, in which the first one must be unique
spec_line_abs = numpy.asarray([
	[1, 2, "5897.5581 5891.5833          ", "Na I"       ],
	[1, 2, "3969.5910 3934.7770          ", "Ca II"      ],
	[0, 1, "2852.9642                    ", "Mg I"       ],
	[1, 2, "2803.5324 2796.3511          ", "Mg II"      ],
	[0, 2, "2600.1725 2586.6496          ", "Fe II UV1"  ],
	[0, 3, "2382.7642 2374.4603 2344.2130", "Fe II UV2+3"],
	[0, 3, "2062.2110 2068.9040 2079.6520", "Fe III UV48"],
	[0, 3, "1926.3040 1914.0560 1895.4560", "Fe III UV34"],
	[1, 2, "1862.7911 1854.7183          ", "Al III"     ],
	[0, 1, "1670.7886                    ", "Al II"      ],
	[0, 1, "1608.4511                    ", "Fe II 1608" ],
	[1, 2, "1550.7785 1548.2049          ", "C IV"       ],
	[0, 1, "1526.7070                    ", "Si II 1526" ],
	[1, 2, "1402.7729 1393.7602          ", "Si IV"      ],
	[1, 1, "1334.5323                    ", "C II"       ],
	[0, 1, "1304.3702                    ", "Si II 1304" ],
	[0, 1, "1260.4221                    ", "Si II 1260" ],
	[1, 2, "1242.8040 1238.8210          ", "N V"        ],
	[1, 1, "1215.6701                    ", "Ly α"       ],
	[0, 2, "1128.0080 1117.9770          ", "P V"        ],
	[1, 2, "1037.6155 1031.9265          ", "O VI"       ],
	[1, 1, "1025.7223                    ", "Ly β"       ],
	[0, 1, "0972.5368                    ", "Ly γ"       ],
	[0, 1, "0949.7431                    ", "Ly δ"       ],
	[0, 1, "0937.8035                    ", "Ly ε"       ],
	[1, 1, "0911.7600                    ", "Lyman limit"],
])

# print(spec_line_emi[numpy.bool_(numpy.int_(spec_line_emi[:, 0])), 2].tolist())
# print(spec_line_abs[numpy.bool_(numpy.int_(spec_line_abs[:, 0])), 3].tolist())

### wavelength plotting range
wave_max = 10500.
wave_min = 3500.
# x_max & x_min are only reset to wave_max & wave_min for new objects
x_max = wave_max
x_min = wave_min

### starting the dash app
app = dash.Dash(__name__, external_stylesheets=external_stylesheets,
                title="SpecViewer", update_title="Loading...")

### get object info
### organize by program, fieldid, catalogid
# programname = ["COSMOS"]
# programname = ["AQMES-Medium", "AQMES-Wide", "AQMES-Bonus", "bhm_aqmes"]
# programname = ["SDSS-RM", "XMM-LSS", "COSMOS", "AQMES-Medium", "AQMES-Wide"] # , "eFEDS1", "eFEDS2"]



###
### the webpage layout
###

# see https://getbootstrap.com/docs/3.4/css/#grid
app.layout = html.Div(className="container-fluid", style={"width": "90%"}, children=[

	# https://dash.plotly.com/dash-core-components/location
	dcc.Location(id="window_location", refresh=False),

	# https://dash.plotly.com/dash-core-components/store
	dcc.Store(id="dash-user-upload", storage_type="session"),

	html.Div(className="row", children=[

		html.Div(className="col-lg-6 col-sm-8 col-xs-12", children=[
			html.H2("SDSSV-BHM Spectra Viewer (remote version)"),
		]),

		html.Div(className="col-lg-6 col-sm-4 col-xs-12", children=[
			dcc.Checklist(id="extra_func_list", options={
				"z": "pipeline redshift",
				"p": "match program",
				"s": "match sdss_id",
				"l": "log10 x-axis",
				"e": "show error (σ)",
				"u": "file uploader",
			},
				value=["z", "p", "s"], inline=True, persistence=True, persistence_type="local",
				style={"marginTop": "20px", "display": "flex", "flexFlow": "wrap"},
				inputStyle={"marginRight": "5px"},
				labelStyle={"width": "180px", "whiteSpace": "nowrap"},
			),

			html.Div(dcc.Upload(html.Div([
				html.Br(), html.H4("Drag and drop / select file(s)"), html.Br(),
			], style={"margin": "0 20px", "textAlign": "center"}),
				id="file_ul", multiple=True,
			), id="file_ul_div", hidden=True, style={
				"margin": "20px 0", "width": "100%",
				"border": "1px dashed", "borderRadius": "5px"}),
		]),
	]),

	html.Div(className="row", children=[
		html.Div(className="col-lg-8 col-xs-12", style={"padding": "0"}, children=[

			## dropdown menu for program/fieldid/catalogid
			html.Div(className="col-lg-3 col-md-3 col-sm-4 col-xs-6", children=[
				html.Label(
					html.H4("Program"),
				),
				dcc.Dropdown(
					id="program_dropdown",
					options=[
						{"label": i, "value": i} for i in [*programs.keys(), "(other)"]],
					placeholder="Program",
				)]),

			## setting an empty value beforehand for next four fields is to suppress the warning from React.js

			## Field ID input (w/ MJD)
			html.Div(className="col-lg-3 col-md-3 col-sm-4 col-xs-6", children=[
				html.Label(
					html.H4("Field & MJD"),
				),
				dcc.Input(
					id="fieldid_input", type="text",
					placeholder="FieldID-MJD", value="", style={"height": "36px", "width": "100%"},
				)], id="fieldid_input_div", hidden=True),

			## Field ID dropdown
			html.Div(className="col-lg-3 col-md-3 col-sm-4 col-xs-6", children=[
				html.Label(
					html.H4("Field ID"),
				),
				dcc.Dropdown(
					id="fieldid_dropdown",
					placeholder="FieldID", value="",
				)], id="fieldid_dropdown_div", hidden=False),

			## catalog ID input
			html.Div(className="col-lg-6 col-md-6 col-sm-8 col-xs-12", children=[
				html.Label(
					html.H4("Catalog ID"),
				),
				dcc.Input(
					id="catalogid_input", type="text",
					placeholder="CatalogID", value="", style={"height": "36px", "width": "100%"},
				)], id="catalogid_input_div", hidden=True),

			## catalog ID dropdown
			html.Div(className="col-lg-6 col-md-6 col-sm-8 col-xs-12", children=[
				html.Label(
					html.H4("Catalog ID"),
				),
				dcc.Dropdown(
					id="catalogid_dropdown",
					placeholder="CatalogID", value="",
				)], id="catalogid_dropdown_div", hidden=False),

			## extra object(s) list input (hidden, but can be used directly otherwise)
			html.Div(className="col-xs-12", title="comma-seperated list", children=[
				html.Label(
					html.H4("Extra Object(s)"),
				),
				dcc.Input(
					id="extra_obj_input", type="text", value="", style={"height": "36px", "width": "100%"},
				)], id="extra_obj_input_div", hidden=True),
		]),
		html.Div(className="col-lg-4 col-xs-12", style={"padding": "0"}, children=[

			## redshift input
			html.Div(className="col-lg-6 col-md-3 col-sm-4 col-xs-6", children=[
				html.Label(
					html.H4("Redshift (z)"),
				),
				dcc.Input( # do not use type="number"! it is automatically updated when the next field changes
					id="redshift_input", # redshift_dropdown
					type="text", step="any", pattern=r"-?\d+(\.\d*)?|-?\.\d+",
					value=redshift or "", placeholder=redshift_default, min=-1,
					style={"height": "36px", "width": "100%"}, inputMode="numeric",
				)]),

			## redshift stepping dropdown
			html.Div(className="col-lg-6 col-md-3 col-sm-4 col-xs-6", children=[
				html.Label(
					html.H4("z stepping"),
				),
				dcc.Dropdown(
					id="redshift_step", options=["any", 0.1, 0.01, 0.001, 0.0001],
					value=stepping, placeholder="Any",
				)]),

		]),
	]),

	html.Div(className="row", id="pipeline_redshift", children=[

		## pipeline info - redshift
		html.Div(className="col-lg-2 col-md-3 col-sm-4 col-xs-6", children=[
			html.Label(
				html.H4("Z", style={"color": "grey"}),
			),
			dcc.Input(
				id="redshift_sdss_z", placeholder="N/A", value="", readOnly=True,
				style={"height": "36px", "width": "100%"}, inputMode="numeric",
			)], title="Read only"),

		## pipeline info - reduced χ²
		html.Div(className="col-lg-2 col-md-3 col-sm-4 col-xs-6", children=[
			html.Label(
				html.H4("RCHI2", style={"color": "grey"}),
			),
			dcc.Input(
				id="redshift_sdss_rchi2", placeholder="N/A", value="", readOnly=True,
				style={"height": "36px", "width": "100%"}, inputMode="numeric",
			)], title="Read only"),

		## pipeline info - bad redshift fits
		html.Div(className="col-lg-2 col-md-3 col-sm-4 col-xs-6", children=[
			html.Label(
				html.H4("ZWARNING", style={"color": "grey"}),
			),
			dcc.Input(
				id="redshift_sdss_zwarning", placeholder="N/A", value="", readOnly=True,
				style={"height": "36px", "width": "100%"}, inputMode="numeric",
			)], title="Read only"),

		## right ascension
		html.Div(className="col-lg-2 col-md-3 col-sm-4 col-xs-6", children=[
			html.Label(
				html.H4("RA (°)", style={"color": "grey"}),
			),
			dcc.Input(
				id="redshift_sdss_ra", placeholder="N/A", value="", readOnly=True,
				style={"height": "36px", "width": "100%"}, inputMode="numeric",
			)], title="Read only"),

		## declination
		html.Div(className="col-lg-2 col-md-3 col-sm-4 col-xs-6", children=[
			html.Label(
				html.H4("DEC (°)", style={"color": "grey"}),
			),
			dcc.Input(
				id="redshift_sdss_dec", placeholder="N/A", value="", readOnly=True,
				style={"height": "36px", "width": "100%"}, inputMode="numeric",
			)], title="Read only"),

	]),

	## multiepoch spectra plot
	# dcc.Checklist(
	# 	id="epoch_list",
	# 	labelStyle={"display": "inline-block"}
	# ),

	html.Div(className="row", children=[
		html.Div(className="col-xs-12", children=[
			dcc.Graph(
				id="spectra_plot",
				style={
					"position": "relative", "overflow": "hidden",
					"height": "max(450px, min(64vw, 80vh))", "width": "100%"},
			),
		]),
	]),

	html.Div(className="row", children=[
		html.Div(className="col-lg-4 col-xs-12", style={"padding": "0"}, children=[

			## axis range (note: these settings are volatile/auto-resetted)
			html.Div(className="col-lg-6 col-md-3 col-sm-4 col-xs-6", children=[

				## y-axis range
				html.Div(className="row", children=[
					html.Div(className="col-xs-12", children=[
						html.Label(
							html.H4("Y-axis range"),
						),
						dcc.Input(
							id="axis_y_max", type="number", step=1, value=y_max_default, placeholder="Max",
							style={"height": "36px", "width": "100%"},
						),
						dcc.Input(
							id="axis_y_min", type="number", step=1, value=y_min_default, placeholder="Min",
							style={"height": "36px", "width": "100%"},
						)]),
				]),

				## x-axis range
				html.Div(className="row", children=[
					html.Div(className="col-xs-12", children=[
						html.Label(
							html.H4("X-axis observed λ range (Å)"),
						),
						dcc.Input(
							id="axis_x_max", type="number", step=1, value=int(x_max), placeholder="Max", # was wave_max
							style={"height": "36px", "width": "100%"},
						),
						dcc.Input(
							id="axis_x_min", type="number", step=1, value=int(x_min), placeholder="Min", # was wave_min
							style={"height": "36px", "width": "100%"},
						)]),
				]),

				# links
				html.Div(className="row", children=[
					html.Div(className="col-xs-12", children=[
						html.H4("Object links"),
						html.Ul(id="generated_links_list"),
					], id="generated_links", hidden=True),
				]),

			]),

			## spectral smoothing
			html.Div(className="col-lg-6 col-md-3 col-sm-4 col-xs-6", children=[
				html.Label(
					html.H4("Smoothing"),
				),
				dcc.Input(
					id="smooth_input", type="number", step=2, min=1, value=smooth_default, placeholder="SmoothWidth",
					style={"height": "36px", "width": "100%"}, max=smooth_max,
				), # PBH: closes dcc.Input
			]), # PBH: closes html.Div

		]),
		html.Div(className="col-lg-8 col-xs-12", style={"padding": "0"}, children=[

			## label spectral lines (emission) (2 columns)
			html.Div(className="col-md-6 col-sm-9 col-xs-12", children=[
				html.Label(
					html.H4("Emission lines", id="line_list_emi_h4", n_clicks=0),
				),
				dcc.Checklist(id="line_list_emi", options=[
					# Set up emission-line active plotting dictionary with values set to the transition wavelengths
					{"label": f"{i[2]: <10}\t(%sÅ)" % round(float(i[1])),
					 "value": f"{i[1]}"} for i in spec_line_emi],
					value=spec_line_emi[numpy.bool_(numpy.int_(spec_line_emi[:, 0])), 1].tolist(), # values are wavelengths
					style={"columnCount": "2"},
					inputStyle={"marginRight": "5px"},
					labelStyle={"whiteSpace": "pre-wrap"},
				),
			]),

			## label spectral lines (absorption) (2 columns)
			html.Div(className="col-md-6 col-sm-9 col-xs-12", children=[
				html.Label(
					html.H4("Absorption lines", id="line_list_abs_h4", n_clicks=0),
				),
				dcc.Checklist(id="line_list_abs", options=[
					# Set up absorption-line active plotting dictionary with values set to the transition names
					{"label": f"{i[3]: <10}\t(%sÅ)" % round(float(i[2].split()[0])),
					 "value": f"{i[2].split()[0]}"} for i in spec_line_abs],
					value=[s.split()[0] for s in spec_line_abs[numpy.bool_(numpy.int_(spec_line_abs[:, 0])), 2]], # wavelengths
					style={"columnCount": "2"},
					inputStyle={"marginRight": "5px"},
					labelStyle={"whiteSpace": "pre-wrap"},
				),
			]),

		]),
	]),

	## TODO: print source information (ra, dec, z, etc...) from some catalog
	# html.Div([
	# 	html.H5(id="property_text")
	# ])

])


###
### interactive callback functions for updating spectral plot
###

## switch between known program(s) or manual input
# use values specified through `search` and `hash` if applicable
# see https://developer.mozilla.org/docs/Web/API/Location for definition
@app.callback(
	Output("fieldid_input_div", "hidden"),
	Output("catalogid_input_div", "hidden"),
	Output("fieldid_dropdown_div", "hidden"),
	Output("catalogid_dropdown_div", "hidden"),
	Output("window_location", "search"),
	Output("program_dropdown", "value"),
	Output("fieldid_input", "value"),
	Output("catalogid_input", "value"),
	Output("redshift_input", "value", allow_duplicate=True),
	Input("window_location", "search"),
	Input("program_dropdown", "value"),
	State("extra_func_list", "value"),
	prevent_initial_call="initial_duplicate")
def set_input_or_dropdown(search: str, program: str, checklist: list[str]):
	fid_mjd, catalog, redshift = "", "", ""
	for x in search.lstrip("?").split("&"):
		if program and program != "(other)": break
		if not fullmatch(r"\d+p?-\d+-[^-](.*[^-])?", x): continue
		program = "(other)"
		fid_mjd = "-".join(x.split("-", 2)[:2])
		catalog = "-".join(x.split("-", 2)[2:])
	if program == "(other)" and "p" in checklist and fullmatch(r"\d+(-.*)?", fid_mjd):
		field = int(fid_mjd.split("-", 1)[0])
		catid = int(catalog)
		for prog in programs.keys():
			if field not in programs.get(f"{prog    }", []): continue
			if catid not in fieldIDs.get(f"{field   }", []): continue
			if catid not in fieldIDs.get(f"{prog}-all", []): continue
			program = prog

	tt, ff = (True, True), (False, False)
	ret = search, program, fid_mjd, catalog, redshift
	# return *ff, *ff, *ret
	if program == "(other)":
		return *ff, *tt, *ret
	else:
		return *tt, *ff, *ret

## dropdown menu
@app.callback(
	Output("fieldid_dropdown", "options"),
	Input("program_dropdown", "value"))
def set_fieldid_options(selected_program):
	if not selected_program or selected_program == "(other)": return []
	xs = programs.get(selected_program, []) + ["all"]
	return [{"label": str(x), "value": str(x)} for x in xs]

@app.callback(
	Output("catalogid_dropdown", "options"),
	Input("fieldid_dropdown", "value"),
	Input("program_dropdown", "value"))
def set_catalogid_options(selected_fieldid, selected_program):
	if not selected_program or selected_program == "(other)": return []
	if not selected_fieldid: return []
	# the following lines are where field numbers are obtained, use strings not numbers for both labels and values
	if selected_fieldid == "all":
		xs = fieldIDs.get(f"{selected_program}-{selected_fieldid}", [])
	else:
		xs = fieldIDs.get(f"{selected_fieldid}", [])
	return [{"label": str(x), "value": str(x)} for x in xs]

@app.callback(
	Output("fieldid_dropdown", "value"),
	Input("fieldid_dropdown", "options"),
	Input("fieldid_input", "value"),
	State("program_dropdown", "value"))
def set_fieldid_value(options, input: str, program: str):
	try:
		if input and program == "(other)":
			return input
		if input and program and fullmatch(r"\d+(-.*)?", input):
			return input.split("-", 1)[0]
		# uncomment the following line to automatically choose the first field in the program
		# return options[0]["value"]
	except Exception as e:
		if str(e): print_exc()
	return ""

@app.callback(
	Output("catalogid_dropdown", "value"),
	Input("catalogid_dropdown", "options"),
	Input("catalogid_input", "value"),
	State("program_dropdown", "value"))
def set_catalogid_value(options, input: str, program: str):
	try:
		if input and program:
			return input
		# uncomment the following line to automatically choose the first catid in the field
		# return options[0]["value"]
	except Exception as e:
		if str(e): print_exc()
	return ""

# enable/disable stepping for the redshift input (see comment in the beginning of the file)
@app.callback(
	Output("redshift_input", "value", allow_duplicate=True),
	Output("redshift_input", "type"),
	Output("redshift_input", "step"),
	State("redshift_input", "value"),
	Input("redshift_step", "value"),
	prevent_initial_call=True)
def set_redshift_stepping(z, step):
	if not step: step = "any"
	if str(step).lower() == "any":
		type = "text"
	else:
		type = "number"
		if z: z = f"%0.{-int(math.log10(float(step)))}f" % float(z)
	return z, type, step

# set extra object(s) list to plot for comparison
# syntax example: http://127.0.0.1:8050/?100701-59719-27021597909876068&extra=1163-52669-0597
@app.callback(
	Output("extra_obj_input", "value"),
	Input("window_location", "search"))
def set_extra_obj(search: str):
	extra_obj = ""
	for x in search.lstrip("?").split("&"):
		if not fullmatch(r"[^=]+=[^=]+", x): continue
		k, v = x.split("=", 1)
		if k in ["ext", "extra", "prev", "previous"]: extra_obj = v
	return extra_obj

# reset axes range, smooth width, and redshift when any of program/fieldid/catid changes
@app.callback(
	Output("axis_y_max", "value"),
	Output("axis_y_min", "value"),
	Output("axis_x_max", "value"),
	Output("axis_x_min", "value"),
	Output("redshift_input", "value", allow_duplicate=True),
	Output("redshift_step", "value"),
	Output("smooth_input", "value"),
	State("axis_y_max", "value"),
	State("axis_y_min", "value"),
	State("axis_x_max", "value"),
	State("axis_x_min", "value"),
	State("redshift_input", "value"),
	State("redshift_step", "value"),
	Input("window_location", "hash"),
	Input("program_dropdown", "value"),
	Input("fieldid_dropdown", "value"),
	Input("catalogid_dropdown", "value"),
	prevent_initial_call=True)
def reset_on_obj_change(y_max, y_min, x_max, x_min, z, z_step, hash: str, program: str, *_):
	smooth = str(smooth_default)
	if program != "(other)":
		z, z_step = "", ""
		y_min, y_max = y_min_default, y_max_default
		x_min, x_max = int(wave_min), int(wave_max)
	for x in hash.lstrip("#").split("&"):
		if not fullmatch(r"[^=]+=[^=]+", x): continue
		k, v = x.split("=", 1)
		if k == "z": z = v
		if k == "m": smooth = v
		if k == "y" and fullmatch(r"[^,]+,[^,]+", v): y_min, y_max = v.split(",", 1)
		if k == "x" and fullmatch(r"[^,]+,[^,]+", v): x_min, x_max = v.split(",", 1)
	return y_max, y_min, x_max, x_min, z, z_step, smooth

## show/hide file upload div
@app.callback(
	Output("file_ul_div", "hidden"),
	Input("extra_func_list", "value"))
def hide_file_upload(checklist: list[str]):
	return "u" not in checklist
@app.callback(
	Output("dash-user-upload", "data"),
	State("dash-user-upload", "data"),
	Input("file_ul", "contents"),
	Input("file_ul", "filename"),
	Input("file_ul", "last_modified"))
def process_upload(sto: dict, contents: list[str], filename: list[str], timestamp: list[float]):
	if not contents: return sto
	if not sto: sto = dict()
	with TemporaryDirectory(prefix="py_", ignore_cleanup_errors=True) as _tmpdir:
		tmpdir = Path(_tmpdir)
		# print(tmpdir)
		for s, _f, t in zip(contents, filename, timestamp):
			try:
				# print((s[:100], _f, t))
				f = tmpdir / _f
				mime, data = s.split(",", 1)
				head, data = 0, b64decode(data).decode()
				for line in data.splitlines():
					if fullmatch(r"^\s*[+-]?\d+.*", line): break
					head += 1
				with open(f, mode="w+") as io:
					io.write(data)
				a = numpy.genfromtxt(f, dtype=None, skip_header=head).transpose()
				sto[f.stem] = a
				# print(a)
			except: print_exc()
	return sto

## hide/show pipeline redshift info
@app.callback(
	Output("pipeline_redshift", "hidden"),
	Input("extra_func_list", "value"))
def hide_pipeline_redshift(checklist: list[str]):
	return "z" not in checklist
@app.callback(
	Output("redshift_sdss_zwarning", "value"),
	Output("redshift_sdss_z", "value"),
	Output("redshift_sdss_rchi2", "value"),
	Output("redshift_sdss_ra", "value"),
	Output("redshift_sdss_dec", "value"),
	Input("fieldid_dropdown", "value"),
	Input("catalogid_dropdown", "value"),
	Input("fieldid_input", "value"),
	Input("catalogid_input", "value"),
	Input("extra_func_list", "value"))
def show_pipeline_redshift(field_d, cat_d, field_i, cat_i, checklist: list[str]):
	try:
		meta = fetch_catID(field_d or field_i, cat_d or cat_i, match_sdss_id="s" in checklist)[0]
		return meta["ZWARNING"], meta["Z"], meta["RCHI2"], meta["RA"], meta["DEC"]
	except Exception as e:
		if str(e): print(f"[show_pipeline_redshift]  fetch_catID{([field_d, field_i], [cat_d, cat_i])}")
		if str(e): print(e) if isinstance(e, HTTPError) else print_exc()
		return None, None, None, None, None

@app.callback(
	Output("generated_links_list", "children"),
	Output("generated_links", "hidden"),
	Input("redshift_sdss_ra", "value"),
	Input("redshift_sdss_dec", "value"),
)
def display_generated_links(ra: float, dec: float):
	links = object_links(ra, dec)
	return [
		html.Li(html.A(id, href=url, target="_blank"))
		for id, url in (s.split(": ", 1) for s in links)
	], (not links)

@app.callback(
	Output("line_list_emi_h4", "n_clicks"),
	Output("line_list_emi", "value"),
	Input("line_list_emi_h4", "n_clicks"),
	State("line_list_emi", "value"),
	State("line_list_emi", "options"),
)
def line_list_emi_select_all(clk: int, val: list, opt: list):
	if (clk > 0):
		clk = 0
		all = [x["value"] for x in opt]
		val = all if len(val) < len(all) else []
	return clk, val

@app.callback(
	Output("line_list_abs_h4", "n_clicks"),
	Output("line_list_abs", "value"),
	Input("line_list_abs_h4", "n_clicks"),
	State("line_list_abs", "value"),
	State("line_list_abs", "options"),
)
def line_list_abs_select_all(clk: int, val: list, opt: list):
	if (clk > 0):
		clk = 0
		all = [x["value"] for x in opt]
		val = all if len(val) < len(all) else []
	return clk, val

## plot the spectra
@app.callback(
	Output("spectra_plot", "figure"),
	Output("redshift_input", "value"),
	Input("fieldid_dropdown", "value"),
	Input("catalogid_dropdown", "value"),
	Input("fieldid_input", "value"),
	Input("catalogid_input", "value"),
	Input("extra_obj_input", "value"),
	Input("redshift_input", "value"), # redshift_dropdown
	Input("redshift_input", "step"),
	Input("axis_y_max", "value"),
	Input("axis_y_min", "value"),
	Input("axis_x_max", "value"),
	Input("axis_x_min", "value"),
	Input("line_list_emi", "value"),
	Input("line_list_abs", "value"),
	Input("smooth_input", "value"),
	Input("extra_func_list", "value"),
	Input("dash-user-upload", "data"))
# The list of inputs above applies to the following function
def make_multiepoch_spectra(field_d, cat_d, field_i, cat_i, extra_obj, redshift, redshift_step,
                            y_max, y_min, x_max, x_min, list_emi, list_abs, smooth,
                            checklist: list[str], user_data: dict):
	layout_axis = dict(fixedrange=True)
	layout = dict(yaxis=layout_axis, xaxis=layout_axis, xaxis2=layout_axis)
	xscale, xtype = identity, "linear"
	if "l" in checklist: xscale, xtype = math.log10, "log" # type: ignore

	fieldid, catalogid = str(field_d or field_i), str(cat_d or cat_i)
	smooth, z = int(smooth or smooth_default), float(redshift or redshift_default)
	if (1 + z) <= 0: z = math.nextafter(-1, 0) # z ∈ (-1, +∞)

	names, waves, fluxes, delta = list[str](), list[NDArray](), list[NDArray](), list[NDArray]()
	if user_data:
		for k, v in user_data.items():
			try: #
				name, wave, flux = str(k), numpy.asarray(v[0]), numpy.asarray(v[1])
				errs = numpy.asarray(v[2] if 2 < len(v) else [])
				if mean(wave) <= 10: wave = 10**wave # λ
				if median(wave) >= 5000: wave = wave / (1 + z) # consider as observed instead of rest frame
				if len(errs) > 0:
					if mean(errs) < 1 and median(errs) < 1 and std(errs) < 1: pass # consider as σ
					else:
						numpy.seterr(divide="ignore") # :(
						errs = 1 / sqrt(errs) # σ
				# print((name, wave, flux, errs))
				names.append(name), waves.append(wave), fluxes.append(flux), delta.append(errs) # type: ignore
			except: print_exc()
	noop_size = len(names)

	try:
		meta, name, wave, flux, errs = fetch_catID(fieldid, catalogid, extra_obj, match_sdss_id="s" in checklist) # type: ignore
		names.extend(name), waves.extend(wave), fluxes.extend(flux), delta.extend(errs) # type: ignore
		if meta["Z"] and not redshift and redshift_step == "any": redshift = meta["Z"]
	except Exception as e:
		if str(e): print(f"[make_multiepoch_spectra] fetch_catID{([field_d, field_i], [cat_d, cat_i], extra_obj)}")
		if str(e): print(e) if isinstance(e, HTTPError) else print_exc()
		return Figure(layout=layout), redshift

	try:

		if not y_min and not y_max: y_min, y_max = y_min_default, y_max_default
		if not x_min and not x_max: x_min, x_max = int(wave_max), int(wave_min)
		y_min, y_max = int(y_min or 0), int(y_max or 0)
		x_min, x_max = int(x_min or 0), int(x_max or 0)
		if y_max < y_min: y_min, y_max = y_max, y_min
		if x_max < x_min: x_min, x_max = x_max, x_min
		# changed following to explicitly be in rest frame (bottom x axis)
		rest_x_max = math.ceil(x_max / (1 + z))
		rest_x_min = math.floor(x_min / (1 + z))

		fig = Figure(layout=layout)
		fig.layout.yaxis.range = [y_min, y_max]
		fig.layout.xaxis.range = [xscale(rest_x_min), xscale(rest_x_max)]

		# For each spectrum in the list
		for i in range(len(names)):
			kws = {}
			if fullmatch(r"allplate-\d+.*", names[i], IGNORECASE):
				kws["line_color"] = "#606060"
			if fullmatch(r"allFPS-\d+.*", names[i], IGNORECASE):
				kws["line_color"] = "#000000"
			# create trace of smoothed spectra
			fig.add_trace(Scatter(
				x=waves[i] if i < noop_size else waves[i] / (1 + z),
				y=convolve(fluxes[i], Box1DKernel(smooth)),
				error_y_width=0, error_y_thickness=1, error_y_type="data", # σ
				error_y_array=delta[i] if delta[i].size and "e" in checklist else None,
				name=names[i], opacity=1 / 2, mode="lines", **kws)) # type: ignore
			# create "ghost trace" spanning the displayed observed wavelength range:
			fig.add_trace(Scatter(
				x=[x_min, x_max], y=[numpy.nan, numpy.nan], showlegend=False))
		fig.data[1].xaxis = "x2" # assign the "ghost trace" to a new axis object

		# Line labels for x-axis
		for l in spec_line_emi: # emission
			j, x = l[2], l[1] # j is the label, x is the wavelength
			if x not in list_emi: continue # skip if the wavelength is not in the active plotting dictionary
			x = float(x)
			if (rest_x_min <= x and x <= rest_x_max):
				fig.add_vline(x=x, line_dash="solid", opacity=1 / 4)
				fig.add_annotation(x=xscale(x), y=y_max, text=j, hovertext=f" {j} ({x} Å)", textangle=70)

		for l in spec_line_abs: # absorption
			j, xs = l[3], l[2].split() # j is the label, xs is the wavelength list
			# j, xs, n, b = l[3], l[2].split(), l[1], bool(l[0]) # j = label, xs = wavelength list, n = multiplicity, b = 0/1
			labeled = False # reset labeling flag
			if xs[0] not in list_abs: continue # skip if the transition is not in the active plotting dictionary
			for x in (xs := list(map(float, xs))): # for each wavelength in the wavelength list
				if (rest_x_min <= x and x <= rest_x_max):
					fig.add_vline(x=x, line_dash="dot", opacity=1 / 2)
					# label the first entry in the list of wavelengths
					labeled or fig.add_annotation(x=xscale(x), y=y_min, text=j, hovertext=f" {j} ({xs} Å)", textangle=70)
					labeled = True

		fig.update_layout( # Rest wavelengths on top axis; observed wavelengths on bottom axis
			# The xaxis1 command just displays the rest-frame axis numbers and title.
			xaxis1=dict(type=xtype, side="top", title_text="Rest-Frame Wavelength (Å)"),
			# The xaxis2 command displays the DATA and the observed-frame axis title, but the numbers are already there.
			xaxis2=dict(type=xtype, anchor="y", overlaying="x", title_text="Observed Wavelength (Å)"),
		)

		fig.update_layout(xaxis2_range=[xscale(x_min), xscale(x_max)]) # this line is necessary for some reason

		fig.update_layout(uirevision=f"{fieldid};{catalogid};{extra_obj}")

	except: print_exc()

	return fig, redshift


if __name__ == "__main__":
	# app.run(threaded=True, debug=True)
	# app.run(host="0.0.0.0", port="8050", threaded=True, debug=True, dev_tools_ui=dash.__version__ >= "3")
	app.run(host="127.0.0.1", port="8050", threaded=True, debug=True, dev_tools_ui=dash.__version__ >= "3")

