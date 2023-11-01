# Copyright (C) 2023 Heptazhou <zhou@0h7z.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

using Pkg: Pkg
cd(@__DIR__)
Pkg.activate(".")

try
	"Manifest.toml" |> f -> (v"1.7" ≤ VERSION && isfile(f) || return;
	any(startswith("julia_version"), eachline(f)) || rm(f))
	Pkg.Registry.update("General")
	Pkg.resolve()
	Pkg.instantiate()
catch
	Pkg.Registry.add("General")
	Pkg.update()
end
using DataFrames, DataFramesMeta,
	FITSIO, JSON, OrderedCollections

