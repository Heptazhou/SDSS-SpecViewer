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
using Dates: DateTime, Second, UTC, now, unix2datetime
using Exts
using FITSIO: FITS, colnames, read_header
using JSON5: JSON5, json
using Mmap: mmap
using Pkg: PlatformEngines
using Serialization: deserialize, serialize
using Zstd_jll: Zstd_jll

const arg_keep = ARGS ∋ "-k" || isinteractive()
const dropfirst(v) = @view v[2:end]
const exe_7zip::String = @try PlatformEngines.find7z() PlatformEngines.exe7z().exec[1]
const exe_zstd::String = Zstd_jll.zstdmt().exec[1]
const hdu2_nrow(fn) = FITS(f -> read_header(get(f, "SPALL", 2))["NAXIS2"], fn)
const projecthash() = @try Context().env.manifest.other["project_hash"] ""
const s_info(xs...) = @info string(xs...)
const u_sort! = unique! ∘ sort!
const u_sorted(x) = issorted(x) & allunique(x)
const zstdcat = `$exe_zstd -dcf`;
const zstdin = `$exe_zstd -q -`;
const zstdmt = `$exe_zstd -1 --long --zstd=strat=7,tlen=4096`;

@kwdef struct File
	name::String
	nrow::Int64
	size::Int64
	time::DateTime
end
File(path) = File((basename, hdu2_nrow, filesize, unix2datetime ∘ mtime)(path)...)

@kwdef struct Header
	date::DateTime             = trunc(now(UTC), Second)
	dims::VTuple{Int64}        = ()
	frmt::VTuple{Int64}        = (1, 0, 0)
	nrow::ODict{Symbol, Int64} = LDict()
	proj::String               = projecthash()
	size::Int64                = -1
	source::Vector{File}       = []
end
Header(dims, nrow, size, source) = Header(; dims, nrow, size, source)

Base.:(==)(a::Header, b::Header) = all((i -> @eval $a.$i == $b.$i), setdiff(fieldnames(Header), [:date]))
Base.cat(x::Integer, y::Integer, ::Val{5}) = flipsign((10^5)abs(x) + mod(y, 10^5), x)
Base.isless(::Any, ::Union{Number, VersionNumber}) = (@nospecialize; Bool(0))
Base.isless(::Union{Number, VersionNumber}, ::Any) = (@nospecialize; Bool(1))

function deser_json(::Type{T}, f::String) where T
	deser_json(T, JSON5.parse(readstr(f), dicttype = ODict{Symbol, Any}))
end
function deser_json(::Type{File}, d::ODict)
	d[:time] = DateTime(d[:time]::String)
	File(; d...)
end
function deser_json(::Type{Header}, d::ODict)
	d[:date]   = (d[:date]::String) |> DateTime
	d[:dims]   = (d[:dims]::Vector...,)
	d[:frmt]   = (d[:frmt]::Vector...,)
	d[:source] = (d[:source]::Vector) .|> Fix1(deser_json, File)
	Header(; d...)
end

function zstd_des(f::String)
	deserialize(IOBuffer(read(`$zstdcat $f`)))
end
function zstd_ser(f::String, x)
	io = IOBuffer()
	serialize(io, x)
	seekstart(io)
	run(`$zstdin -o $f -f`, io)
	close(io)
end

@info "Looking for spAll files or archives (t = $(nthreads()), v$VERSION)"

