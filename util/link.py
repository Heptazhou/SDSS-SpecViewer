def object_links(ra: float, dec: float) -> list[str]:
	"""
	Generate useful object links given RA and DEC.
	"""
	def f(v):
		return "?" + "&".join(v)

	link_list: list[str] = []
	if None in (ra, dec):
		return link_list
	if not (0 <= ra <= 360) or not (-90 <= dec <= 90):
		print(f"[object_links] {(ra, dec)}")
		return link_list

	arg = ["layer=ls-dr10", "zoom=16.0", f"ra={ra}", f"dec={dec}", f"mark={ra},{dec}"]
	url = "https://www.legacysurvey.org/viewer" + f(arg)
	link_list.append(f"Legacy Survey Viewer: {url}")

	arg = ["opt=G", "scale=0.0420", "width=1280", "height=1280", f"ra={ra}", f"dec={dec}"]
	url = "https://skyserver.sdss.org/dr18/SkyServerWS/ImgCutout/getjpeg" + f(arg)
	link_list.append(f"SDSS Image Cutout: {url}")

	arg = ["scale=0.09", f"ra={ra}", f"dec={dec}"]
	url = "https://skyserver.sdss.org/dr18/VisualTools/navi" + f(arg)
	link_list.append(f"SDSS Explore Navi: {url}")

	arg = [f"ra={ra}", f"dec={dec}"]
	url = "https://skyserver.sdss.org/dr18/VisualTools/explore/summary" + f(arg)
	link_list.append(f"SDSS Explore Summary: {url}")

	arg = ["Radius=6.00", f"Coord={ra}d{dec}d"]
	url = "https://simbad.cds.unistra.fr/simbad/sim-coo" + f(arg)
	link_list.append(f"SIMBAD Object Lookup: {url}")

	return link_list

