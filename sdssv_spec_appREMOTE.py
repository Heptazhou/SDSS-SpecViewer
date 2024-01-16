### SpecViewer for Python 3.9+

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
from urllib.parse import urlsplit

import dash
import numpy
import requests
from astropy.convolution import Box1DKernel, convolve
from astropy.io import fits
from astropy.io.fits.fitsrec import FITS_rec
from dash import dcc, html
from dash.dependencies import Input, Output, State
from numpy import sqrt
from numpy.typing import NDArray
from plotly.graph_objects import Figure, Scatter
from requests.exceptions import HTTPError

###
### input the data directory path
###

# NOTE TO CODER: JSON LIKES STRING KEYS FOR DICTIONARIES!!!!!!
dictionaries = json.load(open("dictionaries.txt"))
authentication = "authentication.txt"
programs: dict[str, list[int]] = dictionaries[0]
fieldIDs: dict[str, list[int]] = dictionaries[1]
catalogIDs: dict[str, list[list | int]] = dictionaries[2]

# for testing
# print(programs)
# print("those were programs")
# print(fieldIDs)
# print("those were fieldIDs")
# print(catalogIDs)
# print("those were catalogIDs")
# print("catalog*5", catalogIDs["27021598109009995"]) # for testing
# print("field17049", fieldIDs["17049"]) # for testing

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
y_max_default = 100
y_min_default = -10

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

def SDSSV_buildURL(field: str, MJD: int, objID: str, branch: str):
	"""
	A function to build the url that will be used to fetch the data.

	Field ID may require leading zero(es),
	use str.zfill(6) to fix it.
	"""
	path = ""
	file = f"spec-{field.rstrip('p')}-{MJD}-{objID}.fits" # PBH

	if branch == "v5_4_45":
		path = "https://data.sdss.org/sas/dr9/sdss/spectro/redux"
	if branch == "v5_5_12":
		path = "https://data.sdss.org/sas/dr10/sdss/spectro/redux"
	if branch == "v5_6_5":
		path = "https://data.sdss.org/sas/dr11/sdss/spectro/redux"
	if branch == "v5_7_0" or branch == "v5_7_2":
		path = "https://data.sdss.org/sas/dr12/sdss/spectro/redux"
	if branch == "v5_9_0":
		path = "https://data.sdss.org/sas/dr13/sdss/spectro/redux"
	if branch == "v5_10_0":
		path = "https://data.sdss.org/sas/dr15/sdss/spectro/redux"
	if branch == "v5_13_0":
		path = "https://data.sdss.org/sas/dr16/sdss/spectro/redux"
	if branch == "v5_13_2":
		path = "https://data.sdss.org/sas/dr18/spectro/sdss/redux"
	if not path:
		path = "https://data.sdss5.org/sas/sdsswork/bhm/boss/spectro/redux"
		file = f"{MJD}/{file}"

	url = f"{path}/{branch}/spectra/lite/{field}/{file}"
	# print(url) # for testing
	return url

