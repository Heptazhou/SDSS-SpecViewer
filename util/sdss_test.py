from .sdss import sdss_iau
from .sdss import sdss_sas_fits as func


def testset_dr09() -> None:
	b = "v5_4_45"
	plate, mjd, fiber, fits = 3586, 55181, 1, "spec-3586-55181-0001.fits"
	assert func(plate, mjd, fiber, b) == "https://data.sdss.org/sas/dr9/sdss/spectro/redux/v5_4_45/spectra/lite/3586/" + fits

def testset_dr10() -> None:
	b = "v5_5_12"
	plate, mjd, fiber, fits = 3586, 55181, 1, "spec-3586-55181-0001.fits"
	assert func(plate, mjd, fiber, b) == "https://data.sdss.org/sas/dr10/sdss/spectro/redux/v5_5_12/spectra/lite/3586/" + fits

def testset_dr11() -> None:
	b = "v5_6_5"
	plate, mjd, fiber, fits = 3586, 55181, 1, "spec-3586-55181-0001.fits"
	assert func(plate, mjd, fiber, b) == "https://data.sdss.org/sas/dr11/sdss/spectro/redux/v5_6_5/spectra/lite/3586/" + fits

def testset_dr12_v5_7_0() -> None:
	b = "v5_7_0"
	plate, mjd, fiber, fits = 3586, 55181, 1, "spec-3586-55181-0001.fits"
	assert func(plate, mjd, fiber, b) == "https://data.sdss.org/sas/dr12/sdss/spectro/redux/v5_7_0/spectra/lite/3586/" + fits
def testset_dr12_v5_7_2() -> None:
	b = "v5_7_2"
	plate, mjd, fiber, fits = 7339, 56768, 1, "spec-7339-56768-0001.fits"
	assert func(plate, mjd, fiber, b) == "https://data.sdss.org/sas/dr12/sdss/spectro/redux/v5_7_2/spectra/lite/7339/" + fits

def testset_dr13() -> None:
	b = "v5_9_0"
	plate, mjd, fiber, fits = 3586, 55181, 1, "spec-3586-55181-0001.fits"
	assert func(plate, mjd, fiber, b) == "https://data.sdss.org/sas/dr13/sdss/spectro/redux/v5_9_0/spectra/lite/3586/" + fits

def testset_dr15() -> None:
	b = "v5_10_0"
	plate, mjd, fiber, fits = 3586, 55181, 1, "spec-3586-55181-0001.fits"
	assert func(plate, mjd, fiber, b) == "https://data.sdss.org/sas/dr15/sdss/spectro/redux/v5_10_0/spectra/lite/3586/" + fits
	plate, mjd, fiber, fits = 10000, 57346, 1, "spec-10000-57346-0001.fits"
	assert func(plate, mjd, fiber, b) == "https://data.sdss.org/sas/dr15/sdss/spectro/redux/v5_10_0/spectra/lite/10000/" + fits

def testset_dr16() -> None:
	b = "v5_13_0"
	plate, mjd, fiber, fits = 3586, 55181, 1, "spec-3586-55181-0001.fits"
	assert func(plate, mjd, fiber, b) == "https://data.sdss.org/sas/dr16/sdss/spectro/redux/v5_13_0/spectra/lite/3586/" + fits

def testset_dr18() -> None:
	b = "v5_13_2"
	plate, mjd, fiber, fits = 3586, 55181, 1, "spec-3586-55181-0001.fits"
	assert func(plate, mjd, fiber, b) == "https://data.sdss.org/sas/dr18/spectro/sdss/redux/v5_13_2/spectra/lite/3586/" + fits
def testset_dr18_026() -> None:
	b = "26"
	plate, mjd, fiber, fits = 266, 51602, 1, "spec-0266-51602-0001.fits"
	assert func(plate, mjd, fiber, b) == "https://data.sdss.org/sas/dr18/spectro/sdss/redux/26/spectra/lite/0266/" + fits
def testset_dr18_103() -> None:
	b = "103"
	plate, mjd, fiber, fits = 1960, 53289, 1, "spec-1960-53289-0001.fits"
	assert func(plate, mjd, fiber, b) == "https://data.sdss.org/sas/dr18/spectro/sdss/redux/103/spectra/lite/1960/" + fits
def testset_dr18_104() -> None:
	b = "104"
	plate, mjd, fiber, fits = 2640, 54806, 1, "spec-2640-54806-0001.fits"
	assert func(plate, mjd, fiber, b) == "https://data.sdss.org/sas/dr18/spectro/sdss/redux/104/spectra/lite/2640/" + fits
def testset_dr18_v6_0_4() -> None:
	b = "v6_0_4"
	field, mjd, catid, fits = 15143, 59205, 4544940698, "spec-15143-59205-04544940698.fits"
	assert func(field, mjd, catid, b) == "https://data.sdss.org/sas/dr18/spectro/sdss/redux/v6_0_4/spectra/lite/15143p/59205/" + fits

