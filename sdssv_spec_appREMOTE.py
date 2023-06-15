import io
import json
import math
import re

import dash
import plotly.graph_objects as go
import requests
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
# # print(catalogIDs['27021598150201532'])
# print("those were catalogIDs")

# the redshift and stepping to easily adjust redshift using arrow keys or mouse wheel, disabled by default
redshift_default = 0
redshift = None
stepping = None

# global dict to save results of `fetch_catID`, which greatly improves responsiveness after the first plot
cache: dict[tuple, tuple] = {}

# default y-axis range of spectrum plots
y_max_default = 100
y_min_default = -10

### css files
external_stylesheets = [ 'https://codepen.io/chriddyp/pen/bWLwgP.css',
                         'https://maxcdn.bootstrapcdn.com/bootstrap/3.4.1/css/bootstrap.min.css',
                         'https://aladin.u-strasbg.fr/AladinLite/api/v2/latest/aladin.min.css',
                         'https://use.fontawesome.com/releases/v5.15.4/css/all.css',
                         'https://use.fontawesome.com/releases/v5.15.4/css/v4-shims.css', ]

###
### Any necessary functions
###

def SDSSV_buildURL(fieldID, MJD, objID):
	"""
	A function to build the url that will be used to fetch the data.

	Field IDs don't start with zero but the URLs need leading zeroes;
	using zfill(6) fixes this.
	"""
	url = "https://data.sdss5.org/sas/sdsswork/bhm/boss/spectro/redux/v6_1_0/spectra/lite/" \
		+ "{}/{}/spec-{}-{}-{}.fits".format(str(fieldID).zfill(6), MJD, str(fieldID).zfill(6), MJD, objID)
	print(url) # for testing

	return url

def SDSSV_fetch(username, password, fieldID, MJD, objID):
	"""
	Fetches spectral data for a SDSS-RM object on a
		specific field on a specific MJD. Uses the user
		supplied authentication.

	TO DO: allow for multiple MJDs and fields, for loop it up
	"""
	if not (fieldID and MJD and objID):
		raise Exception((fieldID, MJD, objID))
	url = SDSSV_buildURL(fieldID, MJD, objID)
	# print(url) # for testing
	r = requests.get(url, auth=(username, password))
	print(r.status_code)
	if r.status_code >= 400:
		raise Exception(r.status_code)
	data_test = fits.open(io.BytesIO(r.content))
	flux = data_test[1].data['FLUX']
	wave = 10**data_test[1].data['loglam']
	# print(flux) # for testing
	return wave, flux

def fetch_catID(field, catID, redshift):
	# if (redshift > 0):
	# 	print("fetch_catID", field, catID) # for testing
	# 	print(waves)
	# 	return waves, fluxes, names
	# print("fetch_catID", field, catID) # for testing
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
		dat = SDSSV_fetch(username, password, fld, mjd, catID)
		fluxes.append(dat[1])
		waves.append(dat[0])
		names.append(mjd)
	else:
		for i in catalogIDs[str(catID)]:
			if field == "all":
				# print(i[0], i[1], catID) # for testing
				dat = SDSSV_fetch(username, password, i[0], i[1], catID)
				fluxes.append(dat[1])
				waves.append(dat[0])
				names.append(i[3])
			else:
				if i[0] == field:
					dat = SDSSV_fetch(username, password, i[0], i[1], catID)
					fluxes.append(dat[1])
					waves.append(dat[0])
					names.append(i[3])
	# print(fluxes) # for testing
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
	print("Authentication error, please ctrl-c and fix authentication.txt.")
	# print("Contact Meg (megan.c.davis@uconn.edu) if the issue persists.")



### important spectra lines to label in plots
spectral_lines = { "H α": [6564],
                   "H β": [4862],
                   "Mg II": [2798],
                   "C III ]": [1908],
                   "C IV": [1549],
                   "Ly α": [1215], }

### wavelength plotting range
wave_min = 3500.
wave_max = 10500.

### starting the dash app
app = dash.Dash(__name__, external_stylesheets=external_stylesheets,
                title="SpecViewer", update_title="Loading...")

