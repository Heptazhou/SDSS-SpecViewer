from .math import signbit
from .unit import deg2dms, deg2hms


def testset_deg0() -> None:
	assert signbit(deg2dms(-0.0)[0]) == True
	assert signbit(deg2dms(+0.0)[0]) == False
	assert signbit(deg2hms(-0.0)[0]) == True
	assert signbit(deg2hms(+0.0)[0]) == False

def testset_deg1() -> None:
	assert deg2dms(-0.100) == (-0.0, 6.00, 0.0)
	assert deg2dms(+0.100) == (+0.0, 6.00, 0.0)
	assert deg2hms(-122.5) == (-8.0, 10.0, 0.0)
	assert deg2hms(+122.5) == (+8.0, 10.0, 0.0)

def testset_dms1() -> None:
	assert deg2dms(-295.4319398933482) == (-295.0, 25.0, 54.983616053573314)
	assert deg2dms(-61.01885607803051) == (-61.00, 1.00, 7.8818809098345355)
	assert deg2dms(+295.4319398933482) == (+295.0, 25.0, 54.983616053573314)
	assert deg2dms(+61.01885607803051) == (+61.00, 1.00, 7.8818809098345355)

def testset_hms1() -> None:
	assert deg2hms(-295.4319398933482) == (-19.0, 41.0, 43.66557440356985)
	assert deg2hms(-61.01885607803051) == (-4.00, 4.00, 4.525458727322942)
	assert deg2hms(+295.4319398933482) == (+19.0, 41.0, 43.66557440356985)
	assert deg2hms(+61.01885607803051) == (+4.00, 4.00, 4.525458727322942)

