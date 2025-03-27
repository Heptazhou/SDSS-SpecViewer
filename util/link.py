def link_central(RA, DEC, ZOOM=16):
	""" Generates useful object links given RA, DEC, and zoom level. """

	# Basic error checking
	if not (0 <= RA <= 360):
		return ["Error: RA is out of bounds! Must be between 0 and 360."]

	if not (-90 <= DEC <= 90):
		return ["Error: DEC is out of bounds! Must be between -90 and 90."]

	if not (1 <= ZOOM <= 16):
		return ["Error: ZOOM is out of bounds! Choose between 1 and 16 inclusive."]

	link_list = []

	# Generate the updated Legacy Survey link and add to list
	legacy_link = f"https://www.legacysurvey.org/viewer?ra={RA}&dec={DEC}&zoom={ZOOM}&mark={RA},{DEC}"
	link_list.append(f"Legacy Survey: {legacy_link}")

	# Generate link for SDSS SkyServer
	skyserver_link = f"https://skyserver.sdss.org/dr18/VisualTools/explore/summary?ra={RA}&dec={DEC}"
	link_list.append(f"SDSS SkyServer: {skyserver_link}")

	# Generate link for SIMBAD
	simbad_link = f"https://simbad.u-strasbg.fr/simbad/sim-coo?Coord={RA}d{DEC}d&CooFrame=ICRS&CooEpoch=2000&CooEqui=2000&Radius=2&Radius.unit=arcmin&submit=submit+query&CoordList="
	link_list.append(f"SIMBAD: {simbad_link}")

	return link_list
