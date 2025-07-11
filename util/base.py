from builtins import isinstance as isa # pyright: ignore[reportUnusedImport]
from typing import TypeVar

T = TypeVar("T")

def identity(x: T) -> T: # todo
	return x

# def identity[T](x: T) -> T: # require v3.12+
# 	return x