# https://data.sdss.org/datamodel/files/BOSS_SPECTRO_REDUX/RUN2D/spAll.html
# https://github.com/sdss/idlspec2d/blob/master/datamodel/spall_dm.par
# https://www.sdss.org/dr18/data_access/bitmasks/
const cols = ODict{Symbol, DataType}(
	:CATALOGID   => Int64,   # SDSS-V CatalogID
	:FIELD       => Int64,   # Field number
	:MJD         => Int64,   # Modified Julian date of combined Spectra
	:OBJTYPE     => String,  # Why this object was targetted; QSO=SCIENCE; see spZbest
	:PROGRAMNAME => String,  # Program name within a given survey
	:SDSS_ID     => Int64,   # Unified SDSS-V Target Identifier; UInt32 / -999
	:SURVEY      => String,  # Survey that field is part of
	# :FIELDQUALITY => String,  # Characterization of field quality ("good" | "bad"); was :PLATEQUALITY
	# :RCHI2        => Float32, # Reduced χ² for best fit
	# :SPECOBJID    => Int128,  # Unique ID from SDSSID, Field, MJD, Coadd, RUN2D; Int64 / String since v6.2
	# :SPECPRIMARY  => UInt8,   # Best version of spectrum at this location; Bool / -999; see platemerge.pro
	# :Z            => Float32, # Redshift; assume incorrect if :ZWARNING is nonzero
	# :ZWARNING     => Int64,   # A flag for bad z fits in place of CLASS=UNKNOWN; see bitmasks
)
const fits = let
	extracts(arc::String) = run(`$exe_7zip x $arc`, devnull)
	filename(arc::String) = readlines(`$exe_7zip l -ba -slt $arc`)[1][8:end]
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
	isempty(d) && systemerror("*spAll*.(fits|[7gx]z)", Libc.ENOENT) # 2 No such file or directory
	u_sort!(d.vals, by = s -> (m = match(r"\bv\d+[._]\d+[._]\d+\b", s)) |> isnothing ?
							  "master" : VersionNumber(replace(m.match, "_" => ".")))
end
# FITS(fits[end])["SPALL"]

const df = @time let dir = rstrip(stdpath(@__DIR__, "temp"), '/')
	function _read(fn::String)
		f = File(fn)
		r = @try if f == deser_json(File, "$dir/$(f.name).json")
			@info "Loading `$fn` from cache (try)"
			r = zstd_des("$dir/$(f.name).dat.zst")
			@select! r $(cols.keys)
		end
		if isnothing(r)
			n = FITS(f -> get(f, "SPALL", 2).ext, fn)
			s_info("Reading `$fn[$n]` for ", length(cols), " columns")
			v = @time open(fn) do io
				FITS(mmap(io)) do f
					nx_cols = setdiff(cols.keys, Symbol.(colnames(f[n])))
					@assert isempty(nx_cols) "column(s) not exist: $nx_cols"
					map(col -> ensure_vector(read(f[n], String(col))), cols.keys)
				end
			end
			r = DataFrame(v, cols.keys, copycols = false)
			unique!(@subset! r :CATALOGID .> 0)
			zstd_ser("$dir/$(f.name).dat.zst", r)
			write("$dir/$(f.name).json", json(f, 4))
		end
		# write("$dir/$(f.name).tsv", r)
		r
	end
	df = mapreduce(_read, vcat, fits)
	replace!(df.SDSS_ID, -999 => 0)
	@assert all(!signbit, df.SDSS_ID)
	unique!(df)
	# write("$dir/df.tsv", df)
	df
end
# LDict(propertynames(df), eltype.(eachcol(df))) |> ODict

@info "Setting up dictionary for fieldIDs with each RM_field"

const dict_prg = ODict{String, OSet{cols[:FIELD]}}(
	"SDSS-RM"   => [15171, 15172, 15173, 15290, 16169, 20867, 112359],
	"XMMLSS-RM" => [15000, 15002, 23175, 112361],
	"COSMOS-RM" => [15038, 15070, 15071, 15252, 15253, 16163, 16164, 16165, 20868, 23288, 112360],
)

@info "Sorting out the fields (including the `all` option if instructed to do so)"

