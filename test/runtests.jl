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

using Exts
using Exts: with_temp_env
using Pkg: Pkg
using PythonCall: GIL, Py, pyconvert, pyimport
using Test

const Jl(x::Any) = x
const Jl(x::Py)  = pyconvert(Any, x)

let sys = pyimport("sys")
	sys.path.append(stdpath(@__DIR__, ".."))
end

include("misc.jl")

include("sdss.jl")
include("util.jl")

