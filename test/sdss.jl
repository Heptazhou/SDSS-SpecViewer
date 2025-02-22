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

@testset "sdss" begin
#! format: noindent

using SpecViewer: branch2version, sas_redux_spec

full(field, mjd, obj, branch) = sas_redux_spec(field, mjd, obj, branch, "full")
lite(field, mjd, obj, branch) = sas_redux_spec(field, mjd, obj, branch, "lite")
spec(field, mjd, obj, branch) = sas_redux_spec(field, mjd, obj, branch)

@testset "bra2ver" begin
	@test branch2version("v0_00_0") ≡ v"0"
	@test branch2version("v5_13_2") ≡ v"5.13.2"
end

@testset "dr09" begin
	b = v"5.4.45"
	plate, mjd, fiber, fits = 3586, 55181, 0001, "spec-3586-55181-0001.fits"
	@test full(plate, mjd, fiber, b) ≡ "https://data.sdss.org/sas/dr9/sdss/spectro/redux/v5_4_45/spectra/full/3586/" * fits
	@test lite(plate, mjd, fiber, b) ≡ "https://data.sdss.org/sas/dr9/sdss/spectro/redux/v5_4_45/spectra/lite/3586/" * fits
	@test spec(plate, mjd, fiber, b) ≡ "https://data.sdss.org/sas/dr9/sdss/spectro/redux/v5_4_45/spectra/3586/" * fits
end

@testset "dr10" begin
	b = v"5.5.12"
	plate, mjd, fiber, fits = 3586, 55181, 0001, "spec-3586-55181-0001.fits"
	@test full(plate, mjd, fiber, b) ≡ "https://data.sdss.org/sas/dr10/sdss/spectro/redux/v5_5_12/spectra/full/3586/" * fits
	@test lite(plate, mjd, fiber, b) ≡ "https://data.sdss.org/sas/dr10/sdss/spectro/redux/v5_5_12/spectra/lite/3586/" * fits
	@test spec(plate, mjd, fiber, b) ≡ "https://data.sdss.org/sas/dr10/sdss/spectro/redux/v5_5_12/spectra/3586/" * fits
end

@testset "dr11" begin
	b = v"5.6.5"
	plate, mjd, fiber, fits = 3586, 55181, 0001, "spec-3586-55181-0001.fits"
	@test full(plate, mjd, fiber, b) ≡ "https://data.sdss.org/sas/dr11/sdss/spectro/redux/v5_6_5/spectra/full/3586/" * fits
	@test lite(plate, mjd, fiber, b) ≡ "https://data.sdss.org/sas/dr11/sdss/spectro/redux/v5_6_5/spectra/lite/3586/" * fits
	@test spec(plate, mjd, fiber, b) ≡ "https://data.sdss.org/sas/dr11/sdss/spectro/redux/v5_6_5/spectra/3586/" * fits
end

@testset "dr12" begin
	b = v"5.7.0"
	plate, mjd, fiber, fits = 3586, 55181, 0001, "spec-3586-55181-0001.fits"
	@test full(plate, mjd, fiber, b) ≡ "https://data.sdss.org/sas/dr12/sdss/spectro/redux/v5_7_0/spectra/full/3586/" * fits
	@test lite(plate, mjd, fiber, b) ≡ "https://data.sdss.org/sas/dr12/sdss/spectro/redux/v5_7_0/spectra/lite/3586/" * fits
	@test spec(plate, mjd, fiber, b) ≡ "https://data.sdss.org/sas/dr12/sdss/spectro/redux/v5_7_0/spectra/3586/" * fits

	b = v"5.7.2"
	plate, mjd, fiber, fits = 7339, 56768, 0001, "spec-7339-56768-0001.fits"
	@test full(plate, mjd, fiber, b) ≡ "https://data.sdss.org/sas/dr12/sdss/spectro/redux/v5_7_2/spectra/full/7339/" * fits
	@test lite(plate, mjd, fiber, b) ≡ "https://data.sdss.org/sas/dr12/sdss/spectro/redux/v5_7_2/spectra/lite/7339/" * fits
	@test spec(plate, mjd, fiber, b) ≡ "https://data.sdss.org/sas/dr12/sdss/spectro/redux/v5_7_2/spectra/7339/" * fits
