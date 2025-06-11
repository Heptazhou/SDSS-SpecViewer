from re import fullmatch

from .math import signbit
from .unit import deg2dms, deg2hms


def sdss_sas_fits(field: int | str, mjd: int, obj: int | str, branch: str) -> str:
	"""
	A function to build the url that will be used to fetch the data.
	"""
	if not (field and mjd and obj and branch): # pragma: no cover
		raise Exception((field, mjd, obj, branch))
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
		case "26" | "103" | "104":
			path = "https://data.sdss.org/sas/dr18/spectro/sdss/redux"
		case _:
			path = "https://data.sdss5.org/sas/sdsswork/bhm/boss/spectro/redux"

	match branch:
		case v if fullmatch(r"v5_(\d+_\d+)", v) or v in ("26", "103", "104"):
			url = f"{path}/{branch}/spectra/lite/{field4       }/{file(field4, obj04)}"
		case v if fullmatch(r"v6_[0]_[1-4]", v): # v6.0.1 ~ v6.0.4
			url = f"{path}/{branch}/spectra/lite/{field4}p/{mjd}/{file(field4, obj11)}"
		case v if fullmatch(r"v6_[0-1]_\d+", v): # v6.0.6 ~ v6.1.3
			url = f"{path}/{branch}/spectra/lite/{field6 }/{mjd}/{file(field6, obj  )}"
		case _:                                  # v6.2.0+
			url = f"{path}/{branch}/spectra/{daily}/lite/{group}/{field6}/{mjd}/{file(field6, obj)}"

	return url

def sdss_iau(α: float, δ: float) -> str:
	def _str(x: float, tpl="00") -> str:
		return f"{x:+010.6f}"[1:len(tpl) + 1]

	h, m, s = deg2hms(α)
	lon = _str(h) + _str(m) + _str(s, "00.00")

	d, m, s = deg2dms(δ)
	lat = _str(d) + _str(m) + _str(s, "00.0" )

	pm = "-" if signbit(d) else "+"
	return f"SDSS J{lon}{pm}{lat}"

