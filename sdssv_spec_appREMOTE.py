### SpecViewer for Python 3.9+

"""
Excelsior!
"""

import io
import json
import math
import re

import dash
import numpy
import plotly.graph_objects as go
import requests
from astropy.convolution import Box1DKernel, convolve
from astropy.io import fits
from dash import dcc, html
from dash.dependencies import Input, Output, State

###
### input the data directory path
###

# NOTE TO CODER: JSON LIKES STRING KEYS FOR DICTIONARIES!!!!!!
programs, fieldIDs, catalogIDs = json.load(open("dictionaries.txt"))
authentication = "authentication.txt"

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

# global dict to save results of `fetch_catID`, which greatly improves responsiveness after the first plot
cache: dict[tuple, tuple] = {}

# default y-axis range of spectrum plots
y_max_default = 100
y_min_default = -10

# binning/smoothing along x-axis, disabled by default (1 means no binning)
# we need an upper limit since a very large `binning` freezes the program
binning_default = 1
binning_max = 10000

### css files
external_stylesheets = [ "https://codepen.io/chriddyp/pen/bWLwgP.css",
                         "https://maxcdn.bootstrapcdn.com/bootstrap/3.4.1/css/bootstrap.min.css",
                         "https://aladin.u-strasbg.fr/AladinLite/api/v2/latest/aladin.min.css",
                         "https://use.fontawesome.com/releases/v5.15.4/css/all.css",
                         "https://use.fontawesome.com/releases/v5.15.4/css/v4-shims.css", ]

###
### Any necessary functions
###

def SDSSV_buildURL(fieldID, MJD, objID, branch):
	"""
	A function to build the url that will be used to fetch the data.

	Field IDs don't start with zero but the URLs need leading zeroes;
	using zfill(6) fixes this.
	"""
	url = "https://data.sdss5.org/sas/sdsswork/bhm/boss/spectro/redux/{}/spectra/lite/".format(branch) \
		+ "{}/{}/spec-{}-{}-{}.fits".format(str(fieldID).zfill(6), MJD, str(fieldID).zfill(6), MJD, objID)
	print(url) # for testing

	return url

def SDSSV_fetch(username, password, fieldID, MJD, objID, branch="v6_1_0"):
	"""
	Fetches spectral data for a SDSS-RM object on a
		specific field on a specific MJD. Uses the user
		supplied authentication.

	TO DO: allow for multiple MJDs and fields, for loop it up
	"""
	if not (fieldID and MJD and objID):
		raise Exception((fieldID, MJD, objID))
	url = SDSSV_buildURL(fieldID, MJD, objID, branch)
	# print(url) # for testing
	r = requests.get(url, auth=(username, password))
	r.raise_for_status()
	data_test = fits.open(io.BytesIO(r.content))
	flux = data_test[1].data["FLUX"]
	wave = 10**data_test[1].data["loglam"]
	# print(flux) # for testing
	return wave, flux

def fetch_catID(field, catID, redshift=0):
	# if (redshift > 0):
	# 	print("fetch_catID", field, catID) # for testing
	# 	print(waves)
	# 	return waves, fluxes, names
	# print("fetch_catID", field, catID) # for testing
	if not (field and catID):
		raise Exception((field, catID))
	if (field, catID) in cache:
		return cache[(field, catID)]
	fluxes = []
	waves = []
	names = []
	# print (str(catID))
	# # print ("catalogIDs[str(catID)]")
	# testval = catalogIDs[str(catID)]
	# print (testval)
	if re.fullmatch("\d+-\d+", str(field).strip()):
		fld, mjd = str(field).strip().split("-", 1)
		try:
			dat = SDSSV_fetch(username, password, fld, mjd, str(catID).strip(), "master")
		except:
			dat = SDSSV_fetch(username, password, fld, mjd, str(catID).strip())
		fluxes.append(dat[1])
		waves.append(dat[0])
		names.append(mjd)
	else:
		for i in catalogIDs[str(catID)]:
			if field == "all" or field == i[0]:
				# print("all", i[0], i[1], catID) # for testing
				dat = SDSSV_fetch(username, password, i[0], i[1], catID)
				fluxes.append(dat[1])
				waves.append(dat[0])
				names.append(i[3])
	# print(fluxes) # for testing
	if not (waves and fluxes and names):
		raise Exception((field, catID))
	cache[(field, catID)] = waves, fluxes, names
	return cache[(field, catID)]



