# Copyright (C) 2025 Heptazhou <zhou@0h7z.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, version 3.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

from math import ceil, copysign, floor, fmod
from math import isclose as isapprox
from math import modf, trunc
from typing import overload


def cld(x: int | float, y: int | float) -> int: # pragma: no cover
	return ceil(x / y)
def div(x: int | float, y: int | float) -> int: # pragma: no cover
	return trunc(x / y)
def fld(x: int | float, y: int | float) -> int: # pragma: no cover
	return floor(x / y)

@overload # pragma: no cover
def mod(x: int, y: int) -> int: pass
@overload # pragma: no cover
def mod(x: int, y: float) -> float: pass
@overload # pragma: no cover
def mod(x: float, y: int) -> float: pass
@overload # pragma: no cover
def mod(x: float, y: float) -> float: pass

def mod(x: int | float, y: int | float) -> int | float:
	"""
	The remainder of `fld(x, y)`, which has the same sign as `y` and magnitude less than `abs(y)`.
	"""
	return x % y

@overload # pragma: no cover
def rem(x: int, y: int) -> int: pass
@overload # pragma: no cover
def rem(x: int, y: float) -> float: pass
@overload # pragma: no cover
def rem(x: float, y: int) -> float: pass
@overload # pragma: no cover
def rem(x: float, y: float) -> float: pass

def rem(x: int | float, y: int | float) -> int | float:
	"""
	The remainder of `div(x, y)`, which has the same sign as `x` and magnitude less than `abs(y)`.
	"""
	if not int == type(y) == type(x):
		return fmod(x, y)
	return int(fmod(x, y))

def modf60(x: float) -> tuple[float, float]:
	f, i = modf(roundapprox(x))
	return 60 * f, roundfloat(i)

def roundapprox(x: float) -> float:
	i = roundfloat(x)
	return i if isapprox(x, i) else x

def roundfloat(x: float) -> float:
	return round(x, ndigits=0)

def signbit(x: float) -> bool:
	"""
	Return true if `x` is negative, otherwise false.
	"""
	return copysign(1, x) == -1

