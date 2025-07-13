from .base import Path, identity, isa, isfile, parse_json, write


def testset_base() -> None:
	assert identity(1) == 1
	assert isa(1, int)
	assert isfile("util/__init__.py")
	assert isfile(Path("util/__init__.py"))
	assert parse_json("data/bhm.meta.json")["frmt"] >= [1, 0, 0]
	assert parse_json(b"{}") == {}
	assert write("temp/.gitignore", b"\n*\n") == 3
	assert write("temp/.gitignore", f"\n*\n") == 3

