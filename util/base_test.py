from io import BytesIO as IOBuffer
from pathlib import Path

from .base import identity, isa, isfile, json_parse, json_parsefile, write


def testset_base() -> None:
	assert identity(1) == 1
	assert isa(1, int)
	assert isfile("temp/.gitignore")
	assert isfile(Path("temp/.gitignore"))
	assert json_parse(b"{}") == json_parse("{}") == {}
	assert json_parsefile("data/bhm.meta.json")["frmt"] >= [1, 0, 0]
	assert write("temp/.gitignore", b"\n*\n") == 3
	assert write("temp/.gitignore", f"\n*\n") == 3