const programs_cats = @time let
	f_programs_dict = ODict{String, Expr}(
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
	foreach(sort!, dict_prg.vals)
	x = :(any([$(f_programs_dict.vals...)]))
	all_cats = @spawn @eval OSet(sort!(@rsubset(df, $x).CATALOGID))
	for (p, x) ∈ f_programs_dict
		dict_prg[p] = @eval OSet(sort!(@rsubset(df, $x).FIELD))
	end
	dict_prg |> sort!
	all_cats |> fetch
end

@info "Filling fieldIDs and catalogIDs with only science targets and completed epochs"

const dict_fld = @time let cat_t = cols[:CATALOGID]
	data_of(ids::OSet{cols[:FIELD]}) = @chain df begin
		@select :CATALOGID :FIELD :SURVEY :OBJTYPE
		@rsubset! :FIELD ∈ ids && :SURVEY ≡ "BHM" && :OBJTYPE ∈ ("QSO", "science")
		@by :FIELD :CATALOGID = [:CATALOGID]
	end
	d, init = ODict{String, Vector{cat_t}}(), cat_t[]
	s_info("Processing ", sum(length, dict_prg.vals), " entries of ", length(dict_prg), " programs")
	for (prog, opts) ∈ dict_prg
		data = data_of(opts) |> eachrow
		for (k, v) ∈ data
			(k, v) = string(k), copy(v)
			(haskey(d, k) ? append!(d[k], v) : d[k] = v) |> u_sort!
		end
		d["$prog-all"] = mapreduce(last, vcat, data; init) |> u_sort!
	end
	sort!(d, by = s -> @something tryparse(cat_t, s) s)
end
# @assert all(u_sorted, dict_fld.vals)

@info "Building dictionary for CATALOGID"

const dict_cat = @time let
	dict_of(ids::OSet{cols[:CATALOGID]}) = @chain df begin
		@rselect :CATALOGID :FIELD_MJD = cat(:FIELD, :MJD, Val(5)) :SDSS_ID
		@rsubset! :CATALOGID ∈ ids
		@rorderby :CATALOGID unsigned(:SDSS_ID - 1)
		@distinct! :CATALOGID :FIELD_MJD # ensure SDSS_ID is unique; error in v6.1.1
		innerjoin(on = :CATALOGID,
			(@chain _ begin
				@by :CATALOGID :SDSS_ID = get(:SDSS_ID, 1, 0) # least positive value
			end),
			(@chain _ begin
				@rorderby :CATALOGID :FIELD_MJD
				@by :CATALOGID :FIELD_MJD = [:FIELD_MJD]
			end),
		)
		LDict(_.CATALOGID, vcat.(_.SDSS_ID, _.FIELD_MJD)) |> ODict
	end
	s_info("Processing ", length(programs_cats), " entries")
	dict_of(programs_cats)
end
# @assert u_sorted(dict_cat.keys) & all(u_sorted ∘ dropfirst, dict_cat.vals)
# @show extrema(length, dict_cat.vals) # (2, 94)

@info "Building dictionary for SDSS_ID"

const dict_sid = @time let
	dict_of(ids::OSet{cols[:CATALOGID]}) = @chain df begin
		@rselect :CATALOGID :SDSS_ID
		@rsubset! :SDSS_ID > 0 :CATALOGID ∈ ids
		@rorderby :SDSS_ID :CATALOGID
		@distinct! :CATALOGID # ensure SDSS_ID is unique; error in v6.1.1
		@by :SDSS_ID :CATALOGID = [:CATALOGID]
		LDict(_.SDSS_ID, _.CATALOGID) |> ODict
	end
	s_info("Processing ", length(programs_cats), " entries")
	dict_of(programs_cats)
end
# @assert u_sorted(dict_sid.keys) & all(u_sorted, dict_sid.vals)
# @show extrema(length, dict_sid.vals) # (1, 3)

@info "Dumping dictionaries to file"

@time let dir = rstrip(stdpath(@__DIR__, "data"), '/')
	data = [
		:prg => dict_prg,
		:fld => dict_fld,
		:sid => dict_sid,
		:cat => dict_cat,
	]
	meta = let old = deser_json(Header, "$dir/bhm.meta.json")
		row = ODict(k => length(v) for (k, v) ∈ data)
		len = length(json(ODict(data), ~0))
		new = Header(size(df), row, len, File.(fits))
		new == old ? old : new
	end
	cd(dir) do
		# foreach((k, v)::Pair -> write("bhm-$k.json", json(v, ~0)), data)
		write("bhm.meta.json", json(meta, 4))
		write("bhm.json", json(ODict([:hdr => meta; data]), ~0))
		run(`$zstdmt bhm.json -o bhm.json.zst -f`, devnull)
		arg_keep || rm("bhm.json")
	end
end

