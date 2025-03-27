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

using Pkg: Pkg, Types.Context

@static if isnothing(Base.active_project()) ||
		   !(dirname(Base.active_project()) == @__DIR__)
	Pkg.activate(@__DIR__)
end

let manifest = @something Base.project_file_manifest_path(Base.active_project()) ""
	if (filesize(manifest) ≤ 0) || !(Pkg.is_manifest_current(Context()) == true) ||
	   0 < mtime(manifest) < time() - 86400(30) # 30 day
		include("update.jl")
	end
end

using DataFramesMeta
using Exts
using FITSIO: FITS
using JSON5: json
using Pkg: PlatformEngines

const s_info(xs...) = (@inline; @info string(xs...))
const u_sort! = unique! ∘ sort!

Base.cat(x::Integer, y::Integer, ::Val{5}) = flipsign((10^5)abs(x) + mod(y, 10^5), x)
Base.isless(::Any, ::Union{Number, VersionNumber}) = (@nospecialize; Bool(0))
Base.isless(::Union{Number, VersionNumber}, ::Any) = (@nospecialize; Bool(1))

@info "Looking for spAll files or archives"

# https://data.sdss.org/datamodel/files/BOSS_SPECTRO_REDUX/RUN2D/spAll.html
# https://github.com/sciserver/sqlloader/blob/master/schema/sql/SpectroTables.sql
# https://www.sdss.org/dr18/data_access/bitmasks/
const cols = LDict{Symbol, DataType}(
	:CATALOGID    => Int64,   # SDSS-V CatalogID
	:FIELD        => Int64,   # Field number
	:FIELDQUALITY => String,  # Quality of field ("good" | "bad")
	:MJD          => Int64,   # Modified Julian date of observation
	:OBJTYPE      => String,  # Why this object was targetted; see spZbest
	:PROGRAMNAME  => String,  # Program name within a given survey
	:RCHI2        => Float32, # Reduced χ² for best fit
	:SURVEY       => String,  # Survey that plate is part of
	:Z            => Float32, # Redshift; assume incorrect if ZWARNING is nonzero
	:ZWARNING     => Int64,   # A flag set for bad redshift fits; see bitmasks
)
const fits = try
	exe_7z = @try PlatformEngines.find7z() PlatformEngines.exe7z()
	extracts(arc::String) = run(`$exe_7z x $arc`)
	filename(arc::String) = readlines(`$exe_7z l -ba -slt $arc`)[1][8:end]
	is_arc = endswith(r"\.([7gx]z|rar|zip)")
	is_tmp = endswith(r"\.tmp")
	d = ODict{String, String}()
	for x ∈ getfirst(!isempty, filter(isfile).([ARGS, readdir()]))
		f = is_arc(x) ? filename(x) : x
		contains(f, r"\bspall\b"i) || continue
		contains(f, r"\ballepoch\b"i) && continue
		endswith(f, r"\.fits(\.tmp)?") && (d[f] = x)
	end
	for (k, v) ∈ d
		is_arc(v) && (d[k] = filename(v); isfile(d[k]) || extracts(v); v = d[k])
		is_tmp(v) && (d[k] = replace(v, r"\.tmp$" => ""); isfile(d[k]) || mv(v, d[k]))
	end
	@assert !isempty(d)
	u_sort!(d.vals, by = s -> (m = match(r"\bv\d+[._]\d+[._]\d+\b", s)) |> isnothing ?
							  "master" : VersionNumber(replace(m.match, "_" => ".")))
catch
	systemerror("*spAll*.(fits|[7gx]z)", Libc.ENOENT) # 2 No such file or directory
end
# FITS(fits[end])["SPALL"]

const df = @time @sync let
	_read(f::String) = begin
		n = FITS(f -> get(f, "SPALL", 2).ext, f)
		s_info("Reading ", length(cols), " column(s) from `$f[$n]` (t = $(nthreads()))")
		# see https://0h7z.com/Exts.jl/stable/FITSIO/#Base.read
		FITS(f -> read(f[n], Vector, cols.keys), f)
	end
	df = DataFrame(mapreduce(_read, vcat, fits), cols.keys, copycols = false)
	df = unique!(@rsubset df :FIELDQUALITY ≡ "good")
end
# LDict(propertynames(df), eltype.(eachcol(df)))

@info "Setting up dictionary for fieldIDs with each RM_field"

const programs = LDict{String, OSet{cols[:FIELD]}}(
	"SDSS-RM"   => [15171, 15172, 15173, 15290, 16169, 20867, 112359],
	"XMMLSS-RM" => [15000, 15002, 23175, 112361],
	"COSMOS-RM" => [15038, 15070, 15071, 15252, 15253, 16163, 16164, 16165, 20868, 23288, 112360],
)

@info "Sorting out the fields (including the `all` option if instructed to do so)"