end

@testset "dr13" begin
	b = v"5.9.0"
	plate, mjd, fiber, fits = 3586, 55181, 0001, "spec-3586-55181-0001.fits"
	@test full(plate, mjd, fiber, b) ≡ "https://data.sdss.org/sas/dr13/sdss/spectro/redux/v5_9_0/spectra/full/3586/" * fits
	@test lite(plate, mjd, fiber, b) ≡ "https://data.sdss.org/sas/dr13/sdss/spectro/redux/v5_9_0/spectra/lite/3586/" * fits
	@test spec(plate, mjd, fiber, b) ≡ "https://data.sdss.org/sas/dr13/sdss/spectro/redux/v5_9_0/spectra/3586/" * fits
end

@testset "dr14" begin
	b = v"5.10.0"
	plate, mjd, fiber, fits = 3586, 55181, 0001, "spec-3586-55181-0001.fits"
	@test full(plate, mjd, fiber, b) ≠ "https://data.sdss.org/sas/dr14/sdss/spectro/redux/v5_10_0/spectra/full/3586/" * fits
	@test lite(plate, mjd, fiber, b) ≠ "https://data.sdss.org/sas/dr14/sdss/spectro/redux/v5_10_0/spectra/lite/3586/" * fits
	@test spec(plate, mjd, fiber, b) ≠ "https://data.sdss.org/sas/dr14/sdss/spectro/redux/v5_10_0/spectra/3586/" * fits
	plate, mjd, fiber, fits = 10000, 57346, "0001", "spec-10000-57346-0001.fits"
	@test spec(plate, mjd, fiber, b) ≠ "https://data.sdss.org/sas/dr14/sdss/spectro/redux/v5_10_0/spectra/10000/" * fits
end

@testset "dr15" begin
	b = v"5.10.0"
	plate, mjd, fiber, fits = 3586, 55181, 0001, "spec-3586-55181-0001.fits"
	@test full(plate, mjd, fiber, b) ≡ "https://data.sdss.org/sas/dr15/sdss/spectro/redux/v5_10_0/spectra/full/3586/" * fits
	@test lite(plate, mjd, fiber, b) ≡ "https://data.sdss.org/sas/dr15/sdss/spectro/redux/v5_10_0/spectra/lite/3586/" * fits
	@test spec(plate, mjd, fiber, b) ≡ "https://data.sdss.org/sas/dr15/sdss/spectro/redux/v5_10_0/spectra/3586/" * fits
	plate, mjd, fiber, fits = 10000, 57346, "0001", "spec-10000-57346-0001.fits"
	@test spec(plate, mjd, fiber, b) ≡ "https://data.sdss.org/sas/dr15/sdss/spectro/redux/v5_10_0/spectra/10000/" * fits
end

@testset "dr16" begin
	b = v"5.13.0"
	plate, mjd, fiber, fits = 3586, 55181, 0001, "spec-3586-55181-0001.fits"
	@test full(plate, mjd, fiber, b) ≡ "https://data.sdss.org/sas/dr16/sdss/spectro/redux/v5_13_0/spectra/full/3586/" * fits
	@test lite(plate, mjd, fiber, b) ≡ "https://data.sdss.org/sas/dr16/sdss/spectro/redux/v5_13_0/spectra/lite/3586/" * fits
	@test spec(plate, mjd, fiber, b) ≡ full(plate, mjd, fiber, b)
end

@testset "dr17" begin
	b = v"5.13.2"
	plate, mjd, fiber, fits = 3586, 55181, 0001, "spec-3586-55181-0001.fits"
	@test full(plate, mjd, fiber, b) ≠ "https://data.sdss.org/sas/dr17/sdss/spectro/redux/v5_13_2/spectra/full/3586/" * fits
	@test lite(plate, mjd, fiber, b) ≠ "https://data.sdss.org/sas/dr17/sdss/spectro/redux/v5_13_2/spectra/lite/3586/" * fits
	@test spec(plate, mjd, fiber, b) ≡ full(plate, mjd, fiber, b)
