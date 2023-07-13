import json

import numpy as np
from astropy.io import fits

__author__ = "Meg Davis <megan.c.davis@uconn.edu>, Pat Hall <phall@yorku.ca>"
__year__ = "2021-2023"

print("Loading local copy of spAll-lite-*.fits")
try:
	spAll = fits.open("spAll-lite-master.fits")
except:
	spAll = fits.open("spAll-lite-v6_1_0.fits")
finally:
	data1 = spAll[1].data

print("Setting up dictionaries of fieldIDs for each RM_field")
# syntax: programs = {"RM_field":[fieldIDs,...], ...}
programs = {}
programs = {"SDSS-RM": [15171, 15172, 15173, 15290, 16169, 20867, 112359, "all"], "XMMLSS-RM": [15000, 15002, 23175, 112361, "all"], "COSMOS-RM": [15038, 15070, 15071, 15252, 15253, 16163, 16164, 16165, 20868, 23288, 112360, "all"]}
# programs = {"SDSS-RM":[15171, 15172, 15173, 15290, 16169, 20867, 112359, "all"]}
# programs = {"XMMLSS-RM":[15000, 15002, 23175, 112361, "all"]}
# programs = {"COSMOS-RM":[15038, 15070, 15071, 15252, 15253, 16163, 16164, 16165, 20868, 23288, 112360, "all"]}

# PROGRAMNAME values with possible quasar targets
# bhm_rm RM RMv2 RMv2-fewMWM
# AQMES-Wide AQMES-Medium bhm_aqmes AQMES-Bonus
# eFEDS3 eFEDS1 eFEDS2 MWM3 MWM4
# bhm_spiders bhm_csc bhm_filler
# open_fiber

print("Sorting out the fields (including the `all` option if instructed to do so) ...")

EFEDS1 = (data1["SURVEY"] == "BHM") & (data1["PROGRAMNAME"] == "eFEDS1") & (data1["OBJTYPE"] == "QSO") & (data1["FIELDQUALITY"] == "good")

EFEDS2 = (data1["SURVEY"] == "BHM") & (data1["PROGRAMNAME"] == "eFEDS2") & (data1["OBJTYPE"] == "QSO") & (data1["FIELDQUALITY"] == "good")

EFEDS3 = (data1["SURVEY"] == "BHM") & (data1["PROGRAMNAME"] == "eFEDS3") & (data1["OBJTYPE"] == "QSO") & (data1["FIELDQUALITY"] == "good")

MWM3 = (data1["SURVEY"] == "BHM") & (data1["PROGRAMNAME"] == "MWM3") & (data1["OBJTYPE"] == "QSO") & (data1["FIELDQUALITY"] == "good")

MWM4 = (data1["SURVEY"] == "BHM") & (data1["PROGRAMNAME"] == "MWM4") & (data1["OBJTYPE"] == "QSO") & (data1["FIELDQUALITY"] == "good")

AQMESBONUS = (data1["SURVEY"] == "BHM") & (data1["PROGRAMNAME"] == "AQMES-Bonus") & (data1["OBJTYPE"] == "QSO") & (data1["FIELDQUALITY"] == "good")

AQMESWIDE = (data1["SURVEY"] == "BHM") & (data1["PROGRAMNAME"] == "AQMES-Wide") & (data1["OBJTYPE"] == "QSO") & (data1["FIELDQUALITY"] == "good")

AQMESMED = (data1["SURVEY"] == "BHM") & (data1["PROGRAMNAME"] == "AQMES-Medium") & (data1["OBJTYPE"] == "QSO") & (data1["FIELDQUALITY"] == "good")

RMPLATE = (data1["SURVEY"] == "BHM") & ( (data1["PROGRAMNAME"] == "RM") | (data1["PROGRAMNAME"] == "RMv2") | (data1["PROGRAMNAME"] == "RMv2-fewMWM") ) & (data1["OBJTYPE"] == "QSO") & (data1["FIELDQUALITY"] == "good")

RMFIBER = (data1["SURVEY"] == "BHM") & (data1["PROGRAMNAME"] == "bhm_rm") & (data1["OBJTYPE"] == "science") & (data1["FIELDQUALITY"] == "good")

BHMAQMES = (data1["SURVEY"] == "BHM") & (data1["PROGRAMNAME"] == "bhm_aqmes") & (data1["OBJTYPE"] == "science") & (data1["FIELDQUALITY"] == "good")

BHMCSC = (data1["SURVEY"] == "BHM") & (data1["PROGRAMNAME"] == "bhm_csc") & (data1["OBJTYPE"] == "science") & (data1["FIELDQUALITY"] == "good")

BHMFILLER = (data1["SURVEY"] == "BHM") & (data1["PROGRAMNAME"] == "bhm_filler") & (data1["OBJTYPE"] == "science") & (data1["FIELDQUALITY"] == "good")

BHMSPIDERS = (data1["SURVEY"] == "BHM") & (data1["PROGRAMNAME"] == "bhm_spiders") & (data1["OBJTYPE"] == "science") & (data1["FIELDQUALITY"] == "good")

OPENFIBER = (data1["SURVEY"] == "open_fiber") & (data1["PROGRAMNAME"] == "open_fiber") & (data1["OBJTYPE"] == "science") & (data1["FIELDQUALITY"] == "good")

