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

	match branch:
		case "v5_4_45":
			path = "https://data.sdss.org/sas/dr9/sdss/spectro/redux"
		case "v5_5_12":
			path = "https://data.sdss.org/sas/dr10/sdss/spectro/redux"
		case "v5_6_5":
			path = "https://data.sdss.org/sas/dr11/sdss/spectro/redux"
		case "v5_7_0" | "v5_7_2":
			path = "https://data.sdss.org/sas/dr12/sdss/spectro/redux"
		case "v5_9_0":
			path = "https://data.sdss.org/sas/dr13/sdss/spectro/redux"
		case "v5_10_0":
			path = "https://data.sdss.org/sas/dr15/sdss/spectro/redux"
		case "v5_13_0":
			path = "https://data.sdss.org/sas/dr16/sdss/spectro/redux"
		case "v5_13_2" | "v6_0_4":
			path = "https://data.sdss.org/sas/dr18/spectro/sdss/redux"
		case _:
			path = "https://data.sdss5.org/sas/sdsswork/bhm/boss/spectro/redux"

	match branch:
		case \
			"v5_4_45" | "v5_5_12" | "v5_6_5" | "v5_7_0" | "v5_7_2" | "v5_9_0" | \
			"v5_10_0" | "v5_13_0" | "v5_13_2":
			url = f"{path}/{branch}/spectra/lite/{field}/{file}"
		case \
			"v6_0_1" | "v6_0_2" | "v6_0_3" | "v6_0_4":
			url = f"{path}/{branch}/spectra/lite/{field}p/{MJD}/{file}"
		case \
			"v6_0_6" | "v6_0_7" | "v6_0_8" | "v6_0_9" | \
			"v6_1_0" | "v6_1_1" | "v6_1_2" | "v6_1_3":
			url = f"{path}/{branch}/spectra/lite/{field6}/{MJD}/{file6}"
		case _:
			url = f"{path}/{branch}/spectra/daily/lite/{group6}/{field6}/{MJD}/{file6}"

	return url

