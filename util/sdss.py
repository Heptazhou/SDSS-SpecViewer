from re import fullmatch


def SDSSV_buildURL(field: int | str, mjd: int, obj: str, branch: str) -> str:
	"""
	A function to build the url that will be used to fetch the data.
	"""
	if type(field) == str and fullmatch(r"\d+p?", field):
		field = int(field.rstrip("p"))

	if type(field) == int:
		group = f"{field // 1000}XXX".zfill(6)
	else:
		group = f"{field}"
	if fullmatch(r"allepoch_\w+", group):
		group = "allepoch"

	def file(field: str, obj: str) -> str:
		return f"spec-{field}-{mjd}-{obj}.fits"
	field4 = str(field).zfill(4)
	field6 = str(field).zfill(6)

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
			url = f"{path}/{branch}/spectra/lite/{field4}/{file(field4, obj)}"
		case \
			"v6_0_1" | "v6_0_2" | "v6_0_3" | "v6_0_4":
			url = f"{path}/{branch}/spectra/lite/{field4}p/{mjd}/{file(field4, obj)}"
		case \
			"v6_0_6" | "v6_0_7" | "v6_0_8" | "v6_0_9" | \
			"v6_1_0" | "v6_1_1" | "v6_1_2" | "v6_1_3":
			url = f"{path}/{branch}/spectra/lite/{field6}/{mjd}/{file(field6, obj)}"
		case _:
			url = f"{path}/{branch}/spectra/daily/lite/{group}/{field6}/{mjd}/{file(field6, obj)}"
			if group == "allepoch": url \
				= f"{path}/{branch}/spectra/{group}/lite/{group}/{field6}/{mjd}/{file(field6, obj)}"

	return url