end

@testset "dr18" begin
	b = v"5.13.2"
	plate, mjd, fiber, fits = 3586, 55181, 0001, "spec-3586-55181-0001.fits"
	@test full(plate, mjd, fiber, b) ≡ "https://data.sdss.org/sas/dr18/spectro/sdss/redux/v5_13_2/spectra/full/3586/" * fits
	@test lite(plate, mjd, fiber, b) ≡ "https://data.sdss.org/sas/dr18/spectro/sdss/redux/v5_13_2/spectra/lite/3586/" * fits
	@test spec(plate, mjd, fiber, b) ≡ full(plate, mjd, fiber, b)

	b = v"6.0.4"
	field, mjd, catid, fits = 15143, 59205, 04544940698, "spec-15143-59205-04544940698.fits"
	@test full(field, mjd, catid, b) ≡ "https://data.sdss.org/sas/dr18/spectro/sdss/redux/v6_0_4/spectra/full/15143p/59205/" * fits
	@test lite(field, mjd, catid, b) ≡ "https://data.sdss.org/sas/dr18/spectro/sdss/redux/v6_0_4/spectra/lite/15143p/59205/" * fits
	@test spec(field, mjd, catid, b) ≡ full(field, mjd, catid, b)
end

@testset "work" begin
	b = v"6.0.9"
	field, mjd, catid, fits = 015000, 59146, 4375786564, "spec-015000-59146-4375786564.fits"
	@test full(field, mjd, catid, b) ≡ "https://data.sdss5.org/sas/sdsswork/bhm/boss/spectro/redux/v6_0_9/spectra/full/015000/59146/" * fits
	@test lite(field, mjd, catid, b) ≡ "https://data.sdss5.org/sas/sdsswork/bhm/boss/spectro/redux/v6_0_9/spectra/lite/015000/59146/" * fits
	@test spec(field, mjd, catid, b) ≡ full(field, mjd, catid, b)

	b = v"6.1.1"
	field, mjd, catid, fits = 015000, 59146, 4375786564, "spec-015000-59146-4375786564.fits"
	@test full(field, mjd, catid, b) ≡ "https://data.sdss5.org/sas/sdsswork/bhm/boss/spectro/redux/v6_1_1/spectra/full/015000/59146/" * fits
	@test lite(field, mjd, catid, b) ≡ "https://data.sdss5.org/sas/sdsswork/bhm/boss/spectro/redux/v6_1_1/spectra/lite/015000/59146/" * fits
	@test spec(field, mjd, catid, b) ≡ full(field, mjd, catid, b)
	field, mjd, catid, fits = :allepoch, 60000, 27021598054114233, "spec-allepoch-60000-27021598054114233.fits"
	@test full(field, mjd, catid, b) ≡ "https://data.sdss5.org/sas/sdsswork/bhm/boss/spectro/redux/v6_1_1/spectra/full/allepoch/60000/" * fits
	@test lite(field, mjd, catid, b) ≡ "https://data.sdss5.org/sas/sdsswork/bhm/boss/spectro/redux/v6_1_1/spectra/lite/allepoch/60000/" * fits
	@test spec(field, mjd, catid, b) ≡ full(field, mjd, catid, b)

	b = v"6.1.3"
	field, mjd, catid, fits = 015000, 59146, 4375786564, "spec-015000-59146-4375786564.fits"
	@test full(field, mjd, catid, b) ≡ "https://data.sdss5.org/sas/sdsswork/bhm/boss/spectro/redux/v6_1_3/spectra/full/015000/59146/" * fits
	@test lite(field, mjd, catid, b) ≡ "https://data.sdss5.org/sas/sdsswork/bhm/boss/spectro/redux/v6_1_3/spectra/lite/015000/59146/" * fits
	@test spec(field, mjd, catid, b) ≡ full(field, mjd, catid, b)
	field, mjd, catid, fits = :allepoch, 60000, 27021598054114233, "spec-allepoch-60000-27021598054114233.fits"
	@test full(field, mjd, catid, b) ≡ "https://data.sdss5.org/sas/sdsswork/bhm/boss/spectro/redux/v6_1_3/spectra/full/allepoch/60000/" * fits
	@test lite(field, mjd, catid, b) ≡ "https://data.sdss5.org/sas/sdsswork/bhm/boss/spectro/redux/v6_1_3/spectra/lite/allepoch/60000/" * fits
	@test spec(field, mjd, catid, b) ≡ full(field, mjd, catid, b)
	field, mjd, catid, fits = :allepoch_lco, 60000, 27021598048679601, "spec-allepoch_lco-60000-27021598048679601.fits"
	@test full(field, mjd, catid, b) ≡ "https://data.sdss5.org/sas/sdsswork/bhm/boss/spectro/redux/v6_1_3/spectra/full/allepoch_lco/60000/" * fits
	@test lite(field, mjd, catid, b) ≡ "https://data.sdss5.org/sas/sdsswork/bhm/boss/spectro/redux/v6_1_3/spectra/lite/allepoch_lco/60000/" * fits
	@test spec(field, mjd, catid, b) ≡ full(field, mjd, catid, b)

	b = v"6.2.0"
	field, mjd, catid, fits = 015000, 59146, 4375786564, "spec-015000-59146-4375786564.fits"
	@test full(field, mjd, catid, b) ≡ "https://data.sdss5.org/sas/sdsswork/bhm/boss/spectro/redux/v6_2_0/spectra/daily/full/015XXX/015000/59146/" * fits
	@test lite(field, mjd, catid, b) ≡ "https://data.sdss5.org/sas/sdsswork/bhm/boss/spectro/redux/v6_2_0/spectra/daily/lite/015XXX/015000/59146/" * fits
	@test spec(field, mjd, catid, b) ≡ full(field, mjd, catid, b)
	field, mjd, catid, fits = :allepoch_apo, 60000, 27021602603659704, "spec-allepoch_apo-60000-27021602603659704.fits"
	@test full(field, mjd, catid, b) ≡ "https://data.sdss5.org/sas/sdsswork/bhm/boss/spectro/redux/v6_2_0/spectra/allepoch/full/allepoch/allepoch_apo/60000/" * fits
	@test lite(field, mjd, catid, b) ≡ "https://data.sdss5.org/sas/sdsswork/bhm/boss/spectro/redux/v6_2_0/spectra/allepoch/lite/allepoch/allepoch_apo/60000/" * fits
	@test spec(field, mjd, catid, b) ≡ full(field, mjd, catid, b)
	field, mjd, catid, fits = :allepoch_lco, 60000, 63050395106956948, "spec-allepoch_lco-60000-63050395106956948.fits"
	@test full(field, mjd, catid, b) ≡ "https://data.sdss5.org/sas/sdsswork/bhm/boss/spectro/redux/v6_2_0/spectra/allepoch/full/allepoch/allepoch_lco/60000/" * fits
	@test lite(field, mjd, catid, b) ≡ "https://data.sdss5.org/sas/sdsswork/bhm/boss/spectro/redux/v6_2_0/spectra/allepoch/lite/allepoch/allepoch_lco/60000/" * fits
	@test spec(field, mjd, catid, b) ≡ full(field, mjd, catid, b)

	b = :master
	field, mjd, catid, fits = 016199, 60606, 27021597863477824, "spec-016199-60606-27021597863477824.fits"
	@test full(field, mjd, catid, b) ≡ "https://data.sdss5.org/sas/sdsswork/bhm/boss/spectro/redux/master/spectra/daily/full/016XXX/016199/60606/" * fits
	@test lite(field, mjd, catid, b) ≡ "https://data.sdss5.org/sas/sdsswork/bhm/boss/spectro/redux/master/spectra/daily/lite/016XXX/016199/60606/" * fits
	@test spec(field, mjd, catid, b) ≡ full(field, mjd, catid, b)
end

end