### get object info
### organize by program, fieldid, catalogid
# programname = ['COSMOS']
# programname = ['AQMES-Medium', 'AQMES-Wide', 'AQMES-Bonus', 'bhm_aqmes']
# programname = ['SDSS-RM', 'XMM-LSS', 'COSMOS', 'AQMES-Medium', 'AQMES-Wide'] # , 'eFEDS1', 'eFEDS2']



###
### the webpage layout
###

# see https://getbootstrap.com/docs/3.4/css/#grid
app.layout = html.Div(className="container-fluid", style={"width": "90%"}, children=[
	html.Div(className="row", children=[
		html.H2("SDSSV-BHM Spectra Viewer (remote version)"),
	]),

	html.Div(className="row", children=[

		## dropdown menu for program/designid/catalogid
		html.Div(className="col-lg-2 col-md-3 col-sm-4 col-xs-6", children=[
			html.Label(
				html.H4("Program"),
			),
			dcc.Dropdown(
				id='program_dropdown',
				options=[
					{"label": i, "value": i} for i in [*programs.keys(), "(other)"]],
				placeholder="Program",
			)]),

		## Field ID input
		html.Div(className="col-lg-2 col-md-3 col-sm-4 col-xs-6", children=[
			html.Label(
				html.H4("Field & MJD"),
			),
			dcc.Input(
				id="fieldid_input", type="text",
				placeholder="FieldID-MJD", style={"height": "36px", "width": "100%"},
			)], id="fieldid_input_div", hidden=True),

		## Field ID dropdown
		html.Div(className="col-lg-2 col-md-3 col-sm-4 col-xs-6", children=[
			html.Label(
				html.H4("Field ID"),
			),
			dcc.Dropdown(
				id="fieldid_dropdown",
				placeholder="FieldID",
			)], id="fieldid_dropdown_div", hidden=False),

		## catalog ID input
		html.Div(className="col-lg-4 col-md-6 col-sm-8 col-xs-12", children=[
			html.Label(
				html.H4("Catalog ID"),
			),
			dcc.Input(
				id="catalogid_input", type="text",
				placeholder="CatalogID", style={"height": "36px", "width": "100%"},
			)], id="catalogid_input_div", hidden=True),

		## catalog ID dropdown
		html.Div(className="col-lg-4 col-md-6 col-sm-8 col-xs-12", children=[
			html.Label(
				html.H4("Catalog ID"),
			),
			dcc.Dropdown(
				id="catalogid_dropdown",
				placeholder="CatalogID",
			)], id="catalogid_dropdown_div", hidden=False),

		## whitespace (NOT A FIELD)
		html.Div(className="col-sm-4 visible-sm-block", style={"visibility": "hidden"},
                    children=[html.Label(html.H4("-")), dcc.Dropdown()]),

		## redshift input
		html.Div(className="col-lg-2 col-md-3 col-sm-4 col-xs-6", children=[
			html.Label(
				html.H4("Redshift (z)"),
			),
			dcc.Input(
				id='redshift_input', # redshift_dropdown
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
	# 	labelStyle={'display': 'inline-block'}
	# ),

	html.Div(className="row", children=[
		dcc.Graph(id="spectra_plot"),
	]),

	html.Div(className="row", children=[

		## y-axis range
		html.Div(className="col-lg-2 col-md-3 col-sm-4 col-xs-6", children=[
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
			),
		]),

		## spectral binning
		html.Div(className="col-lg-2 col-md-3 col-sm-4 col-xs-6", children=[
			html.Label(
				html.H4("Binning"),
			),
			dcc.Input(
				id="binning_input", type="number", step=1, min=1, value=1,
				style={"height": "36px", "width": "100%"},
			),
		]),

		## label important spectral lines
		html.Div(className="col-lg-2 col-md-3 col-sm-4 col-xs-6", children=[
			html.Label(
				html.H4("Lines"),
			),
			dcc.Checklist(id="line_list", options=[
				{"label": i + " \t (" + str(int(spectral_lines[i][0])) + "Å)", "value": i} for i in spectral_lines.keys()
			],
				value=list(spectral_lines.keys()),
				inputStyle={"marginRight": "5px"},
				labelStyle={"whiteSpace": "pre-wrap"},
			),
		]),

		# ## user-adjustable redshift
		# html.Div(children=[
		# 	html.H4(children=['Redshift:'])
		# ], style={"width": "10%", 'display': 'inline-block'}),
		#
		# html.Div(children=[
		#             dcc.Textarea(
		#                 id='user_redshift',
		#                 value='0'
		#             ),
		#             html.Button('Submit', id='user_redshift_button', n_clicks=0),
		#             html.Div(id='user_redshift_output', style={'whiteSpace': 'pre-line'})
		# ], style={"width": "30%", 'display': 'inline-block'}),

	]),

	## TODO: print source information (ra, dec, z, etc...) from some catalog
	# html.Div([
	# 	html.H5(id='property_text')
	# ])

])


###
### interactive callback functions for updating spectral plot
###

### redshift
# @app.callback(
# 	Output('user_redshift_output', 'value'), # , 'children'),
# 	Input('user_redshift_button', 'n_clicks'),
# 	State('user_redshift', 'value')
# )
# def update_redshift(n_clicks, user_redshift):
# 	if n_clicks > 0:
# 		redshift = user_redshift
# 		print("redshift is ", redshift)
# 		return redshift

## input manually
@app.callback(
	Output("fieldid_input_div", "hidden"),
	Output("catalogid_input_div", "hidden"),
	Output("fieldid_dropdown_div", "hidden"),
	Output("catalogid_dropdown_div", "hidden"),
	Output("fieldid_input", "value"),
	Output("catalogid_input", "value"),
	Input("program_dropdown", "value"))
def set_input_or_dropdown(program):
	if program and program == "(other)":
		return False, False, True, True, None, None
	else:
		return True, True, False, False, None, None

## dropdown menu
@app.callback(
	Output('fieldid_dropdown', 'options'),
	Input('program_dropdown', 'value'))
def set_fieldid_options(selected_program):
	if not selected_program or selected_program == "(other)": return []
	return [{'label': i, 'value': i} for i in programs[selected_program]]

@app.callback(
	Output('catalogid_dropdown', 'options'),
	Input('fieldid_dropdown', 'value'),
	Input('program_dropdown', 'value'))
def set_catalogid_options(selected_designid, selected_program):
	if not selected_program or selected_program == "(other)": return []
	if not selected_designid: return []
	if selected_designid != 'all':
		return [{'label': i, 'value': i} for i in fieldIDs[str(selected_designid)]]
	else:
		return [{'label': i, 'value': i} for i in fieldIDs[str(selected_program) + "-" + str(selected_designid)]]

@app.callback(
	Output('fieldid_dropdown', 'value'),
	Input('fieldid_dropdown', 'options'),
	Input('fieldid_input', 'value'),
	State('program_dropdown', 'value'))
def set_fieldid_value(available_fieldid_options, input, program):
	try:
		if program == "(other)": return input
		# print("set_fieldid_value", available_fieldid_options[0]['value']) # for testing
		return available_fieldid_options[0]['value']
	except:
		return

@app.callback(
	Output('catalogid_dropdown', 'value'),
	Input('catalogid_dropdown', 'options'),
	Input('catalogid_input', 'value'),
	State('program_dropdown', 'value'))
def set_catalogid_value(available_catalogid_options, input, program):
	try:
		if program == "(other)": return input
		# print("set_catalogid_value", available_catalogid_options[0]['value']) # for testing
		return available_catalogid_options[0]['value']
	except:
		return

@app.callback(
	Output("redshift_input", "value"),
	Output("redshift_input", "type"),
	Output("redshift_input", "step"),
	State("redshift_input", "value"),
	Input("redshift_step", "value"))
def set_redshift_stepping(z, step):
	if not step: step = "any"
	if str(step).lower() == "any":
		type = "text"
	else:
		type = "number"
	if type == "number" and z:
		z = f"%0.{-int(math.log10(step))}f" % float(z)
	return z, type, step


## plotting the spectra
@app.callback(
	Output('spectra_plot', 'figure'),
	Input('fieldid_dropdown', 'value'),
	Input('catalogid_dropdown', 'value'),
	Input('redshift_input', 'value'), # redshift_dropdown
	Input('axis_y_max', 'value'),
	Input('axis_y_min', 'value'),
	State('spectra_plot', 'figure'))
def make_multiepoch_spectra(selected_designid, selected_catalogid, redshift, y_max, y_min, fig):
	try:
		if not redshift: redshift = redshift_default
		waves, fluxes, names = fetch_catID(selected_designid, selected_catalogid, redshift)
		redshift = float(redshift)
	except:
		return go.Figure()

	if not y_max and not y_min: return fig
	if not y_max: y_max = 0
	if not y_min: y_min = 0
	if y_max < y_min: y_min, y_max = y_max, y_min
	x_min = math.floor(wave_min / (1 + redshift))
	x_max = math.ceil(wave_max / (1 + redshift))

	fig = go.Figure()
	fig.layout.xaxis.range = [x_min, x_max]
	fig.layout.yaxis.range = [y_min, y_max]

	print(redshift)
	for i in range(0, len(waves)):
		fig.add_trace(go.Scatter(x=waves[i] / (1 + redshift), y=fluxes[i], name=names[i],
                           opacity=1. / 2., mode='lines'))

	for j in spectral_lines.keys():
		if (spectral_lines[j][0] >= x_min and spectral_lines[j][0] <= x_max):
			xj = [ spectral_lines[j][0], spectral_lines[j][0] ]
			yj = [ y_min, y_max ]
			# print(xj, yj) # for testing
			fig.add_trace(go.Scatter(x=xj, y=yj, opacity=1. / 2., name=j, mode='lines')) # , line=go.scatter.Line(color="black")))

	return fig


# https://dash.plotly.com/basic-callbacks



### changing just the redshift
# @app.callback(
# 	Output('spectra_plot', 'figure'),
# 	Input('redshift_dropdown', 'value'))
# def adjust_redshift_spectra(redshift):
#
# 	fig = go.Figure()
# 	fig.layout.xaxis.range = [wave_min / (1 + redshift), wave_max / (1 + redshift)]
# 	fig.layout.yaxis.range = [y_min, y_max]
#
# 	for i in range(0, len(waves)):
# 		fig.add_trace(go.Scatter(x=waves[i] / (1 + redshift), y=fluxes[i], name=names[i],
#                            opacity=1. / 2., mode='lines'))
#
# 	for j in spectral_lines.keys():
# 		if (spectral_lines[j][0] >= wave_min / (1 + redshift) and spectral_lines[j][0] <= wave_max / (1 + redshift)):
# 			xj = [ spectral_lines[j][0], spectral_lines[j][0] ]
# 			yj = [ y_min, y_max ]
# 			print(xj, yj)
# 			fig.add_trace(go.Scatter(x=xj, y=yj, opacity=1. / 2., name=j, mode='lines')) # , line=go.scatter.Line(color="black")))
#
# 	return fig


### setting the selected epochs for plotting
# @app.callback(
# 	Output('epoch_list', 'value'),
# 	Input('fieldid_dropdown', 'value'),
# 	Input('catalogid_dropdown', 'value'))
# def set_epoch_value(selected_designid, selected_catalogid):
# 	filename = np.array([])
# 	for i in fieldid[selected_designid]:
# 		tmp = glob.glob(dir_spectra + str(i) + 'p/coadd/*/spSpec-' + str(i) + '-*-' + str(selected_catalogid).zfill(11) + '.fits')
# 		if len(tmp) > 0:
# 			filename = np.append(filename, tmp, axis=0)
# 	epoch = np.array([])
# 	for f in filename:
# 		mjd = f.split('/')[-2]
# 		field = f.split('/')[-4][:5]
# 		epoch = np.append(epoch, float(field) + float(mjd) / 1e5)
# 	return [{'label': i, 'value': i} for i in epoch]


if __name__ == '__main__':
	# app.run_server(debug=True)
	app.run_server(host='127.0.0.1', port=8050, debug=True)


