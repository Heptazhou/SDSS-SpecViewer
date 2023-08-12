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
Pkg.Types.EnvCache().manifest.julia_version ≡ VERSION ? Pkg.instantiate() : Pkg.update()

using Base.Threads: @spawn, @threads, nthreads
using DataFrames: AbstractDataFrame, DataFrame
using FITSIO: FITS, Tables.columnnames
using JSON: json
using OrderedCollections: LittleDict, OrderedDict
using Query: @filter, @groupby, @map, @orderby, @select, @take, @thenby, @unique, key

const Int32OrFlt = Union{Int32, Float32, Float64}
const Int32OrStr = Union{Int32, String}
const s_info(xs...) = @static nthreads() > 1 ? @spawn(@info(string(xs...))) : @info(string(xs...))
const u_sort!(v::AbstractDataFrame; kw...) = unique!(sort!(vec(v); kw...))
const u_sort!(v::AbstractVector; kw...) = unique!(sort!(v::Vector; kw...))

Base.convert(::Type{Int32OrStr}, x::Int64) = Int32(x)
Base.isless(::Any, ::Number)               = Bool((0))
Base.isless(::Number, ::Any)               = Bool((1))
Base.vec(v::AbstractDataFrame)             = Matrix(v) |> vec

@info "Looking for spAll file (*.fits|*.fits.tmp|*.fits.gz|*.7z)"

# https://data.sdss.org/datamodel/files/BOSS_SPECTRO_REDUX/RUN2D/spAll.html
# https://github.com/sciserver/sqlloader/blob/master/schema/sql/SpectroTables.sql
# https://www.sdss.org/dr18/data_access/bitmasks/
const cols = [
	:CATALOGID    # Int64    # SDSS-V CatalogID
	:FIELD        # Int32    # Field number
	:FIELDQUALITY # String   # Quality of field ("good" | "bad")
	:MJD          # Int32    # Modified Julian date of observation
	:MJD_FINAL    # Float64  # Mean MJD of the Coadded Spectra
	:OBJTYPE      # String   # Why this object was targetted; see spZbest
	:PROGRAMNAME  # String   # Program name within a given survey
	:RCHI2        # Float32  # Reduced χ² for best fit
	:SURVEY       # String   # Survey that plate is part of
	:Z            # Float32  # Redshift; assume that this redshift is incorrect if the ZWARNING flag is nonzero
	:ZWARNING     # Int32    # A flag set for bad redshift fits in place of calling CLASS=UNKNOWN; see bitmasks
]
const fits = try
	(f = mapreduce(x -> filter!(endswith(x), readdir()), vcat, [r"\.fits(\.tmp)?", r"\.fits\.gz"]))
	(f = [f; filter!(endswith(".7z"), readdir() |> reverse!)][1]) # must be single file archive
	(endswith(f, r"7z|gz") && (run(`7z x $f`); f = readlines(`7z l -ba -slt $f`)[1][8:end]))
	(endswith(f, r"\.tmp") && ((t, f) = (f, replace(f, r"\.tmp$" => "")); mv(t, f)); f)
catch
	throw(SystemError("*.fits", 2)) # ENOENT 2 No such file or directory
end
# FITS(fits)[2]

const df = @time @sync let
	# cols = columnnames(FITS(fits)[2]) # uncomment to read all the columns
	s_info("Reading ", length(cols), " columns from `$fits` (t = $(nthreads()))")
	@threads for col ∈ cols
		@eval $col = read(FITS(fits)[2], $(String(col)))
		@eval $col isa Vector || ($col = collect(Vector{eltype($col)}, eachcol($col)))
	end
	df = DataFrame(@eval (; $(cols...)))
	df = DataFrame(@filter(R -> R.FIELDQUALITY ≡ "good")(df) |> @select(-:FIELDQUALITY) |> @unique())
end
# LittleDict(map(eltype, eachcol(df)), propertynames(df))

@info "Setting up dictionaries of fieldIDs for each RM_field"

const programs =
	OrderedDict{String, Vector{Int32OrStr}}(
		"SDSS-RM"   => [15171, 15172, 15173, 15290, 16169, 20867, 112359, "all"],
		"XMMLSS-RM" => [15000, 15002, 23175, 112361, "all"],
		"COSMOS-RM" => [15038, 15070, 15071, 15252, 15253, 16163, 16164, 16165, 20868, 23288, 112360, "all"],
	)

@info "Sorting out the fields (including the `all` option if instructed to do so)"

