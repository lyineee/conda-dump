class Tree(list):
    def __init__(self, value, children=[]) -> None:
        self._val = value
        return super().__init__(children)

    @property
    def val(self):
        return self._val

    def append(self, *items):
        for item in items:
            if not isinstance(item, type(self)):
                raise TypeError(f'Require type {type(self)} but get type {type(item)}')
            super().append(item)

    def search(self, item):
        for i in self:
            if i.val == item:
                return i
        return False

    def __iter__(self):
        return self.iter()

    def iter(self):
        for i in super().__iter__():
            yield from i.__iter__()
        yield self

    def __str__(self) -> str:
        re = f'{self._val}:['
        for i in super().__iter__():
            re += str(i)
        re += ']'
        return re


if __name__ == "__main__":
    a = Tree(1)
    a.append(Tree(3))
    a.append(Tree(4))
    b = Tree(2)
    b.append(Tree(5))
    a.append(b)
    print(a.search(2))
