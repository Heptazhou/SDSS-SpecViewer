from .link import link_central as func


def testset_lon1() -> None:
	assert func(360, 0) != []
	assert func(361, 0) == []

def testset_lon2() -> None:
	assert func(-0, +0) != []
	assert func(-1, +0) == []

def testset_lat1() -> None:
	assert func(0, +90) != []
	assert func(0, +91) == []

def testset_lat2() -> None:
	assert func(0, -90) != []
	assert func(0, -91) == []

