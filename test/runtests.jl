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

@static if isinteractive()
	using Pkg: Pkg
	Pkg.update()
end

using Exts
using Exts: Jl, with_temp_env
using Pkg: Pkg
using PythonCall: pyimport
using Test

include("misc.jl")
include("sdss.jl")

foreach(_ -> GC.gc(), 1:5)
const py_sys = let sys = pyimport("sys")
	sys.path.append(stdpath(@__DIR__, ".."))
	sys
end
const py_util = pyimport("util")
include("util.jl")