eFEDS1_fields = np.unique(data1["FIELD"][EFEDS1]).tolist()
eFEDS2_fields = np.unique(data1["FIELD"][EFEDS2]).tolist()
eFEDS3_fields = np.unique(data1["FIELD"][EFEDS3]).tolist()
MWM3_fields = np.unique(data1["FIELD"][MWM3]).tolist()
MWM4_fields = np.unique(data1["FIELD"][MWM4]).tolist()
bonus_fields = np.unique(data1["FIELD"][AQMESBONUS]).tolist()
wide_fields = np.unique(data1["FIELD"][AQMESWIDE]).tolist()
med_fields = np.unique(data1["FIELD"][AQMESMED]).tolist()
rmplate_fields = np.unique(data1["FIELD"][RMPLATE]).tolist()
rmfiber_fields = np.unique(data1["FIELD"][RMFIBER]).tolist()
aqbhm_fields = np.unique(data1["FIELD"][BHMAQMES]).tolist()
bhm_csc_fields = np.unique(data1["FIELD"][BHMCSC]).tolist()
bhm_filler_fields = np.unique(data1["FIELD"][BHMFILLER]).tolist()
bhm_spiders_fields = np.unique(data1["FIELD"][BHMSPIDERS]).tolist()
open_fiber_fields = np.unique(data1["FIELD"][OPENFIBER]).tolist()

programs["eFEDS1"] = eFEDS1_fields + ["all"]
programs["eFEDS2"] = eFEDS2_fields + ["all"]
programs["eFEDS3"] = eFEDS3_fields + ["all"]
programs["MWM3"] = MWM3_fields + ["all"]
programs["MWM4"] = MWM4_fields + ["all"]
programs["AQMES-Bonus"] = bonus_fields + ["all"]
programs["AQMES-Wide"] = wide_fields + ["all"]
programs["AQMES-Medium"] = med_fields + ["all"]
programs["RM-Plates"] = rmplate_fields + ["all"]
programs["RM-Fibers"] = rmfiber_fields + ["all"]
programs["bhm_aqmes"] = aqbhm_fields + ["all"]
programs["bhm_csc"] = bhm_csc_fields + ["all"]
programs["bhm_filler"] = bhm_filler_fields + ["all"]
programs["bhm_spiders"] = bhm_spiders_fields + ["all"]
programs["open_fiber"] = open_fiber_fields + ["all"]


# Combine all masks
mask = EFEDS1 | EFEDS2 | EFEDS3 | MWM3 | MWM4 | AQMESBONUS | AQMESWIDE | AQMESMED | RMPLATE | RMFIBER | BHMAQMES | BHMCSC | BHMFILLER | BHMSPIDERS | OPENFIBER


# Set up dictionary of field IDs
# syntax: fieldIDs = {"fieldID":[catalogID, ...], ...}
fieldIDs = {}


print("Filling fieldIDs and catalogIDs with only science targets and completed epochs")
# for each program j, find all catalogIDs in the defined fields k first, then search for those catalogIDs in all fields from all programs m
l = len(programs.keys())
n = len(str(l))
for i, j in enumerate(programs.keys()):
	print(f"\rProcessing %{n}s/%{n}s ..." % (1 + i, l), end="")
	for k in programs[j]:
		if k != "all":
			fieldmask = (data1["FIELD"] == k) & ( (data1["OBJTYPE"] == "science") | (data1["OBJTYPE"] == "QSO") ) & (data1["SURVEY"] == "BHM") & (data1["FIELDQUALITY"] == "good")
			catIDs = np.unique(data1["CATALOGID"][fieldmask])
			catIDs = [ int(x) for x in catIDs ]
			fieldIDs[int(k)] = list(catIDs)
		else:
			programs[j].remove("all")
			cats = []
			for m in programs[j]:
				fieldmask = (data1["FIELD"] == m) & ( (data1["OBJTYPE"] == "science") | (data1["OBJTYPE"] == "QSO") ) & (data1["SURVEY"] == "BHM") & (data1["FIELDQUALITY"] == "good")
				catIDs = np.unique(data1["CATALOGID"][fieldmask])
				catIDs = [ int(x) for x in catIDs ]
				cats = np.append(cats, catIDs)
			catIDs = np.unique(cats)
			catIDs = [ int(x) for x in catIDs ]
			key = str(j) + "-all"
			fieldIDs[key] = list(catIDs)
			programs[j].append("all")
print()


print("Building dictionaries from spAll file (can take a while with AQMES or open fiber targets) ...")

catalogIDs = {}

# For each unique CATALOGID...
all_cat = np.unique(data1["CATALOGID"][mask])
num_cat = len(all_cat)
max_dgt = len("%i" % num_cat)
for j, k in enumerate(all_cat):
	print(f"\rProcessing %{max_dgt}s/%{max_dgt}s ..." % (1 + j, num_cat), end="")
	all_mjd = []
	for m in np.where(data1["CATALOGID"][mask] == k)[0]:
		one_mjd = [int(data1["FIELD"][mask][m]), int(data1["MJD"][mask][m]),
                    float(data1["SPEC1_G"][mask][m]), float(data1["MJD_FINAL"][mask][m])]
		all_mjd.append(one_mjd)
	# store one catIDs info in dict.
	catalogIDs[int(k)] = all_mjd
print()

# Dump list of dictionaries to file
json.dump([programs, fieldIDs, catalogIDs], open("dictionaries.txt", "w"), separators=(",", ":"))

