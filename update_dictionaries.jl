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
using FITSIO: FITS
using JSON: json
using OrderedCollections: OrderedDict
using Query: @filter, @groupby, @map, @select, @unique, key

const Int32OrFlt = Union{Int32, Float32, Float64}
const Int32OrStr = Union{Int32, String}
const s_info(xs...) = @static nthreads() > 1 ? @spawn(@info(string(xs...))) : @info(string(xs...))
const u_sort!(v::AbstractVector; kw...) = unique!(sort!(v; kw...))
const u_sort!(v::Any; kw...) = u_sort!(vec(v); kw...)

Base.convert(::Type{Int32OrStr}, x::Int64) = Int32(x)
Base.isless(::String, ::Int32)             = Bool((0))
Base.vec(df::AbstractDataFrame)            = Matrix(df) |> vec

@info "Finding local copy of `spAll-*.fits` file"

const cols = [:CATALOGID :FIELD :FIELDQUALITY :MJD :MJD_FINAL :OBJTYPE :PROGRAMNAME :SPEC1_G :SURVEY]
const fits = try
	(f = mapreduce(x -> filter!(endswith(x), readdir()), vcat, [r"\.fits(\.tmp)?", r"\.fits\.gz"]))
	(f = [f; filter!(endswith(".7z"), readdir() |> reverse!)][1]) # must be single file archive
	(endswith(f, r"7z|gz") && (run(`7z x $f`); f = readlines(`7z l -ba -slt $f`)[1][8:end]))
	(endswith(f, r"\.tmp") && ((t, f) = (f, replace(f, r"\.tmp$" => "")); mv(t, f)); f)
catch
	throw(SystemError("*.fits", 2)) # ENOENT 2 No such file or directory
end

const df = @time @sync let
	s_info("Reading ", length(cols), " columns from ", fits)
	@threads for col ∈ cols
		@eval $col = read(FITS(fits)[2], $(String(col)))
	end
	df = DataFrame(@eval (; $(cols...)))
	df = DataFrame(@filter(R -> R.FIELDQUALITY == "good")(df) |> @unique())
end
# FITS(fits)[2]

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

const get_data_of(ids::Tuple{Vararg{Int32}}) = # Int32 => :FIELD
	df |> @select(:CATALOGID, :FIELD, :SURVEY, :OBJTYPE) |>
	@filter(R -> R.FIELD ∈ ids && R.SURVEY ≡ "BHM" && R.OBJTYPE ∈ ("QSO", "science")) |>
	@unique() |> @groupby(R -> R.FIELD) |>
	@map(G -> string(key(G)) => G.CATALOGID |> Vector |> u_sort!) |> Tuple

const fieldIDs = @time @sync let
	d = OrderedDict{String, Vector{Int64}}()
	s_info("Processing ", sum(length, programs.vals), " entries of ", length(programs), " programs")
	for (prog, opts) ∈ programs
		data = get_data_of(filter(≠("all"), opts) |> Tuple)
		for (k, v) ∈ data
			haskey(d, k) ? append!(d[k], v) |> u_sort! : d[k] = v
		end
		d["$prog-all"] = mapreduce(p -> p.second, vcat, data, init = valtype(d)()) |> u_sort!
	end
	sort!(d)
end

@info "Building dictionaries from spAll file (can take a while with AQMES or open fiber targets)"

const get_data_of(ids::Tuple{Vararg{Int64}}) = # Int64 => :CATALOGID
	df |> @select(:CATALOGID, :FIELD, :MJD, :SPEC1_G, :MJD_FINAL) |>
	@filter(R -> R.CATALOGID ∈ ids) |>
	@unique() |> @groupby(R -> R.CATALOGID) |>
	@map(G -> string(key(G)) => map(values, @select(-1)(G) |> collect)) |> Tuple

const catalogIDs = @time @sync let
	s_info("Processing ", length(programs_cats), " entries")
	d = OrderedDict{String, Vector{NTuple{4, Int32OrFlt}}}(get_data_of(programs_cats))
	@spawn foreach(u_sort!, d.vals)
	sort!(d, by = s -> parse(Int64, s))
end

@info "Dumping dictionaries to file"
write("dictionaries.txt", json([programs, fieldIDs, catalogIDs]), "\n")

