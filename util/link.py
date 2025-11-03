from collections.abc import Iterable


def object_links(ra: float, dec: float) -> Iterable[str]:
	"""
	Generate useful object links given RA and DEC.
	"""
	def f(x: dict) -> str:
		return "?" + "&".join(f"{k}={v}" for (k, v) in x.items()) if x else ""

	if None in (ra, dec): # pyright: ignore[reportUnnecessaryContains]
		return # pragma: no cover
	if not (0 <= ra <= 360) or not (-90 <= dec <= 90):
		print(f"[object_links] {(ra, dec)}")
		return

	arg = dict(layer="ls-dr10", zoom="16.0", ra=ra, dec=dec, mark=f"{ra},{dec}")
	url = "https://www.legacysurvey.org/viewer" + f(arg)
	yield f"Legacy Survey Viewer: {url}"

	arg = dict(opt="G", scale="0.0420", width=1280, height=1280, ra=ra, dec=dec)
	url = "https://skyserver.sdss.org/dr19/SkyServerWS/ImgCutout/getjpeg" + f(arg)
	yield f"SDSS Image Cutout: {url}"

	arg = dict(scale="0.09", ra=ra, dec=dec)
	url = "https://skyserver.sdss.org/dr19/VisualTools/navi" + f(arg)
	yield f"SDSS Explore Navi: {url}"

	arg = dict(ra=ra, dec=dec)
	url = "https://skyserver.sdss.org/dr19/VisualTools/explore/summary" + f(arg)
	yield f"SDSS Explore Summary: {url}"

	arg = dict(Radius="6.00", Coord=f"{ra}d{dec}d")
	url = "https://simbad.cds.unistra.fr/simbad/sim-coo" + f(arg)
	yield f"SIMBAD Object Lookup: {url}"

