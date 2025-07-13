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

import json as JSON
from builtins import isinstance as isa
from pathlib import Path
from typing import TypeVar

T = TypeVar("T")

def identity(x: T) -> T: # todo v3.12
	return x

# def identity[T](x: T) -> T: # v3.12+
# 	return x

def isfile(f: Path | str) -> bool:
	if isa(f, Path):
		return (f).is_file()
	return Path(f).is_file()

def parse_json(x: str | bytes | bytearray):
	if not isa(x, str):
		return JSON.loads(x)
	with open(x, newline="") as io:
		return JSON.load(io)

def write(f: Path | str, x: bytes | str) -> int:
	if isa(x, bytes):
		with open(f, "wb") as io:
			return io.write(x)
	else:
		with open(f, "wt", newline="") as io:
			return io.write(x)

