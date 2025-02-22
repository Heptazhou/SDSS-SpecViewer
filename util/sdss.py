from typing import Union


def SDSSV_buildURL(field: Union[int, str], MJD: int, objID: str, branch: str):
	"""
	A function to build the url that will be used to fetch the data.

	Field ID may require leading zero(es),
	use str.zfill(6) to fix it.
	"""
	path = ""
	file = f"spec-%s-{MJD}-{objID}.fits" % str(field).rstrip("p")

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
	if path == "":
		path = "https://data.sdss5.org/sas/sdsswork/bhm/boss/spectro/redux"
		file = f"{MJD}/{file}"

	# prior to v6_2_0
	# url = f"{path}/{branch}/spectra/lite/{field}/{file}"
	# v6_2_0+
	fieldgroup = str(floor(int(field) / 1000)).zfill(3) + "XXX"
	url = f"{path}/{branch}/spectra/daily/lite/{fieldgroup}/{field}/{file}"
	# print(url)
	return url

