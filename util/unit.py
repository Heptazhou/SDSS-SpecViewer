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

from .math import modf60, rem


def deg2dms(angle: float) -> tuple[float, float, float]:
	x = rem(angle, 360)
	x, d = modf60(x)
	s, m = modf60(x)
	return d, abs(m), abs(s)

def deg2ha(angle: float) -> float:
	x = rem(angle, 360)
	return (24 / 360) * x

def deg2hms(angle: float) -> tuple[float, float, float]:
	h, m, s = ha2hms(deg2ha(angle))
	return h, abs(m), abs(s)

def ha2hms(angle: float) -> tuple[float, float, float]:
	h, m, s = deg2dms(rem(angle, 24))
	return h, abs(m), abs(s)

