from .base import identity, isa


def testset_base() -> None:
	assert identity(1) == 1
	assert isa(1, int)

