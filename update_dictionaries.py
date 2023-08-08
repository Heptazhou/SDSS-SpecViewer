import json
import os
from concurrent.futures import ThreadPoolExecutor

import numpy as np
from astropy.io import fits

__author__ = "Meg Davis <megan.c.davis@uconn.edu>, Pat Hall <phall@yorku.ca>"
__year__ = "2021-2023"

print("Loading local copy of spAll-lite-*.fits")
try:
	spAll = fits.open("spAll-lite-master.fits")
except:
	spAll = fits.open("spAll-lite-v6_1_0.fits")

CATALOGID = spAll[1].data["CATALOGID"]
FIELD = spAll[1].data["FIELD"]
FIELDQUALITY = spAll[1].data["FIELDQUALITY"]
MJD = spAll[1].data["MJD"]
MJD_FINAL = spAll[1].data["MJD_FINAL"]
OBJTYPE = spAll[1].data["OBJTYPE"]
PROGRAMNAME = spAll[1].data["PROGRAMNAME"]
SPEC1_G = spAll[1].data["SPEC1_G"]
SURVEY = spAll[1].data["SURVEY"]

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

EFEDS1 = \
	(FIELDQUALITY == "good") & (SURVEY == "BHM") & (OBJTYPE == "QSO") & (PROGRAMNAME == "eFEDS1")
EFEDS2 = \
	(FIELDQUALITY == "good") & (SURVEY == "BHM") & (OBJTYPE == "QSO") & (PROGRAMNAME == "eFEDS2")
EFEDS3 = \
	(FIELDQUALITY == "good") & (SURVEY == "BHM") & (OBJTYPE == "QSO") & (PROGRAMNAME == "eFEDS3")
MWM3 = \
	(FIELDQUALITY == "good") & (SURVEY == "BHM") & (OBJTYPE == "QSO") & (PROGRAMNAME == "MWM3")
MWM4 = \
	(FIELDQUALITY == "good") & (SURVEY == "BHM") & (OBJTYPE == "QSO") & (PROGRAMNAME == "MWM4")
AQMESBONUS = \
	(FIELDQUALITY == "good") & (SURVEY == "BHM") & (OBJTYPE == "QSO") & (PROGRAMNAME == "AQMES-Bonus")
AQMESWIDE = \
	(FIELDQUALITY == "good") & (SURVEY == "BHM") & (OBJTYPE == "QSO") & (PROGRAMNAME == "AQMES-Wide")
AQMESMED = \
	(FIELDQUALITY == "good") & (SURVEY == "BHM") & (OBJTYPE == "QSO") & (PROGRAMNAME == "AQMES-Medium")
RMPLATE = \
	(FIELDQUALITY == "good") & (SURVEY == "BHM") & (OBJTYPE == "QSO") & ( (PROGRAMNAME == "RM") | (PROGRAMNAME == "RMv2") | (PROGRAMNAME == "RMv2-fewMWM") )
RMFIBER = \
	(FIELDQUALITY == "good") & (SURVEY == "BHM") & (OBJTYPE == "science") & (PROGRAMNAME == "bhm_rm")
BHMAQMES = \
	(FIELDQUALITY == "good") & (SURVEY == "BHM") & (OBJTYPE == "science") & (PROGRAMNAME == "bhm_aqmes")
BHMCSC = \
	(FIELDQUALITY == "good") & (SURVEY == "BHM") & (OBJTYPE == "science") & (PROGRAMNAME == "bhm_csc")
BHMFILLER = \
	(FIELDQUALITY == "good") & (SURVEY == "BHM") & (OBJTYPE == "science") & (PROGRAMNAME == "bhm_filler")
BHMSPIDERS = \
	(FIELDQUALITY == "good") & (SURVEY == "BHM") & (OBJTYPE == "science") & (PROGRAMNAME == "bhm_spiders")
OPENFIBER = \
	(FIELDQUALITY == "good") & (SURVEY == "open_fiber") & (OBJTYPE == "science") & (PROGRAMNAME == "open_fiber")

eFEDS1_fields = np.unique(FIELD[EFEDS1]).tolist()
eFEDS2_fields = np.unique(FIELD[EFEDS2]).tolist()
eFEDS3_fields = np.unique(FIELD[EFEDS3]).tolist()
MWM3_fields = np.unique(FIELD[MWM3]).tolist()
MWM4_fields = np.unique(FIELD[MWM4]).tolist()
bonus_fields = np.unique(FIELD[AQMESBONUS]).tolist()
wide_fields = np.unique(FIELD[AQMESWIDE]).tolist()
med_fields = np.unique(FIELD[AQMESMED]).tolist()
rmplate_fields = np.unique(FIELD[RMPLATE]).tolist()
rmfiber_fields = np.unique(FIELD[RMFIBER]).tolist()
aqbhm_fields = np.unique(FIELD[BHMAQMES]).tolist()
bhm_csc_fields = np.unique(FIELD[BHMCSC]).tolist()
bhm_filler_fields = np.unique(FIELD[BHMFILLER]).tolist()
bhm_spiders_fields = np.unique(FIELD[BHMSPIDERS]).tolist()
open_fiber_fields = np.unique(FIELD[OPENFIBER]).tolist()

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
	print("\r\x1b[2K", end="")
	print(f"\rProcessing %{n}s/%{n}s ... (%s) " % (1 + i, l, len(programs[j])), end="")
	cats = np.asarray([], np.int64)
	for i in programs[j]:
		if i == "all": continue
		fieldmask = (FIELD == i) & ( (OBJTYPE == "science") | (OBJTYPE == "QSO") ) & (SURVEY == "BHM") & (FIELDQUALITY == "good")
		catIDs = np.unique(CATALOGID[fieldmask])
		cats = np.append(cats, catIDs)
		catIDs = [int(x) for x in catIDs]
		fieldIDs[int(i)] = list(catIDs)
	catIDs = np.unique(cats)
	catIDs = [int(x) for x in catIDs]
	key = "%s-all" % j
	fieldIDs[key] = list(catIDs)
print("\r\x1b[2K\r", end="") # "\e[2K"


print("Building dictionaries from spAll file (can take a while with AQMES or open fiber targets) ...")

def all_mjd_for_cat(cat: str):
	r = []
	for i in np.where(CATALOGID[mask] == cat)[0]:
		v = [int(FIELD[mask][i]), int(MJD[mask][i]), float(SPEC1_G[mask][i]), float(MJD_FINAL[mask][i])]
		r.append(v)
	return r

def pool_map(func, iter, nt: int = min((os.cpu_count() or 8) / 2, 10)):
	nt = int(max(nt or (8 / 2), 2))
	print("Processing %s entries in %s threads ... " % (len(iter), nt))
	with ThreadPoolExecutor( max_workers=nt ) as pool:
		dict = { int(k): v for k, v in zip(iter, pool.map(func, iter)) }
	return dict

# For each unique CATALOGID...
catalogIDs = pool_map(all_mjd_for_cat, np.unique(CATALOGID[mask]))

# Dump list of dictionaries to file
json.dump([programs, fieldIDs, catalogIDs], open("dictionaries.txt", "w"), separators=(",", ":"))

