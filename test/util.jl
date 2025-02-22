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

@testset "util" begin
#! format: noindent

using SpecViewer: sas_redux_spec, version2branch

util = pyimport("util")

spec(field, mjd, obj, branch) = sas_redux_spec(field, mjd, obj, branch, "lite")

function func(field::Union{Integer, Symbol}, mjd::Integer, obj::IntOrStr, v::VersionNumber)
	branch::Symbol = version2branch(v)
	Jl(util.SDSSV_buildURL(string(field), mjd, obj, string(branch)))
end

@testset "dr09" begin
	b = v"5.4.45"
	plate, mjd, fiber = 3586, 55181, "0001"
	@test spec(plate, mjd, fiber, b) ≡ func(plate, mjd, fiber, b)
end

@testset "dr10" begin
	b = v"5.5.12"
	plate, mjd, fiber = 3586, 55181, "0001"
	@test spec(plate, mjd, fiber, b) ≡ func(plate, mjd, fiber, b)
end

@testset "dr11" begin
	b = v"5.6.5"
	plate, mjd, fiber = 3586, 55181, "0001"
	@test spec(plate, mjd, fiber, b) ≡ func(plate, mjd, fiber, b)
end

@testset "dr12" begin
	b = v"5.7.0"
	plate, mjd, fiber = 3586, 55181, "0001"
	@test spec(plate, mjd, fiber, b) ≡ func(plate, mjd, fiber, b)

	b = v"5.7.2"
	plate, mjd, fiber = 7339, 56768, "0001"
	@test spec(plate, mjd, fiber, b) ≡ func(plate, mjd, fiber, b)
end

@testset "dr13" begin
	b = v"5.9.0"
	plate, mjd, fiber = 3586, 55181, "0001"
	@test spec(plate, mjd, fiber, b) ≡ func(plate, mjd, fiber, b)
end

@testset "dr15" begin
	b = v"5.10.0"
	plate, mjd, fiber = 3586, 55181, "0001"
	@test spec(plate, mjd, fiber, b) ≡ func(plate, mjd, fiber, b)
	plate, mjd, fiber = 10000, 57346, "0001"
	@test spec(plate, mjd, fiber, b) ≡ func(plate, mjd, fiber, b)
end

@testset "dr16" begin
	b = v"5.13.0"
	plate, mjd, fiber = 3586, 55181, "0001"
	@test spec(plate, mjd, fiber, b) ≡ func(plate, mjd, fiber, b)
end

@testset "dr17" begin
	b = v"5.13.2"
	plate, mjd, fiber = 3586, 55181, "0001"
	@test spec(plate, mjd, fiber, b) ≡ func(plate, mjd, fiber, b)
end

@testset "dr18" begin
	b = v"5.13.2"
	plate, mjd, fiber = 3586, 55181, "0001"
	@test spec(plate, mjd, fiber, b) ≡ func(plate, mjd, fiber, b)

	b = v"6.0.4"
	field, mjd, catid = 15143, 59205, "04544940698"
	@test spec(field, mjd, catid, b) ≡ func(field, mjd, catid, b)
end

@testset "work" begin
	b = v"6.0.9"
	field, mjd, catid = 015000, 59146, "4375786564"
	@test spec(field, mjd, catid, b) ≡ func(field, mjd, catid, b)

	b = v"6.1.1"
	field, mjd, catid = 015000, 59146, "4375786564"
	@test spec(field, mjd, catid, b) ≡ func(field, mjd, catid, b)
	field, mjd, catid = :allepoch, 60000, "27021598054114233"
	@test spec(field, mjd, catid, b) ≡ func(field, mjd, catid, b)

	b = v"6.1.3"
	field, mjd, catid = 015000, 59146, "4375786564"
	@test spec(field, mjd, catid, b) ≡ func(field, mjd, catid, b)
	field, mjd, catid = :allepoch, 60000, "27021598054114233"
	@test spec(field, mjd, catid, b) ≡ func(field, mjd, catid, b)
	field, mjd, catid = :allepoch_lco, 60000, 27021598048679601
	@test spec(field, mjd, catid, b) ≡ func(field, mjd, catid, b)

	b = v"6.2.0"
	field, mjd, catid = 015000, 59146, "4375786564"
	@test spec(field, mjd, catid, b) ≡ func(field, mjd, catid, b)
	field, mjd, catid = :allepoch_apo, 60000, 27021602603659704
	@test spec(field, mjd, catid, b) ≡ func(field, mjd, catid, b)
	field, mjd, catid = :allepoch_lco, 60000, 63050395106956948
	@test spec(field, mjd, catid, b) ≡ func(field, mjd, catid, b)

	b = v"0" # master
	field, mjd, catid = 016199, 60606, "27021597863477824"
	@test spec(field, mjd, catid, b) ≡ func(field, mjd, catid, b)
end

end

