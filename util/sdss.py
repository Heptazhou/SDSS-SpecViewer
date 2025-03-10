from re import fullmatch


def SDSSV_buildURL(field: int | str, mjd: int, obj: int | str, branch: str) -> str:
	"""
	A function to build the url that will be used to fetch the data.
	"""
	if not (field and mjd and obj and branch):
		raise Exception()
	if type(field) == str and fullmatch(r"\d+p?", field):
		field = int(field.rstrip("p"))

	if type(field) == int:
		group = f"{field // 1000}XXX".zfill(6)
	else:
		group = f"{field}"
	if fullmatch(r"allepoch_\w+", group):
		daily = group = "allepoch"
	else:
		daily = "daily"

	def file(field: str, obj: int | str) -> str:
		return f"spec-{field}-{mjd}-{obj}.fits"
	field4 = str(field).zfill(4)
	field6 = str(field).zfill(6)
	obj04 = str(obj).zfill( 4)
	obj11 = str(obj).zfill(11)

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
		case branch if fullmatch(r"v5_(\d+_\d+)", branch): # v5
			url = f"{path}/{branch}/spectra/lite/{field4       }/{file(field4, obj04)}"
		case branch if fullmatch(r"v6_[0]_[1-4]", branch): # v6.0.1 ~ v6.0.4
			url = f"{path}/{branch}/spectra/lite/{field4}p/{mjd}/{file(field4, obj11)}"
		case branch if fullmatch(r"v6_[0-1]_\d+", branch): # v6.0.6 ~ v6.1.3
			url = f"{path}/{branch}/spectra/lite/{field6 }/{mjd}/{file(field6, obj  )}"
		case _:                                            # v6.2.0+
			url = f"{path}/{branch}/spectra/{daily}/lite/{group}/{field6}/{mjd}/{file(field6, obj)}"

	return url


def SDSS_buildURL(plate: int | str, mjd: int | str, fiber: int | str, branch: str) -> str:
	"""
	A function to build the url that will be used to fetch data from SDSS-I/II.
	"""
	if not (plate and mjd and fiber):
		raise Exception()

	# Fiber string is four digits; pad with leading zeros if needed
	plate4 = str(plate).zfill(4)
	fiber4 = str(fiber).zfill(4)

	# PBH: the three different possible SDSS paths have nothing to do with their branch names;
	# but using them is an easy way to try all three SDSS paths in the SDSSV_fetch function.
	# Both data.sdss.org and dr18.sdss.org work as of March 2025.
	match branch:
		case "master":
			path = "https://data.sdss.org/sas/dr18/spectro/sdss/redux/26/spectra/lite"
		case "v6_2_0":
			path = "https://data.sdss.org/sas/dr18/spectro/sdss/redux/103/spectra/lite"
		case "v6_1_3":
			path = "https://data.sdss.org/sas/dr18/spectro/sdss/redux/104/spectra/lite"
		case _:
			path = "https://dr18.sdss.org/sas/dr18/spectro/sdss/redux/26/spectra/lite"

	url = f"{path}/{plate4}/spec-{plate4}-{mjd}-{fiber4}.fits"

	return url

