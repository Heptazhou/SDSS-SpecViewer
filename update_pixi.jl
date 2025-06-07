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

using Exts

@time if abspath(PROGRAM_FILE) == @__FILE__
	run(`pixi update`, devnull)
	f = "pixi.lock"
	s = readstr(f)
	s = replace(s, r"^( +)(?:\w+): \[\]\n"m => "")
	s = replace(s, r"^( +)(?:\w+):\K(\n\1- )([^: ]+): (.+)$(?!\n\1 |\2)"m => s" [{ \3: \4 }]")
	s = replace(s, r"^( +)(?:\w+):\K(\n\1- )([^\n]+)\2(.+)\2(.+)\2(.+)$(?!\2)"m => s" [\"\3\", \"\4\", \"\5\", \"\6\"]")
	s = replace(s, r"^( +)(?:\w+):\K(\n\1- )([^\n]+)\2(.+)\2(.+)$(?!\2)"m => s" [\"\3\", \"\4\", \"\5\"]")
	s = replace(s, r"^( +)(?:\w+):\K(\n\1- )([^\n]+)\2(.+)$(?!\2)"m => s" [\"\3\", \"\4\"]")
	s = replace(s, r"^( +)(?:\w+):\K(\n\1- )([^\n]+)$(?!\2)"m => s" [\"\3\"]")
	s = replace(s, r"^( +)license(_family)?: .+\n"m => "")
	write(f, s)
	run(`pixi ls -x`, devnull)
end

