import dash 
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objects as go
from dash.dependencies import Input, Output
from astropy.io import fits
import requests
import io
import json

###
### input the data directory path 
###

#NOTE TO CODER: JSON LIKES STRING KEYS FOR DICTIONARIES!!!!!!
programs, plateIDs, catalogIDs = json.load(open("dictionaries.txt"))
authen = './authentication.txt'

### css files
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css', \
'//maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css', \
'http://aladin.u-strasbg.fr/AladinLite/api/v2/latest/aladin.min.css', \
'https://use.fontawesome.com/releases/v5.13.0/css/all.css', \
'https://use.fontawesome.com/releases/v5.13.0/css/v4-shims.css', \
]

###
### Any necessary functions
###

def SDSSV_buildURL(plateID, MJD, objID):
    """
    A function to build the url that will be used to fetch the data. 
    
    Catalog IDs don't start with zero but the URL needs it too,
    using zfill(11) fixes this.
    """
    url = "https://data.sdss5.org/sas/sdsswork/bhm/boss/spectro/redux/v6_0_2/" \
    +"spectra/lite/{}p/{}/spec-{}-{}-{}.fits".format(str(plateID), str(MJD), str(plateID), str(MJD), str(objID).zfill(11))
    
    return url

def SDSSV_fetch(username, password, plateID, MJD, objID):
    """
    Fetches spectral data for a SDSS-RM object on a 
       specific plate on a specific MJD. Uses the user
       supplied authentication. 
    
    TO DO: allow for multiple MJDs and plates, for loop it up
    """
    url = SDSSV_buildURL(plateID, MJD, objID)
    r = requests.get(url, auth=(username, password))  
    data_test = fits.open(io.BytesIO(r.content))
    flux = data_test[1].data['FLUX']
    wave = 10**data_test[1].data['loglam']
    return wave, flux 
   
def fetch_catID(catID, plate):
    fluxes = []
    waves = []
    names = []
    for i in catalogIDs[str(catID)]:
        if plate == "all":
            dat = SDSSV_fetch(username, password,i[0], i[1], catID)
            fluxes.append(dat[1])
            waves.append(dat[0])
            names.append(i[3])
        else:
            if i[0] == plate:
                dat = SDSSV_fetch(username, password,i[0], i[1], catID)
                fluxes.append(dat[1])
                waves.append(dat[0])
                names.append(i[3])
            else:
                continue
    return waves, fluxes, names
    
###
### Authentication
###    
try:
    print("Reading authentication file.")
    with open(authen,'r') as i:
        lines = i.readlines()
        username = lines[0][:-1] #there will be a \n on the username
        password = lines[1]
except: #any error from above will fall through to here.
    print("authentication.txt not provided or incomplete. Please enter authentication.")
    username = input("Enter SDSS-V username:")
    password = input("Enter SDSS-V password:") 

try:
    print("Verifying authentication...")
    fetch_test = SDSSV_fetch(username, password, 15173,59281, 4350951054)
    print("Verification successful.")
except:
    print("Authentication error, please cntrl-c and fix authentication.txt.")
    print("Contact Meg (megan.c.davis@uconn.edu) is the issue persists.")
 

    
### important spectra lines to label in plots
spectral_lines = { 'Ha': [6564], 
                   'Hb': [4862],
                   'MgII': [2798],
                   'CIII': [1908],
                   'CIV': [1549],
                   'Lya': [1215],}

### wavelength plotting range
wave_min = 3750
wave_max = 11000

### starting the dash app
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

### get object info
### organize by program, plateid, catalogid
programname = ['SDSS-RM','XMM-LSS','COSMOS','AQMES-Medium','AQMES-Wide']#,'eFEDS1','eFEDS2']



