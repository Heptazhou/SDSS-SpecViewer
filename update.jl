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

using Pkg: Pkg, Registry, RegistrySpec

@static if isnothing(Base.active_project()) ||
		   !(dirname(Base.active_project()) == @__DIR__)
	Pkg.activate(@__DIR__)
end

let registry = getfield.(Registry.reachable_registries(), :name)
	registry ∋ "0hjl" || Registry.add(RegistrySpec(url = "https://github.com/0h7z/0hjl.git"))
	registry ∋ "General" || Registry.add("General")
	cd(@__DIR__) do
		m = touch(sort([Base.manifest_names...], by = contains("-v"))[end])
		(un_v -> (un_v !== m) && isfile(un_v) && rm(un_v))("Manifest.toml")
		Pkg.update()
		contains(readchomp(m), "julia_version =") || Pkg.upgrade_manifest()
	end
end