###
### Authentication
###
try:
	print("Reading authentication file.")
	with open(authentication, "r") as i:
		lines = i.readlines()
		username = lines[0][:-1] # there will be a \n on the username
		password = lines[1][:-1] # and on the password, at least for some file systems
except: # any error from above will fall through to here.
	print("authentication.txt not provided or incomplete. Please enter authentication.")
	username = input("Enter SDSS-V username:")
	password = input("Enter SDSS-V password:")

try:
	print("Verifying authentication...")
	# fetch_test = SDSSV_fetch(username, password, 15173, 59281, 4350951054)
	fetch_test = SDSSV_fetch(username, password, 112359, 60086, 27021600949438682)
	print("Verification successful.")
except:
	print("Authentication error, please press Ctrl+C and fix authentication.txt.")
	# print("Contact Meg (megan.c.davis@uconn.edu) if the issue persists.")



### spectral lines to label in plot
# https://classic.sdss.org/dr6/algorithms/linestable.html
# the first column means whether to show this line or not by default
spec_line_emi = numpy.asarray([
	[1, 6564.61, "H α"    ],
	[1, 5008.24, "[O III]"],
	[1, 4960.30, "[O III]"],
	[1, 4862.68, "H β"    ],
	[1, 4341.68, "H γ"    ],
	[1, 4102.89, "H δ"    ],
	[0, 3889.00, "He I"   ],
	[1, 3727.09, "O II"   ],
	[1, 2798.75, "Mg II"  ],
	[1, 2326.00, "C II"   ],
	[1, 1908.73, "C III]" ],
	[0, 1640.40, "He II"  ],
	[1, 1549.06, "C IV"   ],
	[1, 1396.75, "Si IV"  ],
	[0, 1305.53, "O I"    ],
	[1, 1240.00, "N V"    ],
	[1, 1215.67, "Ly α"   ],
	[0, 1123.00, "P V"    ],
	[1, 1034.00, "O VI"   ],
	[1, 1025.72, "Ly β"   ],
])
spec_line_abs = numpy.asarray([
	[0, 2800.00, "Mg II"  ],
	[0, 2747.00, "Fe II"  ],
	[0, 2600.00, "Fe II"  ],
	[0, 2400.00, "Fe II"  ],
	[1, 1860.00, "Al III" ],
	[0, 1550.00, "C IV"   ],
	[0, 1400.00, "Si IV"  ],
	[0, 1335.00, "C II"   ],
	[0, 1240.00, "N V"    ],
])

