# from typing import Self
from typing import TypeVar, List

TTree = TypeVar("TTree", bound="Tree")


class Tree(list):
    def __init__(self, value, children=[]) -> None:
        self._val = value
        return super().__init__(children)

    @property
    def val(self):
        return self._val

    def append(self, *items: List[TTree]):
        for item in items:
            if not isinstance(item, type(self)):
                raise TypeError(f"Require type {type(self)} but get type {type(item)}")
            super().append(item)

    def search(self, item):
        for i in self:
            if i.val == item:
                return i
        return False

    def delete(self, tree: TTree):
        for index, node in enumerate(super().__iter__()):
            if node.name == tree.name:
                del self[index]
            else:
                node.delete(tree)

    def print_struct(self, first=True, indent=""):
        if first:
            print(indent + "|__" + f"{self._val}")
        else:
            print(indent + "__" + f"{self._val}")
        for index, node in enumerate(super().__iter__()):
            if index + 1 == len(self):
                node.print_struct(first=True, indent=indent + "      ")
                continue
            node.print_struct(first=False, indent=indent + "      |")

    def __getattr__(self, name):
        if name in self._val.__dict__:
            return self._val.__dict__[name]
        raise NameError(f"no attribute {name} in {type(self._val)}")

    def __iter__(self):
        return self.iter()

    def iter(self):
        for i in super().__iter__():
            yield from i.__iter__()
        yield self

    def __str__(self) -> str:
        re = f"{self._val}:["
        for i in super().__iter__():
            re += str(i)
        re += "]"
        return re


if __name__ == "__main__":
    a = Tree(1)
    a.append(Tree(3))
    a.append(Tree(4))
    b = Tree(2)
    b.append(Tree(5))
    a.append(b)
    print(a.search(2))
