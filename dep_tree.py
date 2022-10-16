from dataclasses import dataclass, field
from typing import List, Union
from packaging import version

from tree import Tree


@dataclass
class DependData:
    name: str

    def __str__(self) -> str:
        return self.name

    def __eq__(self, __o: object) -> bool:
        if not isinstance(__o, type(self)):
            raise TypeError(f"can not perform eq on {type(__o)} and {type(self)}")
        if self.name == __o.name:
            return True
        else:
            return False


@dataclass
class DependInfo(DependData):
    version: version.Version
    file_list: List[str] = field(default=[])


@dataclass
class DependReq(DependData):
    gt: Union[None, version.Version] = field(default=None)
    lt: Union[None, version.Version] = field(default=None)
    ne: Union[None, version.Version] = field(default=None)

    def meet(self, info: DependInfo):
        if self.gt and info.version < self.gt:
            return False
        if self.lt and info.version > self.lt:
            return False
        if self.ne and info.version == self.ne:
            return False
        return True


class DependTree(Tree):
    def __init__(self, data: DependData) -> None:
        super().__init__(data)

    def search(self, item: str):
        return super().search(DependData(name=item))


if __name__ == "__main__":
    d1 = DependInfo(name="dep1", version=version.Version("0.0.1"), file_list=["a", "b"])
    d2 = DependInfo(name="dep2", version=version.Version("0.0.1"), file_list=["c", "d"])
    a = DependTree(d1)
    b = DependTree(d2)
    a.append(b)
    print(a.search("dep2"))
