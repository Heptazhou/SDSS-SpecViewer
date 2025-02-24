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
		case branch if fullmatch(r"v5_(\d+_\d+)", branch):
			url = f"{path}/{branch}/spectra/lite/{field4       }/{file(field4, obj04)}"
		case branch if fullmatch(r"v6_[0]_[1-4]", branch):
			url = f"{path}/{branch}/spectra/lite/{field4}p/{mjd}/{file(field4, obj11)}"
		case branch if fullmatch(r"v6_[0-1]_\d+", branch):
			url = f"{path}/{branch}/spectra/lite/{field6 }/{mjd}/{file(field6, obj  )}"
		case _:
			url = f"{path}/{branch}/spectra/{daily}/lite/{group}/{field6}/{mjd}/{file(field6, obj)}"

	return url

