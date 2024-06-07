# Copyright (C) 2023-2024 Heptazhou <zhou@0h7z.com>
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

using Pkg: Pkg, Registry, RegistrySpec
cd(@__DIR__)
Pkg.activate(".")

let registry = getfield.(Registry.reachable_registries(), :name)
	registry ∋ "0hjl" || Registry.add(RegistrySpec(url = "https://github.com/0h7z/0hjl.git"))
	registry ∋ "General" || Registry.add("General")
	isfile("Manifest.toml") ? Pkg.update() : Pkg.instantiate()
end

