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

using Pkg: Pkg
cd(@__DIR__)
Pkg.activate(".")

using Base.Threads: @spawn, @threads, nthreads
using DataFrames: DataFrame
using DataFramesMeta
using FITSIO: FITS, Tables.columnnames
using FITSIO: FITSIO # fix merged but not released
using JSON: json
using OrderedCollections

const getfirst(predicate::Function) = A -> A[findfirst(predicate, A)]
const s_info(xs...) = @static nthreads() > 1 ? @spawn(@info string(xs...)) : @info string(xs...)
const u_sort! = unique! ∘ sort!

Base.cat(x::Integer, y::Integer, ::Val{5}) = flipsign((10^5)abs(x) + mod(y, 10^5), x)
Base.convert(::Type{S}, v::Vector) where S <: AbstractSet{T} where T = S(T[v;])
Base.isless(::Any, ::Union{Number, VersionNumber}) = Bool(0)
Base.isless(::Union{Number, VersionNumber}, ::Any) = Bool(1)

# https://github.com/JuliaAstro/FITSIO.jl/pull/193
FITSIO.CFITSIO_COLTYPE[080] = UInt64
FITSIO.fits_tform_char(::Type{UInt64}) = 'W'

@static if VERSION < v"1.7"
	(fc::ComposedFunction)(xs...; kw...) = fc.outer(fc.inner(xs...; kw...))
	macro something(xs...)
		:(something($(esc.(xs)...)))
	end
end
@static if VERSION < v"1.9"
	Base.filter(f) = Base.Fix1(filter, f)
end

@info "Looking for spAll file (.fits|.fits.tmp) or archive (.7z|.gz|.rar|.zip)"

# https://data.sdss.org/datamodel/files/BOSS_SPECTRO_REDUX/RUN2D/spAll.html
# https://github.com/sciserver/sqlloader/blob/master/schema/sql/SpectroTables.sql
# https://www.sdss.org/dr18/data_access/bitmasks/
const cols = LittleDict{Symbol, DataType}(
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
	has_7z = (f::String) -> try
		# https://github.com/mcmilk/7-Zip/blob/master/CPP/7zip/UI/Console/Main.cpp
		any(startswith("7-Zip "), readlines(`7z`)) || error()
	catch
		(@info "7z not found. Skipping archive `$f`"; false)
	end
	extracts(arc::String) = run(`7z x $arc`)
	filename(arc::String) = readlines(`7z l -ba -slt $arc`)[1][8:end]
	is_arc = endswith(r"\.(7z|gz|rar|zip)")
	is_tmp = endswith(r"\.tmp")
	d = OrderedDict{String, String}()
	for f ∈ (map)(filter(isfile), [ARGS, readdir()]) |> getfirst(!isempty)
		n = !is_arc(f) ? f : has_7z(f) ? filename(f) : (continue)
		contains(n, r"\bspall\b"i) || continue
		contains(n, r"\ballepoch\b"i) && continue
		endswith(n, r"\.fits(\.tmp)?") && (d[n] = f)
	end
	for (k, v) ∈ d
		is_arc(v) && (d[k] = filename(v); isfile(d[k]) || extracts(v); v = d[k])
		is_tmp(v) && (d[k] = replace(v, r"\.tmp$" => ""); isfile(d[k]) || mv(v, d[k]))
	end
	u_sort!(d.vals, by = s -> (m = match(r"\bv\d+[._]\d+[._]\d+\b", s)) |> isnothing ?
							  "master" : VersionNumber(replace(m.match, "_" => ".")))
catch
	throw(SystemError("*spall*.fits", 2)) # ENOENT 2 No such file or directory
end
# FITS(fits[end])["SPALL"]

const df = @time @sync let cols = cols.keys, fits = fits
	f2df(fits::String; n::Union{Int, String} = "SPALL") = begin
		try
			FITS(fits)[n]
		catch
			n = 2
		end
		# cols = columnnames(FITS(fits)[n]) # uncomment this to read all columns
		s_info("Reading ", length(cols), " column(s) from `$fits` (t = $(nthreads()))")
		@threads for col ∈ cols
			@eval $col = read(FITS($fits)[$n], $(String(col)))
			@eval $col isa Vector || ($col = eachslice($col, dims = ndims($col)))
		end
		@chain DataFrame(@eval (; $(cols...))) begin
			@rsubset! :FIELDQUALITY ≡ "good"
			@select! $(Not(:FIELDQUALITY))
		end
	end
	unique!(fits isa String ? f2df(fits) : mapreduce(f2df, vcat, fits))
end
# LittleDict(propertynames(df), map(eltype, eachcol(df)))

@info "Setting up dictionary for fieldIDs with each RM_field"

const programs =
	LittleDict{String, OrderedSet{cols[:FIELD]}}(
		"SDSS-RM"   => [15171, 15172, 15173, 15290, 16169, 20867, 112359],
		"XMMLSS-RM" => [15000, 15002, 23175, 112361],
		"COSMOS-RM" => [15038, 15070, 15071, 15252, 15253, 16163, 16164, 16165, 20868, 23288, 112360],
	)

@info "Sorting out the fields (including the `all` option if instructed to do so)"

const programs_cats = @time @sync let
	f_programs_dict = LittleDict{String, Expr}(
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
	all_cats = @spawn @eval (OrderedSet ∘ sort!)(@rsubset(df, $x).CATALOGID)
	for (p, x) ∈ f_programs_dict
		programs[p] = @eval (OrderedSet ∘ sort!)(@rsubset(df, $x).FIELD)
	end
	all_cats |> fetch
end

@info "Filling fieldIDs and catalogIDs with only science targets and completed epochs"

const fieldIDs = @time @sync let cat_t = cols[:CATALOGID]
	get_data_of(ids::OrderedSet{cols[:FIELD]}) = @chain df begin
		@select :CATALOGID :FIELD :SURVEY :OBJTYPE
		@rsubset! :FIELD ∈ ids && :SURVEY ≡ "BHM" && :OBJTYPE ∈ ("QSO", "science")
		@by :FIELD :CATALOGID = [:CATALOGID]
	end
	d, init = OrderedDict{String, Vector{cat_t}}(), cat_t[]
	s_info("Processing ", sum(length, programs.vals), " entries of ", length(programs), " programs")
	for (prog, opts) ∈ programs
		data = get_data_of(opts) |> eachrow
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
	get_dict_of(ids::OrderedSet{cols[:CATALOGID]}) = @chain df begin
		@rselect :CATALOGID :FIELD_MJD = cat(:FIELD, :MJD, Val(5)) :RCHI2 :Z :ZWARNING
		@rsubset! :CATALOGID ∈ ids
		@rorderby :CATALOGID :ZWARNING > 0 :RCHI2
		@by :CATALOGID begin
			:ks = string(:CATALOGID[1])
			:vs = (Real[:ZWARNING :Z :RCHI2][1, :], u_sort!([:FIELD_MJD;])...)
		end
		LittleDict(_.ks, _.vs)
	end
	s_info("Processing ", length(programs_cats), " entries")
	get_dict_of(programs_cats)
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

