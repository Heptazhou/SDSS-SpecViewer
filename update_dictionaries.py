import json
import numpy as np
from astropy.io import fits

__author__ = 'Meg Davis <megan.c.davis@uconn.edu>, Pat Hall <phall@yorku.ca>'
__year__ = "2021-2023"

print("Loading local copy of spAll-lite-v6_1_0.fits")
spAll = fits.open('spAll-lite-v6_1_0.fits')

print("Setting up dictionaries of fieldIDs for each RM_field")
# syntax: programs = {'RM_field':[fieldIDs,...], ...}
programs = {}
programs = {'SDSS-RM': [15171, 15172, 15173, 15290, 16169, 20867, 112359, "all"], 'XMMLSS-RM': [15000, 15002, 23175, 112361, "all"], 'COSMOS-RM': [15038, 15070, 15071, 15252, 15253, 16163, 16164, 16165, 20868, 23288, 112360, "all"]}
# programs = {'SDSS-RM':[15171, 15172, 15173, 15290, 16169, 20867, 112359, "all"]}
# programs = {'XMMLSS-RM':[15000, 15002, 23175, 112361, "all"]}
# programs = {'COSMOS-RM':[15038, 15070, 15071, 15252, 15253, 16163, 16164, 16165, 20868, 23288, 112360, "all"]}

# PROGRAMNAME values with possible quasar targets
# bhm_rm RM RMv2 RMv2-fewMWM
# AQMES-Wide AQMES-Medium bhm_aqmes AQMES-Bonus
# eFEDS3 eFEDS1 eFEDS2 MWM3 MWM4
# bhm_spiders bhm_csc bhm_filler
# open_fiber

print("Sorting out the fields (including the `all` option if instructed to do so)...")

EFEDS1 = (spAll[1].data["SURVEY"] == 'BHM') & (spAll[1].data["PROGRAMNAME"] == 'eFEDS1') & (spAll[1].data["OBJTYPE"] == 'QSO') & (spAll[1].data["FIELDQUALITY"] == 'good')

EFEDS2 = (spAll[1].data["SURVEY"] == 'BHM') & (spAll[1].data["PROGRAMNAME"] == 'eFEDS2') & (spAll[1].data["OBJTYPE"] == 'QSO') & (spAll[1].data["FIELDQUALITY"] == 'good')

EFEDS3 = (spAll[1].data["SURVEY"] == 'BHM') & (spAll[1].data["PROGRAMNAME"] == 'eFEDS3') & (spAll[1].data["OBJTYPE"] == 'QSO') & (spAll[1].data["FIELDQUALITY"] == 'good')

MWM3 = (spAll[1].data["SURVEY"] == 'BHM') & (spAll[1].data["PROGRAMNAME"] == 'MWM3') & (spAll[1].data["OBJTYPE"] == 'QSO') & (spAll[1].data["FIELDQUALITY"] == 'good')

MWM4 = (spAll[1].data["SURVEY"] == 'BHM') & (spAll[1].data["PROGRAMNAME"] == 'MWM4') & (spAll[1].data["OBJTYPE"] == 'QSO') & (spAll[1].data["FIELDQUALITY"] == 'good')

AQMESBONUS = (spAll[1].data["SURVEY"] == 'BHM') & (spAll[1].data["PROGRAMNAME"] == 'AQMES-Bonus') & (spAll[1].data["OBJTYPE"] == 'QSO') & (spAll[1].data["FIELDQUALITY"] == 'good')

AQMESWIDE = (spAll[1].data["SURVEY"] == 'BHM') & (spAll[1].data["PROGRAMNAME"] == 'AQMES-Wide') & (spAll[1].data["OBJTYPE"] == 'QSO') & (spAll[1].data["FIELDQUALITY"] == 'good')

AQMESMED = (spAll[1].data["SURVEY"] == 'BHM') & (spAll[1].data["PROGRAMNAME"] == 'AQMES-Medium') & (spAll[1].data["OBJTYPE"] == 'QSO') & (spAll[1].data["FIELDQUALITY"] == 'good')

