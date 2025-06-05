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

@testset "misc" begin
	with_temp_env() do
		err = @catch include("../update.jl")
		@test isnothing(err)
		err = @catch include("../update_dictionaries.jl")
		@test isa(@show(err), LoadError)
		err = err.error
		@test isa(@show(err), SystemError) && err.errnum ≡ Libc.ENOENT

		hdr = @invokelatest Header()
		@test length(hdr.frmt) ≡ 3
		@test length(hdr.proj) ≡ 40
		@test VersionNumber(hdr.frmt...) ≡ v"1.0"
	end
end

