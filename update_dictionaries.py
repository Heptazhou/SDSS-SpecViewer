import json
import requests
import io
import numpy as np
from astropy.io import fits

__author__ = 'Meg Davis <megan.c.davis@uconn.edu'
__year__ = "2021"

print("total runtime: ~ 5 minutes")

#Loading/getting authentication to fetch the spAll file
authen = './authentication.txt'
try:
    with open(authen,'r') as i:
        lines = i.readlines()
        username = lines[0][:-1]
        password = lines[1]
except: #fails if empty or index out of range
    print("authentication.txt not provided or incomplete. Please enter authentication.")
    username = input("Enter SDSS-V username:")
    password = input("Enter SDSS-V password:")

#Fetching spAll file    
try:
    print("Loading spAll-v6_0_2.fits (approx 2 minutes) ...")
    url = 'https://data.sdss5.org/sas/sdsswork/bhm/boss/spectro/redux/v6_0_2/spAll-v6_0_2.fits'
    r = requests.get(url, auth=(username, password))  
    spAll = fits.open(io.BytesIO(r.content))
    print("loading complete.") ## path to spALL-v6_0_2 (stable) file
except: #fails if the authentication is bad or url is bad!
    print("Authentication error, please ctrl-c and rerun app with correct user and pass. Fix authentication.txt for future runs.")
    print("Contact Meg (megan.c.davis@uconn.edu) is the issue persists.")
    
#Setting up dictionaries

#programs = {'field':[plateIDs,...], ...}
programs = {'SDSS-RM':[15171, 15172, 15173, "all"],'XMM-LSS':[15000, 15002, "all"],
            'COSMOS':[15038, 15070, 15071, 15252, 15253, "all"]}

#Sorting out AQMES plates and adding the "all" option
AQWIDE = (spAll[1].data["PROGRAMNAME"] == 'AQMES-Wide') & (spAll[1].data["OBJTYPE"] == 'QSO')
AQMED = (spAll[1].data["PROGRAMNAME"] == 'AQMES-Medium') & (spAll[1].data["OBJTYPE"] == 'QSO')

wide_plates = np.unique(spAll[1].data["PLATE"][AQWIDE]).tolist()
wide_plates.append("all")

med_plates = np.unique(spAll[1].data["PLATE"][AQMED]).tolist()
med_plates.append("all")

programs['AQMES-Wide'] = wide_plates
programs['AQMES-Medium'] = med_plates

#plateIDs = {'plateID':[catalogID, ...], ...}
plateIDs = {}

#main RM masks
#Just RM and just QSOs
mask1 = (spAll[1].data["PROGRAMNAME"] == 'RM') & (spAll[1].data["OBJTYPE"] == 'QSO')
#Include v2 for COSMOS IDs...
mask2 = (spAll[1].data["PROGRAMNAME"] == 'RMv2') & (spAll[1].data["OBJTYPE"] == 'QSO')
#Either 'RM' or 'RMv2', all QSOs
mask = mask1 | mask2 | AQWIDE | AQMED

#fill plateIDs and catalogIDs
#Only QSOs and completed epochs
for i in programs.keys():
    for j in programs[i]:
        if j != 'all':
            platemask = (spAll[1].data["OBJTYPE"] == 'QSO') & (spAll[1].data["PLATE"] == j)
            catIDs = np.unique(spAll[1].data['CATALOGID'][platemask])
            catIDs = [ int(x) for x in catIDs ]
            plateIDs[int(j)] = list(catIDs)
        else:
            programs[i].remove('all')
            cats = []
            for m in programs[i]:
                platemask = (spAll[1].data["OBJTYPE"] == 'QSO') & (spAll[1].data["PLATE"] == m)
                catIDs = np.unique(spAll[1].data['CATALOGID'][platemask])
                catIDs = [ int(x) for x in catIDs ]
                cats = np.append(cats, catIDs)
            catIDs = np.unique(cats)
            catIDs = [ int(x) for x in catIDs ]
            key = str(i)+'-all'
            plateIDs[key] = list(catIDs)
            programs[i].append('all')


print("building dictionaries from spAll_v6_0_2.fits (approx 12 minutes with AQMES) ...")

#catalogIDs = {'catalogID': [[Plate, MJD, SN2, decMJD],  ...], ...}
catalogIDs = {}

for k in np.unique(spAll[1].data['CATALOGID'][mask]):  
    all_mjds = [] 
    for m in np.where(spAll[1].data['CATALOGID'][mask] == k)[0]:
        one_mjd = [int(spAll[1].data['PLATE'][mask][m]), int(spAll[1].data['MJD'][mask][m]), \
                   float(spAll[1].data['SPEC1_G'][mask][m]), float(spAll[1].data['MJD_FINAL'][mask][m])]
        all_mjds.append(one_mjd)
    #store one catIDs info in dict.    
    catalogIDs[int(k)] = all_mjds

#Dump list of dictionaries to file    
json.dump([programs, plateIDs, catalogIDs], open("dictionaries.txt",'w'))