RMPLATE = (spAll[1].data["SURVEY"] == 'BHM') & ( (spAll[1].data["PROGRAMNAME"] == 'RM') | (spAll[1].data["PROGRAMNAME"] == 'RMv2') | (spAll[1].data["PROGRAMNAME"] == 'RMv2-fewMWM') ) & (spAll[1].data["OBJTYPE"] == 'QSO') & (spAll[1].data["FIELDQUALITY"] == 'good')

RMFIBER = (spAll[1].data["SURVEY"] == 'BHM') & (spAll[1].data["PROGRAMNAME"] == 'bhm_rm') & (spAll[1].data["OBJTYPE"] == 'science') & (spAll[1].data["FIELDQUALITY"] == 'good')

BHMAQMES = (spAll[1].data["SURVEY"] == 'BHM') & (spAll[1].data["PROGRAMNAME"] == 'bhm_aqmes') & (spAll[1].data["OBJTYPE"] == 'science') & (spAll[1].data["FIELDQUALITY"] == 'good')

BHMCSC = (spAll[1].data["SURVEY"] == 'BHM') & (spAll[1].data["PROGRAMNAME"] == 'bhm_csc') & (spAll[1].data["OBJTYPE"] == 'science') & (spAll[1].data["FIELDQUALITY"] == 'good')

BHMFILLER = (spAll[1].data["SURVEY"] == 'BHM') & (spAll[1].data["PROGRAMNAME"] == 'bhm_filler') & (spAll[1].data["OBJTYPE"] == 'science') & (spAll[1].data["FIELDQUALITY"] == 'good')

BHMSPIDERS = (spAll[1].data["SURVEY"] == 'BHM') & (spAll[1].data["PROGRAMNAME"] == 'bhm_spiders') & (spAll[1].data["OBJTYPE"] == 'science') & (spAll[1].data["FIELDQUALITY"] == 'good')

OPENFIBER = (spAll[1].data["SURVEY"] == 'open_fiber') & (spAll[1].data["PROGRAMNAME"] == 'open_fiber') & (spAll[1].data["OBJTYPE"] == 'science') & (spAll[1].data["FIELDQUALITY"] == 'good')

eFEDS1_fields = np.unique(spAll[1].data["FIELD"][EFEDS1]).tolist()
eFEDS1_fields.append("all")
eFEDS2_fields = np.unique(spAll[1].data["FIELD"][EFEDS2]).tolist()
eFEDS2_fields.append("all")
eFEDS3_fields = np.unique(spAll[1].data["FIELD"][EFEDS3]).tolist()
eFEDS3_fields.append("all")
MWM3_fields = np.unique(spAll[1].data["FIELD"][MWM3]).tolist()
MWM3_fields.append("all")
MWM4_fields = np.unique(spAll[1].data["FIELD"][MWM4]).tolist()
MWM4_fields.append("all")
bonus_fields = np.unique(spAll[1].data["FIELD"][AQMESBONUS]).tolist()
bonus_fields.append("all")
wide_fields = np.unique(spAll[1].data["FIELD"][AQMESWIDE]).tolist()
wide_fields.append("all")
med_fields = np.unique(spAll[1].data["FIELD"][AQMESMED]).tolist()
med_fields.append("all")
rmplate_fields = np.unique(spAll[1].data["FIELD"][RMPLATE]).tolist()
rmplate_fields.append("all")
rmfiber_fields = np.unique(spAll[1].data["FIELD"][RMFIBER]).tolist()
rmfiber_fields.append("all")
aqbhm_fields = np.unique(spAll[1].data["FIELD"][BHMAQMES]).tolist()
aqbhm_fields.append("all")
bhm_csc_fields = np.unique(spAll[1].data["FIELD"][BHMCSC]).tolist()
bhm_csc_fields.append("all")
bhm_filler_fields = np.unique(spAll[1].data["FIELD"][BHMFILLER]).tolist()
bhm_filler_fields.append("all")
bhm_spiders_fields = np.unique(spAll[1].data["FIELD"][BHMSPIDERS]).tolist()
bhm_spiders_fields.append("all")
open_fiber_fields = np.unique(spAll[1].data["FIELD"][OPENFIBER]).tolist()
open_fiber_fields.append("all")