def SDSSV_fetch(username: str, password: str, field, MJD: int, objID, branch="") \
	-> tuple[FITS_rec, NDArray, NDArray, NDArray]:
	"""
	Fetch spectral data for a SDSS-RM object on a
		specific field on a specific MJD, using the user
		supplied authentication.
	"""
	if type(field) == str:
		if fullmatch(r"\d+p", field):
			branch = branch or "v6_0_4"
	try:
		if (field := int(field)) < 15000:
			branch = branch or "v5_13_2"
		else:
			field = str(field).zfill(6)
	except: None
	field, objID = str(field), str(objID) # ensure type

	if not branch:
		for v in ("master", "v6_1_2", "v6_1_1"):
			try: return SDSSV_fetch(username, password, field, MJD, objID, v)
			except: continue
		raise HTTPError(f"SDSSV_fetch failed for {(field, MJD, objID)}")
	if not (field and MJD and objID):
		raise HTTPError(f"SDSSV_fetch failed for {(field, MJD, objID, branch)}")
	if (field, MJD, objID, branch) in cache:
		return cache[(field, MJD, objID, branch)]

	url = SDSSV_buildURL(field, MJD, objID, branch)
	# print(url) # for testing
	r = requests.get(url, auth=(username, password) if "/sdsswork/" in url else None)
	r.raise_for_status()
	print(r.status_code, url)
	numpy.seterr(divide="ignore") # Python does not comply with IEEE 754 :(
	HDUs = fits.open(BytesIO(r.content))
	meta = HDUs["SPALL"].data
	wave = HDUs["COADD"].data["LOGLAM"] # lg(λ)
	flux = HDUs["COADD"].data["FLUX"]   # f_λ
	errs = HDUs["COADD"].data["IVAR"]   # τ = σ⁻²
	wave = 10**wave                     # λ
	errs = 1 / sqrt(errs)               # σ
	# print(f"meta: {type(meta)} = {str(meta)[:100]}")
	# print(f"wave: {type(wave)} = {str(wave)[:100]}")
	# print(flux) # for testing
	r = meta, wave, flux, errs
	cache[(field, MJD, objID, branch)] = r
	return r