### 
### the webpage layout 
###
app.layout = html.Div(className='container',children=[
    html.H2(children=['SDSSV-BHM Spectra Viewer (remote version)']),

    html.Div([

        ## dropdown menu titles
        html.Div([
            html.H4(children=['Program'])
        ],style={"width": "33%",'display': 'inline-block'}),

        ## plate ID dropdown
        html.Div(children=[
             html.H4(children=['Plate ID'])
        ],style={"width": "33%",'display': 'inline-block'}),

        ## catalog ID dropdown
        html.Div(children=[
             html.H4(children=['Catalog ID'])
        ],style={"width": "33%",'display': 'inline-block'}),

    ]),

    html.Div([

        ## dropdown menu for program/designid/catalogid
        html.Div([
        dcc.Dropdown(
            id='program_dropdown',
            options=[
                {'label': i, 'value': i} for i in programs.keys()],
            placeholder="Program",
            value='SDSS-RM',
            #style={'display': 'inline-block'},
        )],style={"width": "33%",'display': 'inline-block'}),

        ## plate ID dropdown
        html.Div(children=[
        dcc.Dropdown(
            id='plateid_dropdown',
            placeholder='Plate ID',
            #style={'width':'50%','display': 'inline-block'},
        )],style={"width": "33%",'display': 'inline-block'}),


        ## catalog ID dropdown
        html.Div(children=[
        dcc.Dropdown(
            id='catalogid_dropdown',
            placeholder='Catalog ID',
            #style={'width':'50%','display': 'inline-block'},
        )],style={"width": "33%",'display': 'inline-block'}),

    ]),

    ## multiepoch spectra plot
    dcc.Checklist(
        id="epoch_list",
        labelStyle={'display': 'inline-block'}
    ),
    dcc.Graph(id="spectra_plot"),

    html.Div([

    	## spectral binning
        html.Div(children=[
            html.H4(children=['Binning:'])
        ],style={"width": "10%",'display': 'inline-block'}),

        html.Div(children=[
            dcc.Input(id="binning_input", type="number", value=5),
        ],style={"width": "20%",'display': 'inline-block'}), 

        ## label important spectral lines
        html.Div(children=[
            html.H4(children=['Lines:'])
        ],style={"width": "10%",'display': 'inline-block'}),   

        html.Div(children=[
            dcc.Checklist(id="line_list",options=[
                {'label': i+' ('+str(int(spectral_lines[i][0]))+'A)', 'value': i} for i in spectral_lines.keys()
                ], 
                value=list(spectral_lines.keys())),
        ],style={"width": "60%", 'display': 'inline-block'}),    

    ]),
   
    ## TODO: print source information (ra, dec, z, etc...) from some catalog
    html.Div([
    	html.H5(id='property_text')

   	 ])

])


###
### interactive callback functions for updating spectral plot
###

## dropdown menu
@app.callback(
    Output('plateid_dropdown', 'options'),
    Input('program_dropdown', 'value'))
def set_plateid_options(selected_program):
    return [{'label': i, 'value': i} for i in programs[selected_program]]

@app.callback(
    Output('catalogid_dropdown', 'options'),
    Input('plateid_dropdown', 'value'),
    Input('program_dropdown', 'value'))
def set_catalogid_options(selected_designid, selected_program):
    if selected_designid != 'all':
        return [{'label': i, 'value': i} for i in plateIDs[str(selected_designid)]]
    else:
        return [{'label': i, 'value': i} for i in plateIDs[str(selected_program) +"-"+str(selected_designid)]]

@app.callback(
    Output('plateid_dropdown', 'value'),
    Input('plateid_dropdown', 'options'))
def set_plateid_value(available_plateid_options):
    return available_plateid_options[0]['value']

@app.callback(
    Output('catalogid_dropdown', 'value'),
    Input('catalogid_dropdown', 'options'))
def set_catalogid_value(available_catalogid_options):
    return available_catalogid_options[0]['value']


## plotting the spectra
@app.callback(
    Output('spectra_plot','figure'),
    Input('plateid_dropdown', 'value'),
    Input('catalogid_dropdown', 'value'))
def make_multiepoch_spectra(selected_designid, selected_catalogid):
    waves, fluxes, names = fetch_catID(selected_catalogid, selected_designid)

    fig = go.Figure()

    for i in range(0, len(waves)):
        fig.add_trace(go.Scatter(x=waves[i], y=fluxes[i], name=names[i], \
                                 opacity = 1./2., mode='lines'))

        
    return fig

### setting the selected epochs for plotting
# @app.callback(
#     Output('epoch_list','value'),
#     Input('plateid_dropdown', 'value'),
#     Input('catalogid_dropdown', 'value'))
# def set_epoch_value(selected_designid,selected_catalogid):
#     filename = np.array([])
#     for i in plateid[selected_designid]:
#         tmp = glob.glob(dir_spectra+str(i)+'p/coadd/*/spSpec-'+str(i)+'-*-'+str(selected_catalogid).zfill(11)+'.fits')
#         if len(tmp)>0: 
#             filename = np.append(filename,tmp,axis=0)
#     epoch = np.array([])
#     for f in filename:
#         mjd = f.split('/')[-2]
#         plate = f.split('/')[-4][:5]
#         epoch = np.append(epoch,float(plate)+float(mjd)/1e5)
#     return [{'label':i, 'value':i} for i in epoch]

if __name__ == '__main__':
    app.run_server(debug=True)