programs['eFEDS1'] = eFEDS1_fields
programs['eFEDS2'] = eFEDS2_fields
programs['eFEDS3'] = eFEDS3_fields
programs['MWM3'] = MWM3_fields
programs['MWM4'] = MWM4_fields
programs['AQMES-Bonus'] = bonus_fields
programs['AQMES-Wide'] = wide_fields
programs['AQMES-Medium'] = med_fields
programs['RM-Plates'] = rmplate_fields
programs['RM-Fibers'] = rmfiber_fields
programs['bhm_aqmes'] = aqbhm_fields
programs['bhm_csc'] = bhm_csc_fields
programs['bhm_filler'] = bhm_filler_fields
programs['bhm_spiders'] = bhm_spiders_fields
programs['open_fiber'] = open_fiber_fields


# Combine all masks
mask_combined = EFEDS1 | EFEDS2 | EFEDS3 | MWM3 | MWM4 | AQMESBONUS | AQMESWIDE | AQMESMED | RMPLATE | RMFIBER | BHMAQMES | BHMCSC | BHMFILLER | BHMSPIDERS | OPENFIBER
mask = mask_combined


# Set up dictionary of field IDs
# syntax: fieldIDs = {'fieldID':[catalogID, ...], ...}
fieldIDs = {}


print("Filling fieldIDs and catalogIDs with only science targets and completed epochs")
# for each program i, find all catalogIDs in the defined fields j first, then search for those catalogIDs in all fields from all programs m
for i in programs.keys():
	for j in programs[i]:
		if j != 'all':
			fieldmask = (spAll[1].data["FIELD"] == j) & ( (spAll[1].data["OBJTYPE"] == 'science') | (spAll[1].data["OBJTYPE"] == 'QSO') ) & (spAll[1].data["SURVEY"] == 'BHM') & (spAll[1].data["FIELDQUALITY"] == 'good')
			catIDs = np.unique(spAll[1].data['CATALOGID'][fieldmask])
			catIDs = [ int(x) for x in catIDs ]
			fieldIDs[int(j)] = list(catIDs)
		else:
			programs[i].remove('all')
			cats = []
			for m in programs[i]:
				fieldmask = (spAll[1].data["FIELD"] == m) & ( (spAll[1].data["OBJTYPE"] == 'science') | (spAll[1].data["OBJTYPE"] == 'QSO') ) & (spAll[1].data["SURVEY"] == 'BHM') & (spAll[1].data["FIELDQUALITY"] == 'good')
				catIDs = np.unique(spAll[1].data['CATALOGID'][fieldmask])
				catIDs = [ int(x) for x in catIDs ]
				cats = np.append(cats, catIDs)
			catIDs = np.unique(cats)
			catIDs = [ int(x) for x in catIDs ]
			key = str(i) + '-all'
			fieldIDs[key] = list(catIDs)
			programs[i].append('all')


print("Building dictionaries from spAll file (can take a while with AQMES or open fiber targets) ...")

catalogIDs = {}

# For each unique CATALOGID...
for k in np.unique(spAll[1].data['CATALOGID'][mask]):
	all_mjds = []
	for m in np.where(spAll[1].data['CATALOGID'][mask] == k)[0]:
		one_mjd = [int(spAll[1].data['FIELD'][mask][m]), int(spAll[1].data['MJD'][mask][m]),
                    float(spAll[1].data['SPEC1_G'][mask][m]), float(spAll[1].data['MJD_FINAL'][mask][m])]
		all_mjds.append(one_mjd)
	# store one catIDs info in dict.
	catalogIDs[int(k)] = all_mjds

# Dump list of dictionaries to file
json.dump([programs, fieldIDs, catalogIDs], open("dictionaries.txt", 'w'))

