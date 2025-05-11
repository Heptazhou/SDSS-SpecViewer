from .link import link_central as func


def testset_lon1() -> None:
	assert list(func(360, 0)) != []
	assert list(func(361, 0)) == []

def testset_lon2() -> None:
	assert list(func(-0, +0)) != []
	assert list(func(-1, +0)) == []

def testset_lat1() -> None:
	assert list(func(0, +90)) != []
	assert list(func(0, +91)) == []

def testset_lat2() -> None:
	assert list(func(0, -90)) != []
	assert list(func(0, -91)) == []