def fetch_catID(field, catID, extra="") \
	-> tuple[list[float], list[str], list[NDArray], list[NDArray], list[NDArray]]:
	#        here float is actually int & float, as float in Python contains int :(
	if not (field and catID or extra):
		raise Exception()
	field = str(field).replace(" ", "")
	catID = str(catID).replace(" ", "")
	extra = str(extra).replace(" ", "")
	if (field, catID, extra) in cache:
		return cache[(field, catID, extra)]
	name, wave, flux, errs = list[str](), list[NDArray](), list[NDArray](), list[NDArray]()
	# print(catID)
	# # print("catalogIDs[catID]")
	# testval = catalogIDs[catID]
	# print(testval)
	data = catalogIDs.get(catID, [[]]) # [(ZWARNING, Z, RCHI2), {FIELD,MJD}...]
	meta = list(data[0] or [None, None, None]) # (ZWARNING, Z, RCHI2)
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
		try:
			mjd_final = str(dat[0]["MJD_FINAL"][0])
		except:
			mjd_final = str(dat[0]["MJD"][0])
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
			raise
		if not meta[0]: meta[0] = dat[0]["ZWARNING"][0]
		if not meta[1]: meta[1] = dat[0]["Z"][0]
		if not meta[2]: meta[2] = dat[0]["RCHI2"][0]
		try:
			mjd_final = str(dat[0]["MJD_FINAL"][0])
		except:
			mjd_final = str(dat[0]["MJD"][0])
		mjd_list = [mjd]
		name.append(mjd_final)
		wave.append(dat[1])
		flux.append(dat[2])
		errs.append(dat[3])
	else:
		mjd_list = []
		for x in data[1:]: # {13'FIELD,5'MJD}
			x = int(x)
			fid, mjd = divmod(abs(x), 10**5)
			if field == "all" or int(field) == fid:
				dat = SDSSV_fetch(username, password, fid, mjd, catID)
				try:
					mjd_final = str(dat[0]["MJD_FINAL"][0])
				except:
					mjd_final = str(dat[0]["MJD"][0])
				name.append(mjd_final)
				wave.append(dat[1])
				flux.append(dat[2])
				errs.append(dat[3])
				if mjd not in mjd_list: mjd_list.append(mjd)
		mjd_list.sort(reverse=True)
	# print(mjd_list)
	# allplate
	for mjd in mjd_list:
		if mjd <= 59392:
			try:
				dat = SDSSV_fetch(username, password, "allepoch", mjd, catID)
			except Exception as e:
				# if str(e): print(e) if isinstance(e, HTTPError) else print_exc()
				continue
			name.append(f"allplate-{mjd}")
			wave.append(dat[1])
			flux.append(dat[2])
			errs.append(dat[3])
			break
	# allFPS
	for mjd in mjd_list:
		if mjd >= 59393:
			try:
				dat = SDSSV_fetch(username, password, "allepoch", mjd, catID)
			except Exception as e:
				# if str(e): print(e) if isinstance(e, HTTPError) else print_exc()
				continue
			name.append(f"allFPS-{mjd}")
			wave.append(dat[1])
			flux.append(dat[2])
			errs.append(dat[3])
			break
	# print(flux) # for testing
	if not (meta and name and wave and flux):
		raise HTTPError(f"fetch_catID failed for {(field, catID, extra)}")
	r = meta, name, wave, flux, errs
	cache[(field, catID, extra)] = r
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
	fetch_test = SDSSV_fetch(username, password, 112359, 60086, 27021600949438682)
	print("Verification succeeded.")
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
# the first column means whether to show this line or not by default
# the second column is the wavelength, which must be unique
spec_line_emi = numpy.asarray([
	[1, 7753.1900, "[Ar III]"],
	[1, 7137.7700, "[Ar III]"],
	[1, 6564.6130, "H α"     ],
	[0, 6365.5350, "[O I]"   ],
	[0, 6302.0460, "[O I]"   ],
	[0, 5877.2990, "He I"    ],
	[0, 5577.3390, "[O I]"   ],
	[0, 5411.5200, "He II"   ],
	[1, 5008.2390, "[O III]" ],
	[1, 4960.2950, "[O III]" ],
	[1, 4862.6830, "H β"     ],
	[0, 4685.6800, "He II"   ],
	[0, 4363.2090, "[O III]" ],
	[1, 4341.6840, "H γ"     ],
	[1, 4102.8920, "H δ"     ],
	[0, 3971.1950, "H ε"     ],
	[0, 3890.1510, "H ζ"     ],
	[0, 3889.7520, "He I"    ],
	[1, 3728.4830, "[O II]"  ], # 3729.8740 3727.0920
	[1, 2799.9410, "Mg II"   ], # 2803.5300 2796.3520
	[1, 2326.0000, "C II"    ],
	[1, 1908.7340, "C III]"  ],
	[0, 1640.4200, "He II"   ],
	[1, 1549.4800, "C IV"    ],
	[1, 1396.7500, "Si IV"   ],
	[0, 1305.5300, "O I"     ],
	[1, 1240.8100, "N V"     ],
	[1, 1215.6710, "Ly α"    ],
	[0, 1123.0000, "P V"     ],
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
	[1, 2, "1862.7911 1854.7183          ", "Al III"     ],
	[0, 1, "1670.7886                    ", "Al II"      ],
	[0, 1, "1608.4511                    ", "Fe II 1608" ],
	[1, 2, "1550.7785 1548.2049          ", "C IV"       ],
	[0, 1, "1526.7070                    ", "Si II 1526" ],
	[1, 2, "1402.7729 1393.7602          ", "Si IV"      ],
	[1, 1, "1334.5323                    ", "C II"       ],
	[0, 1, "1304.3702                    ", "Si II 1304" ],
	[0, 1, "1302.1685                    ", "O I"        ],
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

# print(spec_line_emi[numpy.bool_(spec_line_emi[:, 0]), 2].tolist())
# print(spec_line_abs[numpy.bool_(spec_line_abs[:, 0]), 3].tolist())

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
				"e": "show error (σ)",
				"u": "file uploader",
			},
				value=["z", "p"], inline=True, persistence=True, persistence_type="local",
				style={"marginTop": "20px", "display": "flex", "flexFlow": "wrap"},
				inputStyle={"marginRight": "5px"},
				labelStyle={"width": "180px", "whiteSpace": "nowrap"},
			),

			html.Div(dcc.Upload(html.Div([
				html.Br(), html.H4("Drag and drop / select file(s)"), html.Br(),
			], style={"margin": "0 20px", "textAlign": "center"}),
				id="file_ul", multiple=True, style={"border": "1px dashed", "borderRadius": "5px"},
			), id="file_ul_div", hidden=True, style={"margin": "20px 0", "width": "100%"}),
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
					value=redshift or "", placeholder=redshift_default, min=0,
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
			)]),

		## pipeline info - reduced χ²
		html.Div(className="col-lg-2 col-md-3 col-sm-4 col-xs-6", children=[
			html.Label(
				html.H4("RCHI2", style={"color": "grey"}),
			),
			dcc.Input(
				id="redshift_sdss_rchi2", placeholder="N/A", value="", readOnly=True,
				style={"height": "36px", "width": "100%"}, inputMode="numeric",
			)]),

		## pipeline info - bad redshift fits
		html.Div(className="col-lg-2 col-md-3 col-sm-4 col-xs-6", children=[
			html.Label(
				html.H4("ZWARNING", style={"color": "grey"}),
			),
			dcc.Input(
				id="redshift_sdss_zwarning", placeholder="N/A", value="", readOnly=True,
				style={"height": "36px", "width": "100%"}, inputMode="numeric",
			)]),

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

			]),

			## spectral smoothing
			html.Div(className="col-lg-6 col-md-3 col-sm-4 col-xs-6", children=[
				html.Label(
					html.H4("Smoothing"),
				),
				dcc.Input(
					id="smooth_input", type="number", step=2, min=1, value=smooth_default, placeholder="SmoothWidth",
					style={"height": "36px", "width": "100%"}, max=smooth_max,
				),
			]),

		]),
		html.Div(className="col-lg-8 col-xs-12", style={"padding": "0"}, children=[

			## label spectral lines (emission) (2 columns)
			html.Div(className="col-md-6 col-sm-9 col-xs-12", children=[
				html.Label(
					html.H4("Emission lines"),
				),
				dcc.Checklist(id="line_list_emi", options=[
					# Set up emission-line active plotting dictionary with values set to the transition wavelengths
					{"label": "{: <10}\t({}Å)".format(i[2], round(float(i[1]))),
					 "value": i[1]} for i in spec_line_emi],
					value=spec_line_emi[numpy.bool_(spec_line_emi[:, 0]), 1].tolist(), # values are wavelengths
					style={"columnCount": "2"},
					inputStyle={"marginRight": "5px"},
					labelStyle={"whiteSpace": "pre-wrap"},
				),
			]),

			## label spectral lines (absorption) (2 columns)
			html.Div(className="col-md-6 col-sm-9 col-xs-12", children=[
				html.Label(
					html.H4("Absorption lines"),
				),
				dcc.Checklist(id="line_list_abs", options=[
					# Set up absorption-line active plotting dictionary with values set to the transition names
					{"label": "{: <10}\t({}Å)".format(i[3], round(float(i[2].split()[0]))),
					 "value": i[2].split()[0]} for i in spec_line_abs],
					value=[s.split()[0] for s in spec_line_abs[numpy.bool_(spec_line_abs[:, 0]), 2]], # wavelengths
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
	Output("window_location", "href"),
	Output("program_dropdown", "value"),
	Output("fieldid_input", "value"),
	Output("catalogid_input", "value"),
	Output("redshift_input", "value", allow_duplicate=True),
	Input("window_location", "href"),
	Input("program_dropdown", "value"),
	State("extra_func_list", "value"),
	prevent_initial_call="initial_duplicate")
def set_input_or_dropdown(location: str, program: str, checklist: list[str]):
	url = urlsplit(location) # <scheme>://<netloc>/<path>?<query>#<fragment>
	search = url.query.lstrip("?")
	hash = url.fragment.lstrip("#")
	fid_mjd, catalog, redshift = "", "", ""
	for x in search.split("&"):
		if program and program != "(other)": break
		if not fullmatch(r"\d+p?-\d+-[^-](.*[^-])?", x): continue
		program = "(other)"
		fid_mjd = "-".join(x.split("-", 2)[:2])
		catalog = "-".join(x.split("-", 2)[2:])
	for x in hash.split("&"):
		if not fullmatch(r"[^=]+=[^=]+", x): continue
		k, v = x.split("=", 1)
		if k == "z": redshift = v
	if program == "(other)" and "p" in checklist and fullmatch(r"\d+(-.*)?", fid_mjd):
		field = int(fid_mjd.split("-", 1)[0])
		catid = int(catalog)
		for prog in programs.keys():
			if field not in programs.get(f"{prog    }", []): continue
			if catid not in fieldIDs.get(f"{field   }", []): continue
			if catid not in fieldIDs.get(f"{prog}-all", []): continue
			program = prog

	tt, ff = (True, True), (False, False)
	ret = location, program, fid_mjd, catalog, redshift
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

# set_fieldid_value is only run when program is switched
@app.callback(
	Output("fieldid_dropdown", "value"),
	Input("fieldid_dropdown", "options"),
	Input("fieldid_input", "value"),
	State("program_dropdown", "value"))
def set_fieldid_value(available_fieldid_options, input: str, program: str):
	try:
		if input and program == "(other)":
			return input
		if input and program and fullmatch(r"\d+(-.*)?", input):
			return input.split("-", 1)[0]
		# uncomment the following line to automatically choose the first field in the program
		# return available_fieldid_options[0]["value"]
	except Exception as e:
		if str(e): print_exc()
	return ""

@app.callback(
	Output("catalogid_dropdown", "value"),
	Input("catalogid_dropdown", "options"),
	Input("catalogid_input", "value"),
	State("program_dropdown", "value"))
def set_catalogid_value(available_catalogid_options, input: str, program: str):
	try:
		if input and program:
			return input
		# uncomment the following line to automatically choose the first catid in the field
		# return available_catalogid_options[0]["value"]
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
	if type == "number" and z:
		z = f"%0.{-int(math.log10(step))}f" % float(z)
	return z, type, step

# set extra object(s) list to plot for comparison
@app.callback(
	Output("extra_obj_input", "value"),
	Input("window_location", "search"))
def set_fieldid_options(search: str):
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
def reset_on_obj_change(y_max, y_min, x_max, x_min, z, z_step, hash, program, *_):
	smooth = smooth_default
	if program != "(other)":
		z, z_step = "", ""
		y_min, y_max = y_min_default, y_max_default
		x_min, x_max = int(wave_min), int(wave_max)
	for x in (hash := str(hash).lstrip("#").split("&") if hash else []):
		if not fullmatch(r"[^=]+=[^=]+", x): continue
		k, v = x.split("=", 1)
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
	with TemporaryDirectory(prefix="py_", ignore_cleanup_errors=True) as tmpdir:
		tmpdir = Path(tmpdir)
		# print(tmpdir)
		for s, f, t in zip(contents, filename, timestamp):
			try:
				# print((s[:100], f, t))
				mime, data = s.split(",", 1)
				f = tmpdir / f
				with open(f, mode="w+") as io:
					io.write(b64decode(data).decode())
				a = numpy.genfromtxt(f).transpose()
				sto[f.stem] = a
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
	Input("fieldid_dropdown", "value"),
	Input("catalogid_dropdown", "value"))
def show_pipeline_redshift(fieldid, catalogid):
	try:
		meta = fetch_catID(fieldid, catalogid)[0]
		return meta[0], meta[1], meta[2]
	except Exception as e:
		if str(e): print(e) if isinstance(e, HTTPError) else print_exc()
		return None, None, None

## plot the spectra
@app.callback(
	Output("spectra_plot", "figure"),
	Output("redshift_input", "value"),
	Input("fieldid_dropdown", "value"),
	Input("catalogid_dropdown", "value"),
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
def make_multiepoch_spectra(fieldid, catalogid, extra_obj, redshift, redshift_step,
                            y_max, y_min, x_max, x_min, list_emi, list_abs, smooth,
                            checklist: list[str], user_data: dict):
	layout_axis = dict(fixedrange=True)
	layout = dict(yaxis=layout_axis, xaxis=layout_axis, xaxis2=layout_axis)

	names, waves, fluxes, delta = list[str](), list[NDArray](), list[NDArray](), list[NDArray]()
	if user_data:
		for k, v in user_data.items():
			try: #
				name, wave, flux = str(k), numpy.asarray(v[0]), numpy.asarray(v[1])
				errs = numpy.asarray([])
				# print((name, wave, flux))
				names.append(name), waves.append(wave), fluxes.append(flux), delta.append(errs)
			except: print_exc()
	noop_size = len(names)
	try:
		meta, name, wave, flux, errs = fetch_catID(fieldid, catalogid, extra_obj)
		names.extend(name), waves.extend(wave), fluxes.extend(flux), delta.extend(errs)
		if meta[1] and not redshift and redshift_step == "any": redshift = meta[1]
		smooth, z = int(smooth or smooth_default), float(redshift or redshift_default)
	except Exception as e:
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
		rest_x_max = math.ceil(x_max / (z + 1))
		rest_x_min = math.floor(x_min / (z + 1))

		fig = Figure(layout=layout)
		fig.layout.yaxis.range = [y_min, y_max]
		fig.layout.xaxis.range = [rest_x_min, rest_x_max]

		# For each spectrum in the list
		for i in range(len(names)):
			kws = dict()
			if fullmatch(r"allplate-\d+.*", names[i], IGNORECASE):
				kws = dict(line_color="#606060")
			if fullmatch(r"allFPS-\d+.*", names[i], IGNORECASE):
				kws = dict(line_color="#000000")
			# create trace of smoothed spectra
			fig.add_trace(Scatter(
				x=waves[i] if i < noop_size else waves[i] / (z + 1),
				y=convolve(fluxes[i], Box1DKernel(smooth)),
				error_y_width=0, error_y_thickness=1, error_y_type="data", # σ
				error_y_array=delta[i] if delta[i].size and "e" in checklist else None,
				name=names[i], opacity=1 / 2, mode="lines", **kws))
			# create "ghost trace" spanning the displayed observed wavelength range:
			fig.add_trace(Scatter(
				x=[x_min, x_max], y=[numpy.nan, numpy.nan], showlegend=False))
		fig.data[1].xaxis = "x2" # assign the "ghost trace" to a new axis object

		for i in spec_line_emi: # emission
			j, x = i[2], i[1] # j is the label, x is the wavelength
			if x not in list_emi: continue # skip if the wavelength is not in the active plotting dictionary
			x = float(x)
			if (rest_x_min <= x and x <= rest_x_max):
				fig.add_vline(x=x, line_dash="solid", opacity=1 / 4)
				fig.add_annotation(x=x, y=y_max, text=j, hovertext=f" {j} ({x} Å)", textangle=70)

		for i in spec_line_abs: # absorption
			j, xs = i[3], i[2].split() # j is the label, xs is the wavelength list
			# j, xs, n, b = i[3], i[2].split(), i[1], bool(i[0]) # j = label, xs = wavelength list, n = multiplicity, b = 0/1
			labeled = False # reset labeling flag
			if xs[0] not in list_abs: continue # skip if the transition is not in the active plotting dictionary
			for x in (xs := list(map(float, xs))): # for each wavelength in the wavelength list
				if (rest_x_min <= x and x <= rest_x_max):
					fig.add_vline(x=x, line_dash="dot", opacity=1 / 2)
					# label the first entry in the list of wavelengths
					labeled or fig.add_annotation(x=x, y=y_min, text=j, hovertext=f" {j} ({xs} Å)", textangle=70)
					labeled = True

		fig.update_layout( # Rest wavelengths on top axis; observed wavelengths on bottom axis
			xaxis1=dict(side="top", title_text="Rest-Frame Wavelength (Å)"),
			xaxis2=dict(anchor="y", overlaying="x", title_text="Observed Wavelength (Å)"),
		)

		fig.update_layout(xaxis2_range=[x_min, x_max]) # this line is necessary for some reason

		fig.update_layout(uirevision=f"{fieldid};{catalogid};{extra_obj}")

	except: print_exc()

	return fig, redshift



if __name__ == "__main__":
	# app.run(threaded=True, debug=True)
	# app.run(host="0.0.0.0", port=8050, threaded=True, debug=True)
	app.run(host="127.0.0.1", port=8050, threaded=True, debug=True)