def testset_work_v6_0_9() -> None:
	b = "v6_0_9"
	field, mjd, catid, fits = 15000, 59146, 4375786564, "spec-015000-59146-4375786564.fits"
	assert func(field, mjd, catid, b) == "https://data.sdss5.org/sas/sdsswork/bhm/boss/spectro/redux/v6_0_9/spectra/lite/015000/59146/" + fits
def testset_work_v6_1_1() -> None:
	b = "v6_1_1"
	field, mjd, catid, fits = 15000, 59146, 4375786564, "spec-015000-59146-4375786564.fits"
	assert func(field, mjd, catid, b) == "https://data.sdss5.org/sas/sdsswork/bhm/boss/spectro/redux/v6_1_1/spectra/lite/015000/59146/" + fits
def testset_work_v6_1_1_all_ep() -> None:
	b = "v6_1_1"
	field, mjd, catid, fits = "allepoch", 60000, 27021598054114233, "spec-allepoch-60000-27021598054114233.fits"
	assert func(field, mjd, catid, b) == "https://data.sdss5.org/sas/sdsswork/bhm/boss/spectro/redux/v6_1_1/spectra/lite/allepoch/60000/" + fits
def testset_work_v6_1_3() -> None:
	b = "v6_1_3"
	field, mjd, catid, fits = 15000, 59146, 4375786564, "spec-015000-59146-4375786564.fits"
	assert func(field, mjd, catid, b) == "https://data.sdss5.org/sas/sdsswork/bhm/boss/spectro/redux/v6_1_3/spectra/lite/015000/59146/" + fits
def testset_work_v6_1_3_all_ep() -> None:
	b = "v6_1_3"
	field, mjd, catid, fits = "allepoch", 60000, 27021598054114233, "spec-allepoch-60000-27021598054114233.fits"
	assert func(field, mjd, catid, b) == "https://data.sdss5.org/sas/sdsswork/bhm/boss/spectro/redux/v6_1_3/spectra/lite/allepoch/60000/" + fits
	field, mjd, catid, fits = "allepoch_lco", 60000, 27021598048679601, "spec-allepoch_lco-60000-27021598048679601.fits"
	assert func(field, mjd, catid, b) == "https://data.sdss5.org/sas/sdsswork/bhm/boss/spectro/redux/v6_1_3/spectra/lite/allepoch_lco/60000/" + fits
def testset_work_v6_2_0() -> None:
	b = "v6_2_0"
	field, mjd, catid, fits = 15000, 59146, 4375786564, "spec-015000-59146-4375786564.fits"
	assert func(field, mjd, catid, b) == "https://data.sdss5.org/sas/sdsswork/bhm/boss/spectro/redux/v6_2_0/spectra/daily/lite/015XXX/015000/59146/" + fits
def testset_work_v6_2_0_all_ep() -> None:
	b = "v6_2_0"
	field, mjd, catid, fits = "allepoch_apo", 60000, 27021602603659704, "spec-allepoch_apo-60000-27021602603659704.fits"
	assert func(field, mjd, catid, b) == "https://data.sdss5.org/sas/sdsswork/bhm/boss/spectro/redux/v6_2_0/spectra/allepoch/lite/allepoch/allepoch_apo/60000/" + fits
	field, mjd, catid, fits = "allepoch_lco", 60000, 63050395106956948, "spec-allepoch_lco-60000-63050395106956948.fits"
	assert func(field, mjd, catid, b) == "https://data.sdss5.org/sas/sdsswork/bhm/boss/spectro/redux/v6_2_0/spectra/allepoch/lite/allepoch/allepoch_lco/60000/" + fits
def testset_work_master() -> None:
	b = "master"
	field, mjd, catid, fits = 15000, 59146, 4375786564, "spec-015000-59146-4375786564.fits"
	assert func(field, mjd, catid, b) == "https://data.sdss5.org/sas/sdsswork/bhm/boss/spectro/redux/master/spectra/daily/lite/015XXX/015000/59146/" + fits
	assert func(field, mjd, catid, b) == func(f"{field}p", mjd, catid, b)

def testset_iau_name_00() -> None:
	assert sdss_iau(000.000_000, -0.000) == "SDSS J000000.00-000000.0"
	assert sdss_iau(000.000_000, +0.000) == "SDSS J000000.00+000000.0"

def testset_iau_name_01() -> None:
	assert sdss_iau(001.999_999, -0.100) == "SDSS J000759.99-000600.0"
	assert sdss_iau(001.999_999, +0.100) == "SDSS J000759.99+000600.0"

def testset_iau_name_02() -> None:
	assert sdss_iau(188.737_042, -1.396) == "SDSS J123456.89-012345.6"
	assert sdss_iau(188.737_042, +1.396) == "SDSS J123456.89+012345.6"