### wavelength plotting range
wave_max = 10500.
wave_min = 3500.

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

	html.Div(className="row", children=[
		html.H2("SDSSV-BHM Spectra Viewer (remote version)"),
	]),

	html.Div(className="row", children=[

		## dropdown menu for program/fieldid/catalogid
		html.Div(className="col-lg-2 col-md-3 col-sm-4 col-xs-6", children=[
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
		html.Div(className="col-lg-2 col-md-3 col-sm-4 col-xs-6", children=[
			html.Label(
				html.H4("Field & MJD"),
			),
			dcc.Input(
				id="fieldid_input", type="text",
				placeholder="FieldID-MJD", value="", style={"height": "36px", "width": "100%"},
			)], id="fieldid_input_div", hidden=True),

		## Field ID dropdown
		html.Div(className="col-lg-2 col-md-3 col-sm-4 col-xs-6", children=[
			html.Label(
				html.H4("Field ID"),
			),
			dcc.Dropdown(
				id="fieldid_dropdown",
				placeholder="FieldID", value="",
			)], id="fieldid_dropdown_div", hidden=False),

		## catalog ID input
		html.Div(className="col-lg-4 col-md-6 col-sm-8 col-xs-12", children=[
			html.Label(
				html.H4("Catalog ID"),
			),
			dcc.Input(
				id="catalogid_input", type="text",
				placeholder="CatalogID", value="", style={"height": "36px", "width": "100%"},
			)], id="catalogid_input_div", hidden=True),

		## catalog ID dropdown
		html.Div(className="col-lg-4 col-md-6 col-sm-8 col-xs-12", children=[
			html.Label(
				html.H4("Catalog ID"),
			),
			dcc.Dropdown(
				id="catalogid_dropdown",
				placeholder="CatalogID", value="",
			)], id="catalogid_dropdown_div", hidden=False),

		## whitespace (not a field)
		html.Div(className="col-sm-4 visible-sm-block", style={"visibility": "hidden"},
                    children=[html.Label(html.H4("-")), dcc.Dropdown()]),

		## redshift input
		html.Div(className="col-lg-2 col-md-3 col-sm-4 col-xs-6", children=[
			html.Label(
				html.H4("Redshift (z)"),
			),
			dcc.Input( # do not use type="number"! it is automatically updated when the next field changes
				id="redshift_input", # redshift_dropdown
				type="text", step="any", pattern="\d+(\.\d*)?|\.\d+",
				value=redshift or "", placeholder=redshift_default, min=0,
				style={"height": "36px", "width": "100%"}, inputMode="numeric",
			)]),

		## redshift stepping dropdown
		html.Div(className="col-lg-2 col-md-3 col-sm-4 col-xs-6", children=[
			html.Label(
				html.H4("z stepping"),
			),
			dcc.Dropdown(
				id="redshift_step", options=["any", 0.1, 0.01, 0.001, 0.0001],
				value=stepping, placeholder="Any",
			)]),

	]),

	## multiepoch spectra plot
	# dcc.Checklist(
	# 	id="epoch_list",
	# 	labelStyle={"display": "inline-block"}
	# ),

	html.Div(className="row", children=[
		dcc.Graph(
			id="spectra_plot",
			style={
				"position": "relative", "overflow": "hidden",
				"height": "max(450px, min(64vw, 80vh))", "width": "108%", "left": "-4%"},
		),
	]),

	html.Div(className="row", children=[

		## axis range (note: these settings are volatile/auto-resetted)
		html.Div(className="col-lg-2 col-md-3 col-sm-4 col-xs-6", children=[

			## y-axis range
			html.Div(className="row", children=[
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

			## x-axis range
			html.Div(className="row", children=[
				html.Label(
					html.H4("X-axis range"),
				),
				dcc.Input(
					id="axis_x_max", type="number", step=1, value=int(wave_max), placeholder="Max",
					style={"height": "36px", "width": "100%"},
				),
				dcc.Input(
					id="axis_x_min", type="number", step=1, value=int(wave_min), placeholder="Min",
					style={"height": "36px", "width": "100%"},
				)]),

		]),

		## spectral binning
		html.Div(className="col-lg-2 col-md-3 col-sm-4 col-xs-6", children=[
			html.Label(
				html.H4("Binning"),
			),
			dcc.Input(
				id="binning_input", type="number", step=1, min=1, value=binning_default, placeholder="BinValue",
				style={"height": "36px", "width": "100%"}, max=binning_max,
			),
		]),

		## whitespace (not a field)
		html.Div(className="col-sm-8 visible-sm-block", style={"visibility": "hidden"},
                    children=[html.Label(html.H4("-")), dcc.Dropdown()]),
		html.Div(className="col-sm-8 visible-sm-block", style={"visibility": "hidden"},
                    children=[html.Label(html.H4("-")), dcc.Dropdown()]),

		## label spectral lines (emission) (2 columns)
		html.Div(className="col-lg-4 col-md-6 col-sm-8 col-xs-12", children=[
			html.Label(
				html.H4("Emission lines"),
			),
			dcc.Checklist(id="line_list_emi", options=[
				{"label": "{: <12}\t({}Å)".format(i[2], int(float(i[1]))), "value": i[1]} for i in spec_line_emi
			],
				value=list(spec_line_emi[numpy.bool_(spec_line_emi[:, 0]), 1]),
				style={"columnCount": "2"},
				inputStyle={"marginRight": "5px"},
				labelStyle={"whiteSpace": "pre-wrap"},
			),
		]),

		## label spectral lines (absorption) (1 column)
		html.Div(className="col-lg-2 col-md-3 col-sm-4 col-xs-6", children=[
			html.Label(
				html.H4("Absorption lines"),
			),
			dcc.Checklist(id="line_list_abs", options=[
				{"label": "{: <12}\t({}Å)".format(i[2], int(float(i[1]))), "value": i[1]} for i in spec_line_abs
			],
				value=list(spec_line_abs[numpy.bool_(spec_line_abs[:, 0]), 1]),
				style={"columnCount": "1"},
				inputStyle={"marginRight": "5px"},
				labelStyle={"whiteSpace": "pre-wrap"},
			),
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
# ps: `location.search` is cleared when `program` is no longer "(other)"
@app.callback(
	Output("fieldid_input_div", "hidden"),
	Output("catalogid_input_div", "hidden"),
	Output("fieldid_dropdown_div", "hidden"),
	Output("catalogid_dropdown_div", "hidden"),
	Output("window_location", "search"),
	Output("program_dropdown", "value"),
	Output("fieldid_input", "value"),
	Output("catalogid_input", "value"),
	Output("redshift_input", "value", True),
	Output("binning_input", "value", True),
	Output("axis_y_max", "value", True),
	Output("axis_y_min", "value", True),
	Output("axis_x_max", "value", True),
	Output("axis_x_min", "value", True),
	Input("window_location", "search"),
	Input("program_dropdown", "value"),
	Input("window_location", "hash"),
	prevent_initial_call="initial_duplicate")
def set_input_or_dropdown(query, program, hash):
	if query: query = str(query).lstrip("?")
	if program and program != "(other)": query = ""
	fld_mjd, catalog, redshift = "", "", redshift_default
	binning = binning_default
	y_min, y_max = y_min_default, y_max_default
	x_min, x_max = int(wave_min), int(wave_max)
	hash = str(hash).lstrip("#").split("&") if hash else []
	if query and re.fullmatch("\d+-\d+-[^-].+[^-]", query):
		for x in hash:
			if not re.fullmatch("[^=]+=[^=]+", x): continue
			k, v = x.split("=", 1)
			if k == "z": redshift = v
		program = "(other)"
		fld_mjd = "-".join(query.split("-", 2)[:2])
		catalog = "-".join(query.split("-", 2)[2:])
	if query and query != "": query = "?" + query
	ret = query, program, fld_mjd, catalog, redshift, binning, y_min, y_max, x_min, x_max
	if program and program == "(other)":
		return False, False, True, True, *ret
	else:
		return True, True, False, False, *ret

## dropdown menu
@app.callback(
	Output("fieldid_dropdown", "options"),
	Input("program_dropdown", "value"))
def set_fieldid_options(selected_program):
	if not selected_program or selected_program == "(other)": return []
	# print(selected_program) # for testing
	return [{"label": i, "value": i} for i in programs[selected_program]]

@app.callback(
	Output("catalogid_dropdown", "options"),
	Input("fieldid_dropdown", "value"),
	Input("program_dropdown", "value"))
def set_catalogid_options(selected_fieldid, selected_program):
	if not selected_program or selected_program == "(other)": return []
	if not selected_fieldid: return []
	# the following lines are where field numbers are obtained, use strings not numbers
	if selected_fieldid != "all":
		return [{"label": i, "value": str(i)} for i in fieldIDs[str(selected_fieldid)]]
	else:
		return [{"label": i, "value": str(i)} for i in fieldIDs[str(selected_program) + "-" + str(selected_fieldid)]]

# set_fieldid_value is only run when program is switched
@app.callback(
	Output("fieldid_dropdown", "value"),
	Input("fieldid_dropdown", "options"),
	Input("fieldid_input", "value"),
	State("program_dropdown", "value"))
def set_fieldid_value(available_fieldid_options, input, program):
	try:
		if program and program == "(other)": return input or ""
		# print("set_fieldid_value", available_fieldid_options[0]["value"], available_catalogid_options[0]["value"]) # for testing
		# uncomment the following line if you prefer to automatically choose the first field in the program
		# return available_fieldid_options[0]["value"]
		return ""
	except:
		# print("set_fieldid_value except", available_fieldid_options) # for testing
		# print("set_fieldid_value except") # for testing
		return ""

@app.callback(
	Output("catalogid_dropdown", "value"),
	Input("catalogid_dropdown", "options"),
	Input("catalogid_input", "value"),
	State("program_dropdown", "value"))
def set_catalogid_value(available_catalogid_options, input, program):
	try:
		if program and program == "(other)": return input or ""
		# print("set_catalogid_value", available_catalogid_options[0]["value"]) # for testing
		# uncomment the following line if you prefer to automatically choose the first catid in the field
		# return available_catalogid_options[0]["value"]
		return ""
	except:
		# print("set_catalogid_value except", catalogid_dropdown) # for testing
		return ""

# enable/disable stepping for the redshift input (see comment in the beginning of the file)
@app.callback(
	Output("redshift_input", "value"),
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

# reset the axes range and binning value whenever any of program/fieldid/catid changes
@app.callback(
	Output("axis_y_max", "value"),
	Output("axis_y_min", "value"),
	Output("axis_x_max", "value"),
	Output("axis_x_min", "value"),
	Output("binning_input", "value"),
	Input("window_location", "hash"),
	Input("program_dropdown", "value"),
	Input("fieldid_dropdown", "value"),
	Input("catalogid_dropdown", "value"),
	prevent_initial_call=True)
def reset_axis_range(hash, program, *_):
	binning = binning_default
	y_min, y_max = y_min_default, y_max_default
	x_min, x_max = int(wave_min), int(wave_max)
	hash = str(hash).lstrip("#").split("&") if hash else []
	if program and program == "(other)":
		for x in hash:
			if not re.fullmatch("[^=]+=[^=]+", x): continue
			k, v = x.split("=", 1)
			if k == "b": binning = v
			if k == "y" and re.fullmatch("[^,]+,[^,]+", v): y_min, y_max = v.split(",", 1)
			if k == "x" and re.fullmatch("[^,]+,[^,]+", v): x_min, x_max = v.split(",", 1)
	return y_max, y_min, x_max, x_min, binning


## plotting the spectra
@app.callback(
	Output("spectra_plot", "figure"),
	Input("fieldid_dropdown", "value"),
	Input("catalogid_dropdown", "value"),
	Input("redshift_input", "value"), # redshift_dropdown
	Input("axis_y_max", "value"),
	Input("axis_y_min", "value"),
	Input("axis_x_max", "value"),
	Input("axis_x_min", "value"),
	Input("line_list_emi", "value"),
	Input("line_list_abs", "value"),
	Input("binning_input", "value"))
def make_multiepoch_spectra(selected_fieldid, selected_catalogid, redshift,
                            y_max, y_min, x_max, x_min, list_emi, list_abs, binning):
	try:
		binning, redshift = int(binning or binning_default), float(redshift or redshift_default)
		waves, fluxes, names = fetch_catID(selected_fieldid, selected_catalogid)
		# print("make_multiepoch_spectra try") # for testing
	except:
		# print("make_multiepoch_spectra except") # for testing
		return go.Figure()

	if not y_min and not y_max: y_min, y_max = y_min_default, y_max_default
	if not x_min and not x_max: x_min, x_max = int(wave_max), int(wave_min)
	if not y_max: y_max = 0
	if not x_max: x_max = 0
	if not y_min: y_min = 0
	if not x_min: x_min = 0
	if y_max < y_min: y_min, y_max = y_max, y_min
	if x_max < x_min: x_min, x_max = x_max, x_min
	x_max = math.ceil(x_max / (1 + redshift))
	x_min = math.floor(x_min / (1 + redshift))

	fig = go.Figure()
	fig.layout.yaxis.range = [y_min, y_max]
	fig.layout.xaxis.range = [x_min, x_max]

	# print(f"redshift: {redshift}")
	for i in range(0, len(waves)):
		# fig.add_trace(go.Scatter(x=waves[i] / (1 + redshift), y=fluxes[i],
		fig.add_trace(go.Scatter(
			x=waves[i] / (1 + redshift),
			y=convolve(fluxes[i], Box1DKernel(binning)),
			name=names[i], opacity=1 / 2, mode="lines"))

	for i in spec_line_emi:
		j, x = i[2], i[1]
		if x not in list_emi: continue
		x = float(x)
		if (x_min <= x and x <= x_max):
			fig.add_vline(x=x, line_dash="solid", opacity=1 / 3)
			fig.add_annotation(x=x, y=y_max, text=j, hovertext=f" {j} ({x} Å)", textangle=70)

	for i in spec_line_abs:
		j, x = i[2], i[1]
		if x not in list_abs: continue
		x = float(x)
		if (x_min <= x and x <= x_max):
			fig.add_vline(x=x, line_dash="dot", opacity=1 / 2)
			fig.add_annotation(x=x, y=y_min, text=j, hovertext=f" {j} ({x} Å)", textangle=70)

	return fig



if __name__ == "__main__":
	# app.run_server(debug=True)
	app.run_server(host="127.0.0.1", port=8050, debug=True)


