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

module SpecViewer

include("const.jl")

using Exts
using Match: @match

function branch2version(b::SymOrStr)::VersionNumber
	branch2version(String(b))
end
function branch2version(b::String)::VersionNumber
	b ≡ "master" && return v"0"
	m = match(r"\bv\d+[._]\d+[._]\d+\b", b).match
	v = VersionNumber(replace(m, '_' => '.'))
end
function version2branch(v::VersionNumber)::Symbol
	@match v begin
		v"0" => :master
		_    => Symbol(replace("v$v", '.' => '_'))
	end
end

function sas_redux_spec(field::Integer, mjd::Integer, obj::IntOrStr, branch::SymOrStr, variant::String = "")::String
	sas_redux_spec(field, mjd, obj, branch2version(branch), variant)
end
function sas_redux_spec(field::Integer, mjd::Integer, obj::IntOrStr, v::VersionNumber, variant::String = "")::String
	v"0" < v ≤ v"5.10.0" || isempty(variant) && (variant = "full")
	path = @match v begin
		v where v"0" < v < v"6" => begin
			isa(obj, Integer) && (obj = string(obj, pad = 04))
			isempty(variant) ? "spectra/$field/" :
			"spectra/$variant/$field/"
		end
		v where v"6" ≤ v ≤ v"6.0.4" => begin
			isa(obj, Integer) && (obj = string(obj, pad = 11))
			"spectra/$variant/$field$(:p)/$mjd/"
		end
		v where v"6" ≤ v < v"6.2.0" => begin
			field = string(field, pad = 06)
			"spectra/$variant/$field/$mjd/"
		end
		_ => begin # LCOV_EXCL_LINE
			field = string(field, pad = 06)
			"spectra/daily/$variant/$(field[1:end-3])XXX/$field/$mjd/"
		end
	end
	sas_redux(v) * path * "spec-$field-$mjd-$obj.fits"
end

function sas_redux(v::VersionNumber)::String
	@match v begin
		v"0"     => sas_redux(:work, v)
		v"6.0.1" => sas_redux(:work, v)
		v"6.0.2" => sas_redux(:work, v)
		v"6.0.3" => sas_redux(:work, v)
		v"6.0.4" => @match_fail sas_redux(:work, v) # dr18
		v"6.0.6" => sas_redux(:work, v)
		v"6.0.7" => sas_redux(:work, v)
		v"6.0.8" => sas_redux(:work, v)
		v"6.0.9" => sas_redux(:work, v)
		v"6.1.0" => sas_redux(:work, v)
		v"6.1.1" => sas_redux(:work, v)
		v"6.1.2" => sas_redux(:work, v)
		v"6.1.3" => sas_redux(:work, v)
		v"6.2.0" => sas_redux(:work, v)
		#
		v"5.4.45" => sas_redux(:dr09, v)
		v"5.5.12" => sas_redux(:dr10, v)
		v"5.6.5"  => sas_redux(:dr11, v)
		v"5.7.0"  => sas_redux(:dr12, v)
		v"5.7.2"  => sas_redux(:dr12, v)
		v"5.9.0"  => sas_redux(:dr13, v)
		#
		v"5.10.0" => @match_fail sas_redux(:dr14, v) # dr15
		v"5.10.0" => sas_redux(:dr15, v)
		v"5.13.0" => sas_redux(:dr16, v)
		v"5.13.2" => @match_fail sas_redux(:dr17, v) # dr18
		v"5.13.2" => sas_redux(:dr18, v)
		v"6.0.4"  => sas_redux(:dr18, v)
	end
end

function sas_redux(s::Symbol, v::VersionNumber)::String
	string(sas_redux(s), version2branch(v), :/)
end
function sas_redux(s::Symbol)::String
	@match s begin
		:dr08 => SAS_REDUX_DR08
		:dr09 => SAS_REDUX_DR09
		:dr10 => SAS_REDUX_DR10
		:dr11 => SAS_REDUX_DR11
		:dr12 => SAS_REDUX_DR12
		:dr13 => SAS_REDUX_DR13
		:dr14 => SAS_REDUX_DR14
		:dr15 => SAS_REDUX_DR15
		:dr16 => SAS_REDUX_DR16
		:dr17 => SAS_REDUX_DR17
		:dr18 => SAS_REDUX_DR18
		:work => SAS_REDUX_WORK
	end
end

end # module