const programs_cats = @time @sync let
	f_programs_dict = LDict{String, Expr}(
		"eFEDS1"       => :(:SURVEY ≡ "BHM" && :OBJTYPE ≡ "QSO" && :PROGRAMNAME ≡ "eFEDS1"),
		"eFEDS2"       => :(:SURVEY ≡ "BHM" && :OBJTYPE ≡ "QSO" && :PROGRAMNAME ≡ "eFEDS2"),
		"eFEDS3"       => :(:SURVEY ≡ "BHM" && :OBJTYPE ≡ "QSO" && :PROGRAMNAME ≡ "eFEDS3"),
		"MWM3"         => :(:SURVEY ≡ "BHM" && :OBJTYPE ≡ "QSO" && :PROGRAMNAME ≡ "MWM3"),
		"MWM4"         => :(:SURVEY ≡ "BHM" && :OBJTYPE ≡ "QSO" && :PROGRAMNAME ≡ "MWM4"),
		"AQMES-Bonus"  => :(:SURVEY ≡ "BHM" && :OBJTYPE ≡ "QSO" && :PROGRAMNAME ≡ "AQMES-Bonus"),
		"AQMES-Wide"   => :(:SURVEY ≡ "BHM" && :OBJTYPE ≡ "QSO" && :PROGRAMNAME ≡ "AQMES-Wide"),
		"AQMES-Medium" => :(:SURVEY ≡ "BHM" && :OBJTYPE ≡ "QSO" && :PROGRAMNAME ≡ "AQMES-Medium"),
		"RM-Plates"    => :(:SURVEY ≡ "BHM" && :OBJTYPE ≡ "QSO" && :PROGRAMNAME ∈ ("RM", "RMv2", "RMv2-fewMWM")),
		"RM-Fibers"    => :(:SURVEY ≡ "BHM" && :OBJTYPE ≡ "science" && :PROGRAMNAME ≡ "bhm_rm"),
		"bhm_aqmes"    => :(:SURVEY ≡ "BHM" && :OBJTYPE ≡ "science" && :PROGRAMNAME ≡ "bhm_aqmes"),
		"bhm_csc"      => :(:SURVEY ≡ "BHM" && :OBJTYPE ≡ "science" && :PROGRAMNAME ≡ "bhm_csc"),
		"bhm_filler"   => :(:SURVEY ≡ "BHM" && :OBJTYPE ≡ "science" && :PROGRAMNAME ≡ "bhm_filler"),
		"bhm_spiders"  => :(:SURVEY ≡ "BHM" && :OBJTYPE ≡ "science" && :PROGRAMNAME ≡ "bhm_spiders"),
		"open_fiber"   => :(:SURVEY ≡ "open_fiber" && :OBJTYPE ≡ "science" && :PROGRAMNAME ≡ "open_fiber"),
	)
	foreach(sort!, programs.vals)
	x = :(any([$(f_programs_dict.vals...)]))
	all_cats = @spawn @eval OSet(sort!(@rsubset(df, $x).CATALOGID))
	for (p, x) ∈ f_programs_dict
		programs[p] = @eval OSet(sort!(@rsubset(df, $x).FIELD))
	end
	all_cats |> fetch
end

@info "Filling fieldIDs and catalogIDs with only science targets and completed epochs"

const fieldIDs = @time @sync let cat_t = cols[:CATALOGID]
	data_of(ids::OSet{cols[:FIELD]}) = @chain df begin
		@select :CATALOGID :FIELD :SURVEY :OBJTYPE
		@rsubset! :FIELD ∈ ids && :SURVEY ≡ "BHM" && :OBJTYPE ∈ ("QSO", "science")
		@by :FIELD :CATALOGID = [:CATALOGID]
	end
	d, init = ODict{String, Vector{cat_t}}(), cat_t[]
	s_info("Processing ", sum(length, programs.vals), " entries of ", length(programs), " programs")
	for (prog, opts) ∈ programs
		data = data_of(opts) |> eachrow
		for (k, v) ∈ data
			(k, v) = string(k), copy(v)
			(haskey(d, k) ? append!(d[k], v) : d[k] = v) |> u_sort!
		end
		d["$prog-all"] = mapreduce(last, vcat, data; init) |> u_sort!
	end
	sort!(d, by = s -> @something tryparse(cat_t, s) s)
end

@info "Building dictionary for catalogIDs"

const catalogIDs = @time @sync let
	dict_of(ids::OSet{cols[:CATALOGID]}) = @chain df begin
		@rselect :CATALOGID :FIELD_MJD = cat(:FIELD, :MJD, Val(5)) :RCHI2 :Z :ZWARNING
		@rsubset! :CATALOGID ∈ ids
		@rorderby :CATALOGID :ZWARNING > 0 :RCHI2
		@by :CATALOGID begin
			:ks = string(:CATALOGID[1])
			:vs = (Real[:ZWARNING :Z :RCHI2][1, :], u_sort!([:FIELD_MJD;])...)
		end
		LDict(_.ks, _.vs)
	end
	s_info("Processing ", length(programs_cats), " entries")
	dict_of(programs_cats)
end

@info "Dumping dictionaries to file"
write("dictionaries.txt",
	"""
	[
		$(json(programs)),
		$(json(fieldIDs)),
		$(json(catalogIDs))
	]
	""")

