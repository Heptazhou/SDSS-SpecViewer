def link_central(RA: float, DEC: float, ZOOM: int = 16):
	"""
	Generate useful object links given RA, DEC, and zoom level.
	"""

	if None in (RA, DEC, ZOOM):
		return []
	if (0 <= RA <= 360) and (-90 <= DEC <= 90) and (1 <= ZOOM <= 16):
		link_list = []
	else:
		print(f"[link_central] {(RA, DEC, ZOOM)}")
		return []

	legacy_link = f"https://www.legacysurvey.org/viewer?ra={RA}&dec={DEC}&zoom={ZOOM}&mark={RA},{DEC}"
	link_list.append(f"Legacy Survey Viewer: {legacy_link}")

	skyserver_link = f"https://skyserver.sdss.org/dr18/VisualTools/explore/summary?ra={RA}&dec={DEC}"
	link_list.append(f"SDSS Explore Summary: {skyserver_link}")

	simbad_link = f"https://simbad.u-strasbg.fr/simbad/sim-coo?Coord={RA}d{DEC}d&CooFrame=ICRS&CooEpoch=2000&CooEqui=2000&Radius=2&Radius.unit=arcmin&submit=submit+query&CoordList="
	link_list.append(f"SIMBAD Object Lookup: {simbad_link}")

	return link_list

