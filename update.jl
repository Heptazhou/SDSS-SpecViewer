# Copyright (C) 2023-2025 Heptazhou <zhou@0h7z.com>
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

@static if isnothing(Base.active_project()) ||
		   !(dirname(Base.active_project()) == @__DIR__)
	using Pkg: Pkg
	Pkg.activate(@__DIR__)
end

using Pkg: Pkg, Registry, RegistrySpec

let registry = getfield.(Registry.reachable_registries(), :name)
	registry ∋ "0hjl" || Registry.add(RegistrySpec(url = "https://github.com/0h7z/0hjl.git"))
	registry ∋ "General" || Registry.add("General")
	cd(() -> touch(Base.manifest_names[VERSION < v"1.10.8" ? end : end ÷ 2]), @__DIR__)
	Pkg.update()
end

