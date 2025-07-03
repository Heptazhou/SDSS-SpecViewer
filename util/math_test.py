from .math import Inf, mod, modf60, nextfloat, prevfloat, rem, signbit


def testset_mf60() -> None:
	assert modf60(-1.25) == (-15.0, -1)
	assert modf60(-2.50) == (-30.0, -2)
	assert modf60(+3.75) == (+45.0, +3)
	assert modf60(+5.00) == (+00.0, +5)

def testset_mod0() -> None:
	assert type(mod(1.0, 1.0)) == float
	assert type(mod(1.0, 100)) == float
	assert type(mod(100, 1.0)) == float
	assert type(mod(100, 100)) == int

def testset_rem0() -> None:
	assert type(rem(1.0, 1.0)) == float
	assert type(rem(1.0, 100)) == float
	assert type(rem(100, 1.0)) == float
	assert type(rem(100, 100)) == int

def testset_mod1() -> None:
	assert mod(+20, +50) == +20
	assert mod(+30, +50) == +30
	assert mod(+70, +50) == +20
	assert mod(+80, +50) == +30

def testset_mod2() -> None:
	assert mod(-20, +50) == +30
	assert mod(-30, +50) == +20
	assert mod(-70, +50) == +30
	assert mod(-80, +50) == +20

def testset_mod3() -> None:
	assert mod(-20, -50) == -20
	assert mod(-30, -50) == -30
	assert mod(-70, -50) == -20
	assert mod(-80, -50) == -30

def testset_mod4() -> None:
	assert mod(+20, -50) == -30
	assert mod(+30, -50) == -20
	assert mod(+70, -50) == -30
	assert mod(+80, -50) == -20

def testset_rem1() -> None:
	assert rem(+20, +50) == +20
	assert rem(+30, +50) == +30
	assert rem(+70, +50) == +20
	assert rem(+80, +50) == +30

def testset_rem2() -> None:
	assert rem(-20, +50) == -20
	assert rem(-30, +50) == -30
	assert rem(-70, +50) == -20
	assert rem(-80, +50) == -30

def testset_rem3() -> None:
	assert rem(-20, -50) == -20
	assert rem(-30, -50) == -30
	assert rem(-70, -50) == -20
	assert rem(-80, -50) == -30

def testset_rem4() -> None:
	assert rem(+20, -50) == +20
	assert rem(+30, -50) == +30
	assert rem(+70, -50) == +20
	assert rem(+80, -50) == +30

def testset_prev() -> None:
	assert prevfloat(-1.0) == -1.0000000000000002
	assert prevfloat(-Inf) == -Inf
	assert prevfloat(+0.0) == -5.0e-324
	assert prevfloat(+1.0) == +0.9999999999999999

def testset_next() -> None:
	assert nextfloat(-0.0) == +5.0e-324
	assert nextfloat(-1.0) == -0.9999999999999999
	assert nextfloat(+1.0) == +1.0000000000000002
	assert nextfloat(+Inf) == +Inf

def testset_sign() -> None:
	assert signbit(-0.0) == True
	assert signbit(-1.0) == True
	assert signbit(+0.0) == False
	assert signbit(+1.0) == False

