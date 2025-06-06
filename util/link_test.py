from .link import object_links as links


def testset_lon1() -> None:
	assert list(links(360, 0)) != []
	assert list(links(361, 0)) == []

def testset_lon2() -> None:
	assert list(links(-0, +0)) != []
	assert list(links(-1, +0)) == []

def testset_lat1() -> None:
	assert list(links(0, +90)) != []
	assert list(links(0, +91)) == []

def testset_lat2() -> None:
	assert list(links(0, -90)) != []
	assert list(links(0, -91)) == []

