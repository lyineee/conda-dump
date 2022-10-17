from dataclasses import dataclass, field
from typing import List, Optional
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
class DependReq(DependData):
    gt: Optional[version.Version] = field(default=None)
    lt: Optional[version.Version] = field(default=None)
    ne: Optional[version.Version] = field(default=None)
    eq: Optional[version.Version] = field(default=None)

    def meet_version(self, info):
        if self.gt and info < self.gt:
            return False
        if self.lt and info > self.lt:
            return False
        if self.ne and info == self.ne:
            return False
        if self.eq and info != self.eq:
            return False
        return True


@dataclass
class DependInfo(DependData):
    version: version.Version
    link: Optional[str] = None
    files: List[str] = field(default_factory=list)
    depends: List[DependReq] = field(default_factory=list)

    def __str__(self):
        return f"name: {self.name}, version: {self.version}"


class DependTree(Tree):
    def __init__(self, data: DependData) -> None:
        super().__init__(data)

    def search(self, item: str):
        return super().search(DependData(name=item))


if __name__ == "__main__":
    d1 = DependInfo(name="dep1", version=version.Version("0.0.1"), files=["a", "b"])
    d2 = DependInfo(name="dep2", version=version.Version("0.0.1"), files=["c", "d"])
    a = DependTree(d1)
    b = DependTree(d2)
    a.append(b)
    print(a.search("dep2"))
