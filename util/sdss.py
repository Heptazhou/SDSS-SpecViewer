from typing import Union


def SDSSV_buildURL(field: Union[int, str], MJD: int, objID: str, branch: str) -> str:
	"""
	A function to build the url that will be used to fetch the data.
	"""
	path = ""
	try:
		field = int(field)
	except:
		field = 0

	field6 = f"{field}".zfill(6)
	group6 = f"{field // 10**3}XXX".zfill(6)

	file = f"spec-{field}-{MJD}-{objID}.fits"
	file6 = f"spec-{field6}-{MJD}-{objID}.fits"

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
	if branch == "v6_0_4":
		path = "https://data.sdss.org/sas/dr18/spectro/sdss/redux"
	if branch == "v6_0_9" or branch == "v6_1_3":
		path = "https://data.sdss5.org/sas/sdsswork/bhm/boss/spectro/redux"
		file = file6
		field = field6

	if not path:
		path = "https://data.sdss5.org/sas/sdsswork/bhm/boss/spectro/redux"

		url = f"{path}/{branch}/spectra/daily/lite/{group6}/{field6}/{MJD}/{file6}"
	elif branch == "v6_0_4":
		url = f"{path}/{branch}/spectra/lite/{field}p/{MJD}/{file}"
	elif branch == "v6_0_9" or branch == "v6_1_3":
		url = f"{path}/{branch}/spectra/lite/{field}/{MJD}/{file}"
	else:
		url = f"{path}/{branch}/spectra/lite/{field}/{file}"

	return url

