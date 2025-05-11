def link_central(RA: float, DEC: float) -> list[str]:
	"""
	Generate useful object links given RA and DEC.
	"""

	if None in (RA, DEC):
		return []
	if (0 <= RA <= 360) and (-90 <= DEC <= 90):
		link_list = []
	else:
		print(f"[link_central] {(RA, DEC)}")
		return []

	url = f"https://www.legacysurvey.org/viewer?layer=ls-dr10&zoom=16.0&ra={RA}&dec={DEC}&mark={RA},{DEC}"
	link_list.append(f"Legacy Survey Viewer: {url}")

	url = f"https://skyserver.sdss.org/dr18/SkyServerWS/ImgCutout/getjpeg?$ic&ra={RA}&dec={DEC}"
	link_list.append(f"SDSS Image Cutout: {url}")

	url = f"https://skyserver.sdss.org/dr18/VisualTools/navi?scale=0.09&ra={RA}&dec={DEC}"
	link_list.append(f"SDSS Explore Navi: {url}")

	url = f"https://skyserver.sdss.org/dr18/VisualTools/explore/summary?ra={RA}&dec={DEC}"
	link_list.append(f"SDSS Explore Summary: {url}")

	url = f"https://simbad.cds.unistra.fr/simbad/sim-coo?Radius=6.00&Coord={RA}d{DEC}d"
	link_list.append(f"SIMBAD Object Lookup: {url}")

	return link_list