const programs_cats = @time @sync let
	f_programs_dict = OrderedDict{String, Expr}(
		"eFEDS1"       => :(_.SURVEY ≡ "BHM" && _.OBJTYPE ≡ "QSO" && _.PROGRAMNAME ≡ "eFEDS1"),
		"eFEDS2"       => :(_.SURVEY ≡ "BHM" && _.OBJTYPE ≡ "QSO" && _.PROGRAMNAME ≡ "eFEDS2"),
		"eFEDS3"       => :(_.SURVEY ≡ "BHM" && _.OBJTYPE ≡ "QSO" && _.PROGRAMNAME ≡ "eFEDS3"),
		"MWM3"         => :(_.SURVEY ≡ "BHM" && _.OBJTYPE ≡ "QSO" && _.PROGRAMNAME ≡ "MWM3"),
		"MWM4"         => :(_.SURVEY ≡ "BHM" && _.OBJTYPE ≡ "QSO" && _.PROGRAMNAME ≡ "MWM4"),
		"AQMES-Bonus"  => :(_.SURVEY ≡ "BHM" && _.OBJTYPE ≡ "QSO" && _.PROGRAMNAME ≡ "AQMES-Bonus"),
		"AQMES-Wide"   => :(_.SURVEY ≡ "BHM" && _.OBJTYPE ≡ "QSO" && _.PROGRAMNAME ≡ "AQMES-Wide"),
		"AQMES-Medium" => :(_.SURVEY ≡ "BHM" && _.OBJTYPE ≡ "QSO" && _.PROGRAMNAME ≡ "AQMES-Medium"),
		"RM-Plates"    => :(_.SURVEY ≡ "BHM" && _.OBJTYPE ≡ "QSO" && _.PROGRAMNAME ∈ ("RM", "RMv2", "RMv2-fewMWM")),
		"RM-Fibers"    => :(_.SURVEY ≡ "BHM" && _.OBJTYPE ≡ "science" && _.PROGRAMNAME ≡ "bhm_rm"),
		"bhm_aqmes"    => :(_.SURVEY ≡ "BHM" && _.OBJTYPE ≡ "science" && _.PROGRAMNAME ≡ "bhm_aqmes"),
		"bhm_csc"      => :(_.SURVEY ≡ "BHM" && _.OBJTYPE ≡ "science" && _.PROGRAMNAME ≡ "bhm_csc"),
		"bhm_filler"   => :(_.SURVEY ≡ "BHM" && _.OBJTYPE ≡ "science" && _.PROGRAMNAME ≡ "bhm_filler"),
		"bhm_spiders"  => :(_.SURVEY ≡ "BHM" && _.OBJTYPE ≡ "science" && _.PROGRAMNAME ≡ "bhm_spiders"),
		"open_fiber"   => :(_.SURVEY ≡ "open_fiber" && _.OBJTYPE ≡ "science" && _.PROGRAMNAME ≡ "open_fiber"),
	)
	foreach(u_sort!, programs.vals)
	all_prog = @eval @filter([$(f_programs_dict.vals...)] |> any)
	all_cats = @spawn DataFrame(df |> all_prog |> @select(:CATALOGID)) |> u_sort! |> Tuple
	for (k, v) ∈ f_programs_dict
		program = @eval @filter($v)
		programs[k] = Int32OrStr[DataFrame(df |> program |> @select(:FIELD)) |> u_sort!; "all"]
	end
	all_cats |> fetch
end

@info "Filling fieldIDs and catalogIDs with only science targets and completed epochs"

const fieldIDs = @time @sync let
	get_data_of(ids::Tuple{Vararg{Int32}}) = # Int32 => :FIELD
		@select(:CATALOGID, :FIELD, :SURVEY, :OBJTYPE)(df) |>
		@filter(R -> R.FIELD ∈ ids && R.SURVEY ≡ "BHM" && R.OBJTYPE ∈ ("QSO", "science")) |>
		@unique() |> @groupby(R -> R.FIELD) |>
		@map(G -> string(key(G)) => u_sort!(G.CATALOGID |> Vector)) |> Tuple
	d = OrderedDict{String, Vector{Int64}}()
	s_info("Processing ", sum(length, programs.vals), " entries of ", length(programs), " programs")
	for (prog, opts) ∈ programs
		data = get_data_of(filter(≠("all"), opts) |> Tuple)
		for (k, v) ∈ data
			haskey(d, k) ? append!(d[k], v) |> u_sort! : d[k] = v
		end
		d["$prog-all"] = mapreduce(p -> p.second, vcat, data, init = valtype(d)()) |> u_sort!
	end
	sort!(d, by = s -> something(tryparse(Int32, s), s))
end

@info "Building dictionaries (can take a while with AQMES or open fiber targets)"

const catalogIDs = @time @sync let
	z_best_of(G) = @select(:ZWARNING, :Z, :RCHI2)(G) |>
				   @orderby(R -> R.ZWARNING > (0)) |> @thenby(R -> R.RCHI2) |>
				   @take(1) |> x -> collect(x)[1]
	get_data_of(ids::Tuple{Vararg{Int64}}) = # Int64 => :CATALOGID
		@select(:CATALOGID, :FIELD, :MJD, :MJD_FINAL, :RCHI2, :Z, :ZWARNING)(df) |>
		@filter(R -> R.CATALOGID ∈ ids) |>
		@unique() |> @groupby(R -> R.CATALOGID) |>
		@map(G -> string(key(G)) => NTuple{3, Int32OrFlt}[z_best_of(G) |> values
			map(values, @select(:FIELD, :MJD, :MJD_FINAL)(G) |> collect) |> u_sort!]) |> Tuple
	s_info("Processing ", length(programs_cats), " entries")
	d = OrderedDict{String, Vector{NTuple{3, Int32OrFlt}}}(get_data_of(programs_cats))
	sort!(d, by = s -> parse(Int64, s))
end

@info "Dumping dictionaries to file"
write("dictionaries.txt", json([programs, fieldIDs, catalogIDs]), "\n")

